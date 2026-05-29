"""CSV ingestion adapter (EPIC-1, task 1.A.2).

Maps a CSV with the canonical column headers onto :class:`Product`. Accepts either
a CSV string/bytes payload or a filesystem path. Uses only the standard library.
"""

from __future__ import annotations

import csv
import io
import os
from collections.abc import Iterable, Mapping

from ..schemas import Availability, Product

# Canonical columns mapped onto Product (header matching is case-insensitive and
# whitespace-tolerant): id, title, description, price, currency, availability,
# image_url, product_url, store, category.


def _looks_like_path(source: str) -> bool:
    # A path has no newline and points at an existing file. Anything with a
    # newline is treated as inline CSV content.
    return "\n" not in source and "\r" not in source and os.path.isfile(source)


def _read_text(source: str | bytes) -> str:
    if isinstance(source, bytes):
        return source.decode("utf-8-sig")
    if _looks_like_path(source):
        with open(source, encoding="utf-8-sig", newline="") as fh:
            return fh.read()
    return source


def _normalise_keys(row: Mapping[str, str | None]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in row.items():
        if key is None:
            continue
        out[key.strip().lower()] = (value or "").strip()
    return out


def _to_availability(value: str) -> Availability:
    if not value:
        return Availability.unknown
    try:
        return Availability(value.strip().lower())
    except ValueError:
        return Availability.unknown


def _row_to_product(row: Mapping[str, str]) -> Product:
    price_raw = row.get("price", "")
    return Product(
        id=row["id"],
        title=row.get("title", ""),
        description=row.get("description") or None,
        price=float(price_raw) if price_raw else 0.0,
        currency=row.get("currency", ""),
        availability=_to_availability(row.get("availability", "")),
        image_url=row.get("image_url") or None,
        product_url=row.get("product_url", ""),
        store=row.get("store", ""),
        category=row.get("category") or None,
    )


def parse_csv(source: str | bytes) -> list[Product]:
    """Parse a CSV source (string, bytes, or path) into a list of products.

    Recognised columns: ``id, title, description, price, currency, availability,
    image_url, product_url, store, category``. Unknown columns are ignored.
    """
    text = _read_text(source)
    reader: Iterable[Mapping[str, str | None]] = csv.DictReader(io.StringIO(text))
    products: list[Product] = []
    for raw in reader:
        row = _normalise_keys(raw)
        if not row.get("id"):
            # Skip blank/incomplete rows rather than emit an invalid product.
            continue
        products.append(_row_to_product(row))
    return products
