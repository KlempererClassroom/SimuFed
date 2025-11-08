from __future__ import annotations
import random
import time
from dataclasses import dataclass

@dataclass
class FaultConfig:
    """Configuration for simulating client delays and dropouts."""
    drop_prob: float = 0.0       # probability to drop an update
    max_delay_s: float = 0.0     # maximum artificial delay in seconds

def maybe_delay_and_drop(cfg: FaultConfig) -> bool:
    """
    Simulates real-world client unreliability.

    Returns True if the client update should be dropped.
    May sleep for a random delay in [0, max_delay_s].
    """
    if cfg.max_delay_s > 0:
        time.sleep(random.uniform(0.0, cfg.max_delay_s))
    return random.random() < cfg.drop_prob

'''
Example 'FaultConfig(drop_prob=0.2, max_delay_s=3.0)' meaning:

20 % chance of dropping the message,

otherwise, may sleep for up to 3 seconds.
'''