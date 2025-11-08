# SimuFed — A Lightweight Federated Data Processing Framework

SimuFed is a minimal simulation framework for **federated data processing**.  
It demonstrates how distributed clients can compute local statistics and send aggregated results to a central coordinator — with simulated network delays and client dropouts.

---

## 📘 Features

- **Synchronous federated aggregation** (round-based)
- **Client-level statistics**: mean, variance, and histogram
- **Fault simulation**: random delay and dropout
- **Synthetic data generation** for easy testing
- Fully modular design — Coordinator, Clients, and Utilities

---

## 🧱 Project Structure

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

## ⚙️ Run Instructions

### 1️⃣ Setup Virtual Environment and Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 2️⃣ Generate Synthetic Datasets
```bash
python scripts/make_partitions.py --outdir datasets --clients 3 --rows 1000
```

#### Example Output
```
Generated partition_1.csv (mean≈10.0, std≈2.0)
Generated partition_2.csv (mean≈10.5, std≈2.5)
Generated partition_3.csv (mean≈11.0, std≈2.0)
✅ Created 3 CSV partitions in datasets/
```

---

### 3️⃣ Run the Synchronous Federated Demo
```bash
python run_sync_demo.py --clients 3 --timeout 5 --drop-prob 0.2 --max-delay 3
```

#### Expected Output
```
=== Round Complete ===
Received: 3 / Dropped: 0
Duration: 1.84s
Global n=3000  Global mean=10.73  var=4.11
[Client 1] n=1000  mean=10.00  var=3.97
[Client 2] n=1000  mean=10.51  var=4.30
[Client 3] n=1000  mean=11.68  var=4.06
```

---

### 💡 Notes
- `--drop-prob` controls the fraction of clients that may drop out each round.
- `--max-delay` simulates random network latency (in seconds).
- Adjust `--timeout` to control how long the Coordinator waits for missing clients.

---

## 🧭 Milestone Scope

- Fully functional **synchronous coordinator–client** pipeline  
- Fault simulation (delay & dropout)  
- Verified aggregation correctness  
- Modular design for extension to asynchronous rounds  

---

## 🧪 Example Experiments

You can explore different failure rates and delays:

```bash
# compare runs with varying fault levels
for dp in 0.0 0.2 0.5; do
  echo "--- drop_prob=$dp ---"
  python run_sync_demo.py --clients 3 --timeout 3 --drop-prob $dp --max-delay 1
done
```
