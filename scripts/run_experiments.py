#!/usr/bin/env python3
from __future__ import annotations

import csv
import shlex
import subprocess
from pathlib import Path


# Each command string contains the drop probability as: --drop-prob X
COMMANDS = [
    "run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.0 --max-delay 3",
    "run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.5 --max-delay 3",
    "run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.8 --max-delay 3",
    "run_async_demo.py --clients 5 --timeout 5 --drop-prob 0.0 --max-delay 3 --grace 1",
    "run_async_demo.py --clients 5 --timeout 5 --drop-prob 0.5 --max-delay 3 --grace 1",
    "run_async_demo.py --clients 5 --timeout 5 --drop-prob 0.8 --max-delay 3 --grace 1",
]

PYTHON = "python"  # or ".venv/bin/python3" if you prefer absolute


def parse_drop_prob(cmd: str) -> float:
    parts = shlex.split(cmd)
    if "--drop-prob" in parts:
        idx = parts.index("--drop-prob")
        return float(parts[idx + 1])
    return 0.0


def run_and_collect(cmd: str) -> dict | None:
    print(f"Running: {PYTHON} {cmd}")
    proc = subprocess.Popen(
        [PYTHON] + shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()

    stats_line = None
    for line in stdout.splitlines():
        if line.startswith("STATS,"):
            stats_line = line.strip()
            break

    if stats_line is None:
        print("  !! No STATS line found, skipping")
        if stderr.strip():
            print("  stderr:\n", stderr)
        return None

    # stats_line example:
    # STATS,mode=sync,clients_expected=5,received=3,...
    tokens = stats_line.split(",")[1:]  # skip "STATS"
    data = {}
    for tok in tokens:
        k, v = tok.split("=", 1)
        data[k] = v

    # Convert numeric fields
    for key in ("clients_expected", "received", "dropped", "global_n"):
        data[key] = int(data[key])
    for key in ("duration", "global_mean", "global_var"):
        try:
            data[key] = float(data[key])
        except ValueError:
            data[key] = float("nan")

    # Add drop_prob from the command string
    data["drop_prob"] = parse_drop_prob(cmd)

    return data


def main() -> None:
    rows: list[dict] = []

    for cmd in COMMANDS:
        res = run_and_collect(cmd)
        if res is not None:
            rows.append(res)

    if not rows:
        print("No results collected.")
        return

    # Define column order (note: drop_prob included!)
    fieldnames = [
        "mode",
        "drop_prob",
        "clients_expected",
        "received",
        "dropped",
        "duration",
        "global_n",
        "global_mean",
        "global_var",
    ]

    out_path = Path("results.csv")
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Saved {out_path} with {len(rows)} rows")


if __name__ == "__main__":
    main()
