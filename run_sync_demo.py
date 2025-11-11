from __future__ import annotations
import argparse
from pathlib import Path

from SimuFed.coordinator import Coordinator
from SimuFed.client import ClientConfig
from SimuFed.fault_simulator import FaultConfig

def main():
    parser = argparse.ArgumentParser(
        description="Run a synchronous federated aggregation demo using SimuFed."
    )
    parser.add_argument("--dataset-dir", type=Path, default=Path("datasets"))
    parser.add_argument("--clients", type=int, default=3)
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--drop-prob", type=float, default=0.0)
    parser.add_argument("--max-delay", type=float, default=0.0)
    args = parser.parse_args()

    # verify dataset files exist
    files = [args.dataset_dir / f"partition_{i+1}.csv" for i in range(args.clients)]
    for f in files:
        if not f.exists():
            raise FileNotFoundError(
                f"Missing dataset file: {f} (generate with scripts/make_partitions.py)"
            )

    # create client configurations
    clients = []
    for i, f in enumerate(files, start=1):
        clients.append(
            ClientConfig(
                client_id=i,
                csv_path=str(f),
                column="value",
                bins=args.bins,
                hist_range=None,
                faults=FaultConfig(drop_prob=args.drop_prob, max_delay_s=args.max_delay),
            )
        )

    # run one synchronous round
    coord = Coordinator(timeout_s=args.timeout)
    result = coord.run_round(clients)

    # print summary
    print("\n=== Federated Round Complete ===")
    print(f"Received: {len(result.summaries)} / Dropped: {result.dropped}")
    print(f"Duration: {result.duration_s:.3f}s")
    print(
        f"Global n={result.aggregated['n']}, "
        f"mean={result.aggregated['mean']:.4f}, "
        f"std={result.aggregated['var']**0.5:.4f}"
    )

if __name__ == "__main__":
    main()


'''
Uses your ClientConfig and FaultConfig to spin up N clients.

Each client reads its CSV and either sends or drops an update.

The Coordinator waits for responses (up to --timeout) and aggregates results.

The printed summary makes it easy to demonstrate functionality during your presentation.
'''