from __future__ import annotations
from dataclasses import dataclass
from multiprocessing import Process, Queue
from typing import List
import time

from SimuFed.client import ClientConfig, worker
from SimuFed.utils.aggregator import Summary, merge_summaries

@dataclass
class RoundResult:
    """Holds results from a single federated aggregation round."""
    summaries: List[Summary]
    aggregated: dict
    dropped: int
    duration_s: float

class Coordinator:
    """Central orchestrator managing clients and aggregation."""
    def __init__(self, timeout_s: float = 5.0):
        self.timeout_s = timeout_s

    def run_round(self, clients: List[ClientConfig]) -> RoundResult:
        """Runs one synchronous round of federated aggregation."""
        q: Queue = Queue()
        procs: List[Process] = []

        start_time = time.time()

        # Step 1: Launch all client processes
        for cfg in clients:
            p = Process(target=worker, args=(cfg, q), daemon=True)
            p.start()
            procs.append(p)

        # Step 2: Collect results with timeout
        received: List[Summary] = []
        expected = len(clients)
        remaining = expected
        deadline = start_time + self.timeout_s

        while time.time() < deadline and remaining > 0:
            try:
                s = q.get(timeout=0.1)
                received.append(s)
                remaining -= 1
            except Exception:
                pass  # no message yet — keep polling

        # Step 3: Ensure all processes end gracefully
        for p in procs:
            p.join(timeout=0.1)

        # Step 4: Aggregate results
        dropped = expected - len(received)
        aggregated = merge_summaries(received)
        duration = time.time() - start_time

        # Step 5: Return results
        return RoundResult(
            summaries=received,
            aggregated=aggregated,
            dropped=dropped,
            duration_s=duration
        )

'''
Coordinator.run_round():

    Starts each client as a process.

    Waits on a queue until all clients respond or timeout occurs.

    Calls merge_summaries() to combine all client results.

    Returns a structured RoundResult with everything you need (summaries, global stats, dropped count, duration).

'''