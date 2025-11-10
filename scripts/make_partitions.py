from __future__ import annotations
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic CSV partitions for SimuFed clients."
    )
    parser.add_argument("--outdir", type=Path, default=Path("datasets"))
    parser.add_argument("--clients", type=int, default=3)
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)

    # Generate a single dataset with n elements
    n = args.clients * args.rows
    x = rng.normal(loc=0, scale=args.clients, size=n)
    x = np.sort(x)
    df = pd.DataFrame({"value": x})

    # Pathologically partition the dataset into consecutive chunks
    # Each client gets a chunk with slightly different statistics
    # We will show that aggregate of the clients approximates the global stats: mean=0, std=args.clients
    for i in range(args.clients):
        start_idx = i * args.rows
        end_idx = start_idx + args.rows
        partition = df.iloc[start_idx:end_idx].sample(frac=1, random_state=args.seed).reset_index(drop=True)
        partition.to_csv(args.outdir / f"partition_{i+1}.csv", index=False)
        client_mean = partition["value"].mean()
        client_std = partition["value"].std()
        print(f"Generated partition_{i+1}.csv (rows={len(partition)}) (mean={client_mean:.2f}, std={client_std:.2f})")

    print(f">>> Created {args.clients} CSV partitions in {args.outdir}/")
    print(f">>> Federated Average should approximate global stats: mean=0, std={args.clients:.2f}")

if __name__ == "__main__":
    main()

'''
Generates one CSV per client.

Each CSV has a column "value" with numeric data.

Slight variations in mean/variance ensure global aggregation isn’t trivial.

Reproducible across runs because of --seed.
'''