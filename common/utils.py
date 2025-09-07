"""Common utilities for deterministic data generation and helpers."""
from __future__ import annotations

import random
import datetime as _dt
from typing import Iterable, Iterator, List, Sequence, Tuple

GLOBAL_SEED = 42


def get_rng(seed: int | None = None) -> random.Random:
    """Return a random generator seeded deterministically.

    Parameters
    ----------
    seed: int | None
        When provided, use this seed; otherwise use GLOBAL_SEED.
    """
    return random.Random(GLOBAL_SEED if seed is None else seed)


def batch(iterable: Sequence, size: int) -> Iterator[Sequence]:
    """Yield successive batches of ``size`` from ``iterable``."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def daterange(start: _dt.date, end: _dt.date, step: int = 1) -> Iterator[_dt.date]:
    """Yield dates from ``start`` to ``end`` inclusive stepping by ``step`` days."""
    cur = start
    delta = _dt.timedelta(days=step)
    while cur <= end:
        yield cur
        cur += delta


def next_business_day(date: _dt.date) -> _dt.date:
    """Return next business day (Mon-Fri)."""
    next_day = date + _dt.timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += _dt.timedelta(days=1)
    return next_day

