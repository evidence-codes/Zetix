"""Catalog ingestion adapters (EPIC-1, tasks 1.A.2–1.A.4).

Each adapter normalises an external catalog source into ``list[Product]`` so the
:class:`zetix_api.services.catalog.CatalogService` can index it uniformly. The
adapters are pure parsers/fetchers — they do not touch the running app and are
wired later behind an ingestion endpoint/CLI.
"""

from __future__ import annotations

from .csv_adapter import parse_csv
from .json_adapter import parse_json
from .shopify_adapter import fetch_shopify

__all__ = ["fetch_shopify", "parse_csv", "parse_json"]
