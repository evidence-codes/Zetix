"""Runtime configuration. Kept dependency-light (stdlib only) for the foundation."""

from __future__ import annotations

import os
from dataclasses import dataclass

API_VERSION = "0.1.0"


@dataclass(frozen=True)
class Settings:
    version: str = API_VERSION
    # Default top-k results returned by /search (PRD FR-06: top 10).
    default_top_k: int = 10

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            default_top_k=int(os.getenv("ZETIX_DEFAULT_TOP_K", "10")),
        )
