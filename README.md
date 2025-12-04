# SimuFed — A Lightweight Federated Data Processing Framework

SimuFed is a minimal simulation framework for **federated data processing**.  
It models how distributed clients compute local statistics (mean, variance, histogram) and send aggregated summaries to a central coordinator, with **simulated latency, delays, and client dropouts**.

SimuFed supports both:

- **Synchronous aggregation** (round-based federated round)
- **Asynchronous aggregation** (streaming updates)

This makes it ideal for learning and demonstrating practical distributed-systems concepts at small scale.

---

## Features

- **Local client statistics**: mean, variance, histogram  
- **Synchronous vs Asynchronous** aggregation modes  
- **Fault simulation**:
  - random network delay  
  - random client dropout  
- **Synthetic dataset generator**
- **Experiment pipeline + plotting scripts**
- Designed to be small, readable, and fully reproducible

---

## Project Structure

```
SimuFed/
│── client.py # Local client logic
│── coordinator.py # Synchronous coordinator
│── coordinator_async.py # Asynchronous coordinator
│── fault_simulator.py # Delay + dropout simulation
│── utils/
│ └── aggregator.py # Summary merging utilities
│
scripts/
│ └── make_partitions.py # Dataset generator
│
datasets/ # CSV partitions (created after running generator)
run_sync_demo.py # Sync demonstration
run_async_demo.py # Async demonstration
run_all_experiments.py # Full experiment sweep
plots/
│ └── plot_results.py # Script to generate graphs
requirements.txt
README.md
```

---

## 1. Installation

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

---

## 2. Generate Synthetic Datasets

Before running any demo, generate dataset partitions:

    python scripts/make_partitions.py --outdir datasets --clients 5 --rows 1000

⚠️ **Important:**  
Your dataset count **must match** the number of clients used in the demos.

Example:

If you run:

    python run_sync_demo.py --clients 3 ...

You must regenerate:

    python scripts/make_partitions.py --outdir datasets --clients 3 --rows 1000

Otherwise you will see:

    FileNotFoundError: Missing dataset file: datasets/partition_4.csv (generate with scripts/make_partitions.py)

---

## 3. Synchronous Federated Demo

The synchronous coordinator:

- waits for all clients or timeout  
- aggregates summaries **after** collecting all results  
- simulates classic “round-based” federated learning  

Run:

    python run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.2 --max-delay 3

**Example Output**

    [Client 2] Sent summary (n=1000).
    [Client 4] Dropped update.
    [Client 1] Sent summary (n=1000).

    === Federated Round Complete ===
    Received: 4 / Dropped: 1
    Duration: 5.07s
    Global n=4000, mean=0.1234, std=2.93
    STATS,mode=sync,clients_expected=5,received=4,dropped=1,...

The `STATS,...` line at the end is machine-readable and is used by the experiment script.

---

## 4. Asynchronous Federated Demo

The asynchronous coordinator:

- launches all clients  
- merges each client’s summary into the global aggregate **as soon as it arrives**  
- prints a running view of global mean/variance  
- stops when:
  - all clients respond, OR
  - global timeout reached, OR
  - a short **grace period** has passed since the last update  

Run:

    python run_async_demo.py \
      --clients 5 \
      --timeout 5 \
      --drop-prob 0.3 \
      --max-delay 3 \
      --grace 1

**Example Output**

    [Async] Starting round with 5 clients, timeout=5.0s, grace=1.0s
    [Client 3] Sent summary (n=1000).
    [Async] Update 1/5 → global mean=2.5900, var=3.1300
    [Client 1] Sent summary (n=1000).
    [Async] Update 2/5 → global mean=0.4100, var=5.7700
    [Async] All clients responded.

    === Async Round Complete ===
    Received: 5 / Dropped: 0
    Duration: 2.59s
    Final global n=5000, mean=-0.0994, var=24.9677
    STATS,mode=async,clients_expected=5,received=5,dropped=0,...

Here again, the final `STATS,...` line is used for automated experiments.

---

## 5. Running Full Experiments (Used for Plots)

We provide an automated experiment script to reproduce all graphs in the report.

### Step 1 — Generate datasets

    python scripts/make_partitions.py --outdir datasets --clients 5 --rows 1000

### Step 2 — Run sync + async sweeps

This will run several configurations (different drop probabilities, sync vs async) and produce a `results.csv` file in the project root.

    python run_all_experiments.py

Example of generated CSV:

    mode,drop_prob,clients_expected,received,dropped,duration,global_n,global_mean,global_var
    sync,0.0,5,5,0,2.7134,5000,-0.0994,24.9677
    sync,0.5,5,1,4,5.0173,1000,2.4938,0.6362
    sync,0.8,5,0,5,5.0581,0,nan,nan
    async,0.0,5,5,0,2.5894,5000,-0.0994,24.9677
    async,0.5,5,1,4,2.5975,1000,2.4938,0.6362
    async,0.8,5,1,4,1.3610,1000,-2.7210,0.7464

Each row is one run with a particular drop probability and mode.

---

## 6. Plotting the Results

To regenerate the figures used in the report:

    python plots/plot_results.py

This will read `results.csv` and generate:

- `runtime_vs_drop.png` — **Round duration vs drop probability** for sync vs async.  
- `success_vs_drop.png` — **Fraction of clients received** vs drop probability.  
- `accuracy_vs_drop.png` — **Error in global mean** vs drop probability.  

You can embed these PNGs directly into your final report or slides.

---

## 7. Results Overview (What the Plots Show)

### 7.1 Runtime vs Drop Probability

- **Synchronous** runtime grows toward the timeout as more clients drop or are delayed.  
- **Asynchronous** runtime stays lower:
  - when all clients respond, it finishes close to the “natural” completion time;  
  - when many drop out, it stops quickly once the grace period elapses.

File: `runtime_vs_drop.png`

---

### 7.2 Client Success Rate vs Drop Probability

- Both modes see fewer successful clients as `drop_prob` increases.  
- At high drop probabilities, the synchronous coordinator can receive **zero** updates (all dropped or late), producing `NaN` global statistics.  
- The asynchronous coordinator often still obtains at least one update because it is not blocked on a hard barrier.

File: `success_vs_drop.png`

---

### 7.3 Accuracy Degradation Under Dropout

We compare the global mean from SimuFed to the “true” centralized mean (approximately 0 for the synthetic setup).

- With **no dropout**, both sync and async exactly match the centralized baseline (up to floating-point noise).  
- With **moderate dropout**, global mean deviates but remains reasonable if at least one client per mode responds.  
- With **extreme dropout**, synchronous may get zero summaries and cannot compute a valid mean/variance, while asynchronous still returns a (biased but defined) estimate from the surviving clients.

File: `accuracy_vs_drop.png`

---

## 8. Notes and Tuning Knobs

- `--drop-prob`  
  Per-client probability of being dropped in a round.

- `--max-delay`  
  Maximum simulated network delay per client (seconds). Actual delay is drawn uniformly from `[0, max_delay]`.

- `--timeout`  
  Coordinator’s overall patience for a given round (seconds). In sync mode this behaves like a classic barrier timeout.

- `--grace` (async only)  
  Extra time to keep listening **after** the last update arrives. Useful to model “soft” waiting for stragglers without blocking for the full timeout.

---

## 9. Milestone Scope (What This Repository Demonstrates)

- Fully functional **synchronous coordinator–client pipeline**  
- Fully functional **asynchronous aggregation** with live updates  
- **Fault simulation** (delay + dropout) using `FaultConfig`  
- **Verified aggregation correctness** via distributed vs centralized comparison  
- **Experiment workflow**:
  - log machine-readable `STATS` lines  
  - collect into `results.csv`  
  - generate plots via `plots/plot_results.py`  
- Clear, modular Python code suitable for extension

---

## 10. Reproducibility Checklist

1. Clone repository  
2. Create and activate virtual environment  
3. `pip install -r requirements.txt`  
4. Generate datasets:

       python scripts/make_partitions.py --outdir datasets --clients 5 --rows 1000

5. Run demos:

       python run_sync_demo.py --clients 5 --timeout 5 --drop-prob 0.2 --max-delay 3
       python run_async_demo.py --clients 5 --timeout 5 --drop-prob 0.3 --max-delay 3 --grace 1

6. Run full experiments:

       python run_all_experiments.py

7. Generate plots:

       python plots/plot_results.py

If you follow these steps, you should reproduce the same behavior and graphs shown in the report.

---

## 11. License / Course Context

This project was developed as part of **COMPSCI 532 — Systems for Data Science** and is intended for educational and demonstration purposes.
