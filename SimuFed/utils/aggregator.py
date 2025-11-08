from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import numpy as np


'''
Summary → stores a single client’s local stats.

make_hist() → quickly builds a histogram (using NumPy).

merge_summaries() → merges all summaries efficiently without raw data.
'''
@dataclass
class Summary:
    """Holds a client’s summarized statistics."""
    client_id: int
    n: int
    s: float          # sum(x)
    s2: float         # sum(x^2)
    hist_counts: List[int]
    hist_edges: List[float]

    @property
    def mean(self) -> float:
        return 0.0 if self.n == 0 else self.s / self.n

    @property
    def var(self) -> float:
        if self.n <= 1:
            return 0.0
        # stable variance calculation
        return max(self.s2 / self.n - (self.s / self.n) ** 2, 0.0)


def make_hist(x: np.ndarray, bins: int = 10, range_: Tuple[float, float] | None = None) -> Tuple[np.ndarray, np.ndarray]:
    """Build histogram counts and edges for a local client’s data."""
    counts, edges = np.histogram(x, bins=bins, range=range_)
    return counts.astype(int), edges


def merge_summaries(summaries: List[Summary]) -> Dict[str, float | List[int] | List[float]]:
    """Aggregate multiple client summaries into one global summary."""
    n_total = sum(s.n for s in summaries)
    s_total = sum(s.s for s in summaries)
    s2_total = sum(s.s2 for s in summaries)

    # Assume same bin edges for all clients
    edges = summaries[0].hist_edges if summaries else []
    counts = np.sum([np.array(s.hist_counts, dtype=int) for s in summaries], axis=0).tolist() if summaries else []

    mean = 0.0 if n_total == 0 else s_total / n_total
    var = 0.0 if n_total == 0 else max(s2_total / n_total - mean ** 2, 0.0)

    return {
        "n": n_total,
        "sum": s_total,
        "sumsq": s2_total,
        "mean": mean,
        "var": var,
        "hist_counts": counts,
        "hist_edges": edges,
    }



'''In a federated setup:

Each client computes local statistics:

1. n → count of rows

2. sum(x)

3. sum(x²)

4. histogram counts

The Coordinator receives these and merges them to get the global mean and variance efficiently without centralizing data.

This is the heart of SimuFed — it lets you reproduce global metrics just by combining numbers, not the raw data.
'''