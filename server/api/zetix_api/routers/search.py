"""POST /search — ranked visual product search (FR-34, FR-06).

Privacy: the query vector / image is used only to compute results and is never
persisted (ADR-0002). The returned query_id is an ephemeral trace id.
"""

from __future__ import annotations

import base64
import time
import uuid

from fastapi import APIRouter, Depends
from zetix_embedding import EmbeddingService

from ..deps import get_embedder, get_vector_store
from ..schemas import (
    Product,
    ScoredProduct,
    SearchFilters,
    SearchRequest,
    SearchResponse,
)
from ..services import VectorStore

router = APIRouter(tags=["search"])


def _make_filter(filters: SearchFilters | None):
    if filters is None:
        return None

    def predicate(payload: dict) -> bool:
        if filters.category and payload.get("category") != filters.category:
            return False
        price = payload.get("price")
        if filters.price_min is not None and (price is None or price < filters.price_min):
            return False
        if filters.price_max is not None and (price is None or price > filters.price_max):
            return False
        return not (filters.in_stock_only and payload.get("availability") != "in_stock")

    return predicate


@router.post("/search", response_model=SearchResponse)
def search(
    req: SearchRequest,
    store: VectorStore = Depends(get_vector_store),
    embedder: EmbeddingService = Depends(get_embedder),
) -> SearchResponse:
    started = time.perf_counter()

    if req.vector is not None:
        vector = req.vector
    else:
        # Server-side image path (admin/testing). On-device clients send the vector.
        assert req.image is not None  # guaranteed by SearchRequest validation
        if req.image.base64:
            data = base64.b64decode(req.image.base64)
        else:
            # A real impl fetches req.image.url; the stub seeds from the URL string.
            data = (req.image.url or "").encode("utf-8")
        vector = embedder.embed_image(data)

    hits = store.query(req.store, vector, req.top_k, _make_filter(req.filters))
    results = [
        ScoredProduct(product=Product.model_validate(payload), score=score)
        for _id, score, payload in hits
    ]

    latency_ms = (time.perf_counter() - started) * 1000.0
    return SearchResponse(results=results, query_id=str(uuid.uuid4()), latency_ms=latency_ms)
