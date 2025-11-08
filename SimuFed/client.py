from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import numpy as np
from multiprocessing import Queue
from SimuFed.utils.aggregator import Summary, make_hist
from SimuFed.fault_simulator import FaultConfig, maybe_delay_and_drop

@dataclass
class ClientConfig:
    """Configuration for a federated client process."""
    client_id: int
    csv_path: str
    column: str = "value"
    bins: int = 10
    hist_range: tuple[float, float] | None = None
    faults: FaultConfig = field(default_factory=FaultConfig)

def worker(cfg: ClientConfig, out_q: Queue):
    """
    Run by each simulated client process.
    Computes local statistics and sends them to the coordinator.
    """
    # Step 1: Load the local dataset
    df = pd.read_csv(cfg.csv_path)
    x = df[cfg.column].to_numpy(dtype=float)

    # Step 2: Compute local statistics
    n = int(x.size)
    s = float(np.sum(x))
    s2 = float(np.sum(x * x))
    counts, edges = make_hist(x, bins=cfg.bins, range_=cfg.hist_range)

    # Step 3: Possibly delay or drop
    should_drop = maybe_delay_and_drop(cfg.faults)
    if should_drop:
        # client drops out this round
        print(f"[Client {cfg.client_id}] Dropped update.")
        return

    # Step 4: Package and send results to Coordinator
    summary = Summary(
        client_id=cfg.client_id,
        n=n,
        s=s,
        s2=s2,
        hist_counts=counts.tolist(),
        hist_edges=edges.tolist(),
    )
    out_q.put(summary)
    print(f"[Client {cfg.client_id}] Sent summary (n={n}).")

'''
ClientConfig → defines all per-client settings (path to CSV, histogram bins, fault config).

worker() → function executed in a separate process:

    Reads CSV into a Pandas DataFrame.

    Converts the target column into a NumPy array for fast math.

    Computes stats (mean/var indirectly, via sums).

    Runs the fault simulation.

    Pushes a Summary object into a Queue.
'''