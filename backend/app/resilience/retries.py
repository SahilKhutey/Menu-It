"""
ModularMenu — Bounded Exponential Backoff with Jitter (ARC-12 §20.4, ADR-0251).
Calculates safe, bounded backoff delays preventing thundering herd spikes.
"""

import random


def calculate_retry_delay(
    attempt: int,
    base_seconds: float = 2.0,
    max_seconds: float = 60.0,
    jitter_factor: float = 0.2,
) -> float:
    """Calculate bounded exponential delay with randomized jitter."""
    if attempt <= 0:
        return 0.0

    exponential = min(max_seconds, base_seconds * (2 ** max(0, attempt - 1)))

    if jitter_factor > 0:
        low = 1.0 - jitter_factor
        high = 1.0 + jitter_factor
        jitter = random.uniform(low, high)
        return min(max_seconds, exponential * jitter)

    return exponential
