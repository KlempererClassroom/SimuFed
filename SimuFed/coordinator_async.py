# SimuFed/coordinator_async.py

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Process, Queue
from typing import List
import time

from SimuFed.client import ClientConfig, worker as client_worker
from SimuFed.utils.aggregator import merge_summaries


@dataclass
class AsyncRoundResult:
    """Result of one asynchronous aggregation round."""
    received: int
    dropped: int
    duration_s: float
    aggregated: dict


class AsyncCoordinator:
    """
    Asynchronous-style coordinator:
    - Starts all clients.
    - As each client finishes, it immediately merges that summary into a global aggregate.
    - Prints a running view of the global mean/variance.
    - Stops when:
        * all clients responded, OR
        * overall timeout is hit, OR
        * a short 'grace' period has elapsed since the last update.
    """

    def __init__(self, timeout_s: float, grace_after_last: float = 1.0) -> None:
        self.timeout_s = timeout_s
        self.grace_after_last = grace_after_last

    def _start_clients(self, clients: List[ClientConfig], out_q: Queue) -> List[Process]:
        procs: List[Process] = []
        for cfg in clients:
            p = Process(target=client_worker, args=(cfg, out_q), daemon=True)
            p.start()
            procs.append(p)
        return procs

    def run_round(self, clients: List[ClientConfig]) -> AsyncRoundResult:
        """
        Fire off all clients, then keep consuming summaries as they arrive.

        This is 'async' in the sense that we don't wait for a fixed barrier
        before aggregating — the aggregate is updated on every arrival.
        """
        expected = len(clients)
        queue: Queue = Queue()
        procs = self._start_clients(clients, queue)

        start = time.time()
        received = []
        last_recv_time: float | None = None

        print(f"[Async] Starting round with {expected} clients, "
              f"timeout={self.timeout_s}s, grace={self.grace_after_last}s")

        while True:
            now = time.time()
            # Hard overall timeout
            if now - start >= self.timeout_s:
                print("[Async] Overall timeout reached.")
                break

            # If we have at least one update, stop after 'grace_after_last' seconds
            # with no new updates.
            if last_recv_time is not None and (now - last_recv_time) >= self.grace_after_last:
                print("[Async] Grace period after last update elapsed.")
                break

            # Try to get one new summary, with a short polling timeout
            try:
                summary = queue.get(timeout=0.2)
            except Exception:
                # Nothing arrived in this 0.2s window; loop back to check timeouts.
                continue

            received.append(summary)
            last_recv_time = time.time()

            agg = merge_summaries(received)
            print(f"[Async] Update {len(received)}/{expected} → "
                  f"global mean={agg['mean']:.4f}, var={agg['var']:.4f}")

            # If everyone has checked in, we can stop early
            if len(received) == expected:
                print("[Async] All clients responded.")
                break

        duration = time.time() - start

        # Best-effort join; clients may have exited already
        for p in procs:
            p.join(timeout=0.1)

        dropped = expected - len(received)
        final_agg = merge_summaries(received) if received else {}

        print("\n=== Async Round Complete ===")
        print(f"Received: {len(received)} / Dropped: {dropped}")
        print(f"Duration: {duration:.3f}s")
        if final_agg:
            print(f"Final global n={final_agg['n']}, "
                  f"mean={final_agg['mean']:.4f}, var={final_agg['var']:.4f}")
        else:
            print("No summaries received; no aggregate computed.")

        return AsyncRoundResult(
            received=len(received),
            dropped=dropped,
            duration_s=duration,
            aggregated=final_agg,
        )
