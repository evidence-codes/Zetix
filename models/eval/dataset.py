"""Labelled evaluation datasets for the search-quality harness.

A dataset is a pair: a *catalog* of products (pushed to the index) and a *query set*
mapping each query to the product id it should retrieve.

Two sources are supported:

* :func:`synthetic_dataset` — a small, self-contained catalog across a few categories
  plus a labelled query set, so the harness runs with zero external data.
* :func:`load_dataset` — read a real dataset from JSON, so the same harness can target
  a real 10k catalog later (format documented in ``models/eval/README.md`` and below).

Real-dataset JSON format::

    {
      "store": "acme",
      "products": [ {<Product fields: id, title, price, currency,
                      product_url, store, image_url, category, ...>}, ... ],
      "queries":  [ {"query_id": "q1", "expected_id": "sku-1",
                     "image_url": "https://...", "category": "furniture"}, ... ]
    }

Each query identifies the image whose embedding is the search input. For the synthetic
set we reuse each product's own ``image_url`` as the query image, so the indexed vector
and the query vector are derived identically (see the harness for the methodology note).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Query:
    """One labelled query: which catalog item should this image retrieve?"""

    query_id: str
    expected_id: str
    # The image whose embedding is the query input. The stub embedder seeds from this
    # string (mirroring how the catalog indexes ``image_url or id``), so an exact match
    # is retrievable end-to-end. A real run swaps in OpenCLIP + real image bytes.
    image_url: str
    category: str | None = None


@dataclass(frozen=True)
class Dataset:
    """A labelled dataset: catalog products + the query set to evaluate against."""

    store: str
    products: list[dict]
    queries: list[Query] = field(default_factory=list)


# --- Synthetic catalog -------------------------------------------------------------

# A handful of products across a few categories. Kept small and deterministic so the
# harness runs instantly and the smoke test is stable.
_SYNTHETIC_PRODUCTS: list[dict] = [
    # furniture
    {"id": "fur-1", "title": "Mid-century credenza", "category": "furniture", "price": 899.0},
    {"id": "fur-2", "title": "Oak dining table", "category": "furniture", "price": 1299.0},
    {"id": "fur-3", "title": "Velvet accent chair", "category": "furniture", "price": 449.0},
    # footwear
    {"id": "shoe-1", "title": "Running shoe, teal", "category": "footwear", "price": 120.0},
    {"id": "shoe-2", "title": "Leather chelsea boot", "category": "footwear", "price": 210.0},
    {"id": "shoe-3", "title": "Canvas low-top", "category": "footwear", "price": 65.0},
    # lighting
    {"id": "lamp-1", "title": "Brass arc floor lamp", "category": "lighting", "price": 340.0},
    {"id": "lamp-2", "title": "Paper pendant light", "category": "lighting", "price": 89.0},
    # bags
    {"id": "bag-1", "title": "Canvas tote", "category": "bags", "price": 48.0},
    {"id": "bag-2", "title": "Leather weekender", "category": "bags", "price": 280.0},
]


def _product(raw: dict, store: str) -> dict:
    """Expand a compact spec into a full Product payload accepted by /admin/catalog."""
    pid = raw["id"]
    return {
        "id": pid,
        "title": raw["title"],
        "price": raw["price"],
        "currency": "USD",
        "availability": "in_stock",
        "image_url": f"https://store.example/img/{pid}.jpg",
        "product_url": f"https://store.example/p/{pid}",
        "store": store,
        "category": raw["category"],
    }


def synthetic_dataset(store: str = "eval-synthetic") -> Dataset:
    """Build the zero-dependency synthetic dataset.

    Each product yields exactly one labelled query whose image is the product's own
    ``image_url``. Because the stub embedder is deterministic on the seed bytes, the
    query embedding equals the indexed embedding and the expected item is the top hit.
    """
    products = [_product(raw, store) for raw in _SYNTHETIC_PRODUCTS]
    queries = [
        Query(
            query_id=f"q-{p['id']}",
            expected_id=p["id"],
            image_url=p["image_url"],
            category=p["category"],
        )
        for p in products
    ]
    return Dataset(store=store, products=products, queries=queries)


def load_dataset(path: str | Path) -> Dataset:
    """Load a real labelled dataset from JSON (format documented in the module docstring)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    store = data["store"]
    products = list(data["products"])
    queries = [
        Query(
            query_id=q["query_id"],
            expected_id=q["expected_id"],
            image_url=q["image_url"],
            category=q.get("category"),
        )
        for q in data["queries"]
    ]
    return Dataset(store=store, products=products, queries=queries)
