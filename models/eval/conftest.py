"""Pytest setup: make the ``eval`` package importable as ``import eval``.

The smoke test (``test_eval.py``) lives *inside* the package, so we add the package's
parent (``models/``) to ``sys.path``. The server packages are wired separately by
``eval._paths`` when the harness is imported.
"""

from __future__ import annotations

import sys
from pathlib import Path

_MODELS_DIR = Path(__file__).resolve().parents[1]  # models/
if str(_MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(_MODELS_DIR))
