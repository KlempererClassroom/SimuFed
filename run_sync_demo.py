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
    clients: list[ClientConfig] = []
    for i, f in enumerate(files, start=1):
        clients.append(
            ClientConfig(
                client_id=i,
                csv_path=str(f),
                column="value",
                bins=args.bins,
                hist_range=None,
                faults=FaultConfig(
                    drop_prob=args.drop_prob,
                    max_delay_s=args.max_delay,
                ),
            )
        )

    # run one synchronous round
    coord = Coordinator(timeout_s=args.timeout)
    result = coord.run_round(clients)

    received_count = len(result.summaries)
    dropped_count = result.dropped
    duration = result.duration_s

    if result.aggregated:
        global_n = result.aggregated["n"]
        global_mean = result.aggregated["mean"]
        global_var = result.aggregated["var"]
        global_std = global_var ** 0.5
    else:
        global_n = 0
        global_mean = float("nan")
        global_var = float("nan")
        global_std = float("nan")

     # human-readable summary
    print("\n=== Federated Round Complete ===")
    print(f"Received: {received_count} / Dropped: {dropped_count}")
    print(f"Duration: {duration:.3f}s")
    if global_n > 0:
        print(
            f"Global n={global_n}, "
            f"mean={global_mean:.4f}, "
            f"std={global_std:.4f}"
        )
    else:
        print("No summaries received; no aggregate computed.")

    # safe strings for STATS line
    gm_str = f"{global_mean:.4f}" if global_n > 0 else "nan"
    gv_str = f"{global_var:.4f}" if global_n > 0 else "nan"

    # Machine-readable stats line for experiments
    print(
        "STATS,"
        f"mode=sync,"
        f"clients_expected={args.clients},"
        f"received={received_count},"
        f"dropped={dropped_count},"
        f"duration={duration:.4f},"
        f"global_n={global_n},"
        f"global_mean={gm_str},"
        f"global_var={gv_str}"
    )


if __name__ == "__main__":
    main()
