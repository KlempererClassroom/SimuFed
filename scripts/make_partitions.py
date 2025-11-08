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

    for i in range(args.clients):
        # Give each client a slightly different distribution
        mu = 10 + i * 0.5
        sigma = 2 + (i % 2) * 0.5
        x = rng.normal(loc=mu, scale=sigma, size=args.rows)
        df = pd.DataFrame({"value": x})
        df.to_csv(args.outdir / f"partition_{i+1}.csv", index=False)
        print(f"Generated partition_{i+1}.csv (mean≈{mu}, std≈{sigma})")

    print(f"\n>>>  Created {args.clients} CSV partitions in {args.outdir}/")

if __name__ == "__main__":
    main()

'''
Generates one CSV per client.

Each CSV has a column "value" with numeric data.

Slight variations in mean/variance ensure global aggregation isn’t trivial.

Reproducible across runs because of --seed.
'''