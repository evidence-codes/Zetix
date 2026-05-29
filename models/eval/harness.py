"""Search-quality evaluation harness (TASKS 1.E.2 / 1.E.3).

Computes Top-1 / Top-3 / Top-5 accuracy and a per-category breakdown for visual
search, driving the *real* pipeline through its public seams:

1. Build the FastAPI app via ``from zetix_api import create_app`` (no network).
2. Push the catalog through ``POST /admin/catalog``.
3. For each labelled query, derive the query vector the *same way the catalog indexes*
   an item (the embedder seeds from the product's ``image_url or id`` bytes — see
   ``services/catalog.py`` ``_index_seed`` and ``StubEmbeddingService``), then call
   ``POST /search`` and check whether the expected product id is within top-k.

Methodology note: deriving the query vector identically to the indexing vector makes
this a real end-to-end search through the API, but on the *stub* embedder it is an
exact-vector match — so synthetic accuracy is high BY CONSTRUCTION. Real M1 accuracy
requires ``ZETIX_EMBEDDER=openclip`` and a real labelled 10k catalog, where the query
image and the catalog image differ and similarity is genuinely tested.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# Put the server packages (zetix_api / zetix_embedding) on sys.path *before* importing
# them, so the harness runs without installing the server package. A no-op when it is
# already importable (e.g. the server venv). Kept inline (not a helper import) so the
# wiring is guaranteed to run ahead of the third-party imports below.
_REPO_ROOT = Path(__file__).resolve().parents[2]
for _root in (_REPO_ROOT / "server" / "api", _REPO_ROOT / "server" / "embedding"):
    if _root.is_dir() and str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from zetix_api import create_app  # noqa: E402
from zetix_embedding import EMBEDDING_DIM, StubEmbeddingService  # noqa: E402

from .dataset import Dataset, Query, synthetic_dataset  # noqa: E402

# Top-k cutoffs reported. Must request at least max(K) results from /search.
TOP_KS = (1, 3, 5)


@dataclass
class QueryResult:
    """Per-query outcome: where (if at all) the expected id ranked."""

    query_id: str
    expected_id: str
    category: str | None
    rank: int | None  # 1-based rank of the expected id, or None if not in results
    top_id: str | None  # id of the rank-1 result (for eyeballing misses)

    def hit_at(self, k: int) -> bool:
        return self.rank is not None and self.rank <= k


def _index_seed_bytes(query: Query) -> bytes:
    """Reproduce the bytes the catalog embeds for a product.

    Mirrors ``CatalogService._index_seed``: the image URL (or id) uniquely identifies
    the visual. The synthetic queries carry the product's own ``image_url``.
    """
    return (query.image_url or query.expected_id).encode("utf-8")


def _push_catalog(client, dataset: Dataset) -> None:
    resp = client.post(
        "/admin/catalog",
        json={"store": dataset.store, "mode": "full", "products": dataset.products},
    )
    resp.raise_for_status()
    body = resp.json()
    if body["indexed_count"] != len(dataset.products):
        raise RuntimeError(
            f"indexed {body['indexed_count']} of {len(dataset.products)} products"
        )


def _evaluate_query(client, store: str, embedder, query: Query, top_k: int) -> QueryResult:
    vector = embedder.embed_image(_index_seed_bytes(query))
    if len(vector) != EMBEDDING_DIM:
        raise RuntimeError(f"query vector has {len(vector)} dims, expected {EMBEDDING_DIM}")

    resp = client.post(
        "/search",
        json={"store": store, "vector": vector, "top_k": top_k},
    )
    resp.raise_for_status()
    results = resp.json()["results"]
    ranked_ids = [r["product"]["id"] for r in results]

    rank = ranked_ids.index(query.expected_id) + 1 if query.expected_id in ranked_ids else None
    return QueryResult(
        query_id=query.query_id,
        expected_id=query.expected_id,
        category=query.category,
        rank=rank,
        top_id=ranked_ids[0] if ranked_ids else None,
    )


def _accuracies(results: list[QueryResult]) -> dict[str, float]:
    total = len(results)
    if total == 0:
        return {f"top{k}": 0.0 for k in TOP_KS}
    return {f"top{k}": sum(r.hit_at(k) for r in results) / total for k in TOP_KS}


def _per_category(results: list[QueryResult]) -> dict[str, dict]:
    buckets: dict[str, list[QueryResult]] = defaultdict(list)
    for r in results:
        buckets[r.category or "uncategorised"].append(r)
    return {
        category: {"count": len(group), **_accuracies(group)}
        for category, group in sorted(buckets.items())
    }


def evaluate(dataset: Dataset) -> dict:
    """Run the full eval over a dataset and return a structured result dict.

    The embedder used to derive query vectors is the *same kind* the server selects via
    env (default: stub), so the query and indexing vectors are derived consistently.
    """
    # FastAPI TestClient is imported lazily so importing this module doesn't require it.
    from fastapi.testclient import TestClient

    app = create_app()
    # The harness derives query vectors with the same embedder family the app indexes
    # with. StubEmbeddingService is deterministic on the seed bytes; swapping in OpenCLIP
    # (ZETIX_EMBEDDER=openclip) would require embedding real image bytes here too.
    embedder = StubEmbeddingService()
    top_k = max(TOP_KS)

    with TestClient(app) as client:
        _push_catalog(client, dataset)
        results = [
            _evaluate_query(client, dataset.store, embedder, q, top_k)
            for q in dataset.queries
        ]

    return {
        "store": dataset.store,
        "n_products": len(dataset.products),
        "n_queries": len(results),
        **_accuracies(results),
        "per_category": _per_category(results),
        "queries": [
            {
                "query_id": r.query_id,
                "expected_id": r.expected_id,
                "category": r.category,
                "rank": r.rank,
                "top_id": r.top_id,
                "hit_top1": r.hit_at(1),
                "hit_top3": r.hit_at(3),
                "hit_top5": r.hit_at(5),
            }
            for r in results
        ],
    }


# --- Reporting ---------------------------------------------------------------------

M1_TOP3_BAR = 0.80


def format_report(result: dict) -> str:
    """Render a human-readable report from a structured eval result."""
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("Zetix search-quality eval (TASKS 1.E.2 / 1.E.3)")
    lines.append("=" * 70)
    lines.append(
        f"store={result['store']}  products={result['n_products']}  "
        f"queries={result['n_queries']}"
    )
    lines.append("")
    lines.append("Per-query results:")
    lines.append(f"  {'query':<14}{'expected':<10}{'rank':<6}{'top-1 result':<16}result")
    for q in result["queries"]:
        rank = "-" if q["rank"] is None else str(q["rank"])
        verdict = "HIT " if q["hit_top3"] else "MISS"
        lines.append(
            f"  {q['query_id']:<14}{q['expected_id']:<10}{rank:<6}"
            f"{(q['top_id'] or '-'):<16}{verdict}"
        )
    lines.append("")
    lines.append("Aggregate accuracy:")
    for k in TOP_KS:
        lines.append(f"  Top-{k}: {result[f'top{k}']:.1%}")
    lines.append("")
    lines.append("Per-category accuracy (niche-category risk check, 1.E.3):")
    lines.append(f"  {'category':<16}{'n':<5}{'Top-1':<9}{'Top-3':<9}Top-5")
    for category, stats in result["per_category"].items():
        lines.append(
            f"  {category:<16}{stats['count']:<5}"
            f"{stats['top1']:<9.1%}{stats['top3']:<9.1%}{stats['top5']:.1%}"
        )
    lines.append("")
    passed = result["top3"] >= M1_TOP3_BAR
    bar = f"M1 acceptance bar: Top-3 > {M1_TOP3_BAR:.0%}"
    lines.append(f"{bar}  ->  Top-3={result['top3']:.1%}  [{'PASS' if passed else 'BELOW BAR'}]")
    lines.append(
        "NOTE: synthetic accuracy is high BY CONSTRUCTION (stub exact-vector match). "
        "Real M1 needs ZETIX_EMBEDDER=openclip + a real labelled 10k catalog."
    )
    lines.append("=" * 70)
    return "\n".join(lines)


def run(dataset: Dataset | None = None, *, json_out: str | None = None) -> dict:
    """Evaluate ``dataset`` (default: synthetic), print the report, return the result.

    If ``json_out`` is given, the structured result is also written there as JSON.
    """
    dataset = dataset or synthetic_dataset()
    result = evaluate(dataset)
    print(format_report(result))
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print(f"\nWrote structured result to {json_out}")
    return result
