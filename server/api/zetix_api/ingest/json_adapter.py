"""JSON ingestion adapter (EPIC-1, task 1.A.3).

Accepts a JSON catalog as a raw string/bytes payload, an already-parsed ``list`` of
product dicts, or an object of the form ``{"products": [...]}``. Each product dict
is validated against :class:`Product`.
"""

from __future__ import annotations

import json
from typing import Any

from ..schemas import Product


def _extract_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("products", [])
    else:
        raise TypeError(f"unsupported JSON catalog type: {type(data).__name__}")

    if not isinstance(items, list):
        raise TypeError("'products' must be a list of product objects")
    return items


def parse_json(data: str | bytes | dict | list) -> list[Product]:
    """Parse a JSON catalog into a list of products.

    ``data`` may be a JSON string/bytes payload, a list of product dicts, or a
    mapping containing a ``products`` list.
    """
    if isinstance(data, str | bytes):
        data = json.loads(data)

    items = _extract_items(data)
    return [Product.model_validate(item) for item in items]
