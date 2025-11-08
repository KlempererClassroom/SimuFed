# SimuFed — A Lightweight Federated Data Processing Framework

## Overview
SimuFed simulates federated data processing with a central **Coordinator** and multiple **Clients**.
Clients compute local statistics on their partitions and send summaries to the Coordinator for aggregation.

## Milestone Scope
- Synchronous round-based aggregation
- Local mean/variance/histogram on CSV partitions
- Fault simulation: random delay and drop
- Minimal logs + example output

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# make synthetic partitions
python scripts/make_partitions.py --outdir datasets --clients 3 --rows 1000

# run synchronous demo
python run_sync_demo.py --clients 3 --timeout 5 --drop-prob 0.2 --max-delay 3

simufed/
  __init__.py
  coordinator.py
  client.py
  fault_simulator.py
  utils/
    __init__.py
    aggregator.py
scripts/
  make_partitions.py
datasets/
  .gitkeep
tests/
  test_aggregator.py (optional)
