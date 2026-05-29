"""Zetix search-quality evaluation harness (EPIC-1 / TASKS 1.E.2–1.E.4).

Computes Top-1 / Top-3 / Top-5 accuracy plus a per-category breakdown by driving the
real FastAPI search pipeline in-process. See ``README.md`` for methodology and the M1
acceptance bar (Top-3 > 80%).
"""

from __future__ import annotations

from .dataset import Dataset, Query, load_dataset, synthetic_dataset
from .harness import M1_TOP3_BAR, TOP_KS, evaluate, format_report, run

__all__ = [
    "Dataset",
    "Query",
    "load_dataset",
    "synthetic_dataset",
    "evaluate",
    "format_report",
    "run",
    "M1_TOP3_BAR",
    "TOP_KS",
]
