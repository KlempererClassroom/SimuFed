# SimuFed — A Lightweight Federated Data Processing Framework

SimuFed is a minimal simulation framework for **federated data processing**.  
It demonstrates how distributed clients can compute local statistics and send aggregated results to a central coordinator — with simulated network delays and client dropouts.

---

## Features

- **Synchronous federated aggregation** (round-based)
- **Client-level statistics**: mean, variance, and histogram
- **Fault simulation**: random delay and dropout
- **Synthetic data generation** for easy testing
- Fully modular design — Coordinator, Clients, and Utilities

---

## Project Structure

```
SimuFed/
│
├── client.py             # Local client logic (compute & send summaries)
├── coordinator.py        # Central orchestrator
├── fault_simulator.py    # Delay and dropout simulation
├── utils/
│   └── aggregator.py     # Statistical merging utilities
│
scripts/
│   └── make_partitions.py  # Synthetic dataset generator
│
datasets/
│   └── .gitkeep
│
run_sync_demo.py          # Example round runner
requirements.txt
README.md
```

---

## Run Instructions

###Setup Virtual Environment and Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Generate Synthetic Datasets
```bash
python scripts/make_partitions.py --outdir datasets --clients 5 --rows 100
```

#### Example Output
It can be seen that each partition has wildly different local statistics. Federated computation rests on the assumption that local statistics approximate the global distribution when aggregated. We will demonstrate this in the next section.
```
Generated partition_1.csv (rows=100) (mean -6.78, std 2.02)
Generated partition_2.csv (rows=100) (mean -2.58, std 0.90)
Generated partition_3.csv (rows=100) (mean -0.01, std 0.76)
Generated partition_4.csv (rows=100) (mean 2.33, std 0.76)
Generated partition_5.csv (rows=100) (mean 6.71, std 2.44)
>>> Created 5 CSV partitions in datasets/
>>> Federated Average should approximate global stats: mean=0, std=5.00
```

---

### Run the Synchronous Federated Demo

Consider the case where no clients drop out and there is some network delay. This simulates a stable network with some latency. Our aggregated statistics should closely approximate the global statistics.
```bash
$> python run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.0 --max-delay 3
... (logs showing client delays) ...
=== Federated Round Complete ===
Received: 5 / Dropped: 0
Duration: 3.023s
Global n=500, mean=-0.0656, std=4.7949
```

Now consider a more unstable network where some clients drop out and there is variable delay. The aggregated statistics may deviate more from the global statistics due to missing data.
```bash
$> python run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.5 --max-delay 3
... (logs showing client delays) ...
=== Federated Round Complete ===
Received: 3 / Dropped: 2
Duration: 5.038s
Global n=300, mean=-2.3439, std=3.9562
```

If majority clients drop out, the aggregated statistics may be significantly off from the global statistics.
```bash
$> python run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.8 --max-delay 3
... (logs showing client delays) ...
=== Federated Round Complete ===
Received: 2 / Dropped: 3
Duration: 5.071s
Global n=200, mean=-0.1272, std=2.5905
```

---

### Notes
- `--drop-prob` controls the fraction of clients that may drop out each round.
- `--max-delay` simulates random network latency (in seconds).
- Adjust `--timeout` to control how long the Coordinator waits for missing clients.

---

## Milestone Scope

- Fully functional **synchronous coordinator–client** pipeline  
- Fault simulation (delay & dropout)  
- Verified aggregation correctness  
- Modular design for extension to asynchronous rounds  

---

## Example Experiments

You can explore different failure rates and delays:

```bash
# compare runs with varying fault levels
for dp in 0.0 0.2 0.5; do
  echo "--- drop_prob=$dp ---"
  python run_sync_demo.py --clients 3 --timeout 3 --drop-prob $dp --max-delay 1
done
```
