# run_async_demo.py

from __future__ import annotations

import argparse
from pathlib import Path
from multiprocessing import set_start_method

from SimuFed.client import ClientConfig
from SimuFed.coordinator_async import AsyncCoordinator
from SimuFed.fault_simulator import FaultConfig


def build_client_configs(
    num_clients: int,
    data_dir: str,
    faults: FaultConfig,
    bins: int = 10,
    hist_range: tuple[float, float] | None = None,
) -> list[ClientConfig]:
    configs: list[ClientConfig] = []
    base = Path(data_dir)
    for cid in range(1, num_clients + 1):
        csv_path = base / f"partition_{cid}.csv"
        cfg = ClientConfig(
            client_id=cid,
            csv_path=str(csv_path),
            column="value",
            bins=bins,
            hist_range=hist_range,
            faults=faults,
        )
        configs.append(cfg)
    return configs


def main() -> None:
    parser = argparse.ArgumentParser(description="SimuFed asynchronous demo")
    parser.add_argument("--clients", type=int, default=3, help="Number of clients")
    parser.add_argument("--data-dir", type=str, default="datasets", help="Directory with partition_*.csv files")
    parser.add_argument("--timeout", type=float, default=5.0, help="Overall timeout in seconds")
    parser.add_argument("--drop-prob", type=float, default=0.2, help="Per-client drop probability")
    parser.add_argument("--max-delay", type=float, default=3.0, help="Max simulated delay per client (seconds)")
    parser.add_argument("--grace", type=float, default=1.0,
                        help="Grace period after last update before closing the round") 
    args = parser.parse_args()

    faults = FaultConfig(
        drop_prob=args.drop_prob,
        max_delay_s=args.max_delay,
    )

    configs = build_client_configs(
        num_clients=args.clients,
        data_dir=args.data_dir,
        faults=faults,
        bins=10,
        hist_range=None,
    )

    coord = AsyncCoordinator(timeout_s=args.timeout, grace_after_last=args.grace)
    coord.run_round(configs)


if __name__ == "__main__":
    # For safety on macOS / some Linux setups
    try:
        set_start_method("spawn")
    except RuntimeError:
        # start method was already set
        pass

    main()
