"""Catalog indexing service: embeds products and upserts them into the vector store.

Foundation behaviour: the indexing vector is derived from the product's image URL (or
id, as a fallback) via the embedder. The real EPIC-1 path downloads the image and
embeds it with OpenCLIP — same ``EmbeddingService.embed_image`` interface.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from zetix_embedding import EmbeddingService

from ..schemas import CatalogPushMode, CatalogPushRequest, CatalogPushResponse, Product
from .vector_store import VectorStore


class CatalogService:
    def __init__(self, store: VectorStore, embedder: EmbeddingService) -> None:
        self._store = store
        self._embedder = embedder
        self._last_indexed: dict[str, str] = {}

    def _index_seed(self, product: Product) -> bytes:
        # Stand-in for the real image bytes: the image URL uniquely identifies the
        # visual. Falls back to the product id when no image is present.
        return (product.image_url or product.id).encode("utf-8")

    def push(self, req: CatalogPushRequest) -> CatalogPushResponse:
        if req.mode is CatalogPushMode.full:
            self._store.clear(req.store)

        items: list[tuple[str, list[float], dict]] = []
        for product in req.products:
            vector = self._embedder.embed_image(self._index_seed(product))
            items.append((product.id, vector, product.model_dump(mode="json")))

        indexed = self._store.upsert(req.store, items) if items else 0
        removed = (
            self._store.delete(req.store, req.removed_ids)
            if req.mode is CatalogPushMode.delta and req.removed_ids
            else 0
        )
        self._last_indexed[req.store] = datetime.now(UTC).isoformat()

        return CatalogPushResponse(
            job_id=str(uuid.uuid4()),
            accepted=True,
            mode=req.mode,
            indexed_count=indexed,
            removed_count=removed,
        )

    def count(self, store: str) -> int:
        return self._store.count(store)

    def last_indexed_at(self, store: str) -> str | None:
        return self._last_indexed.get(store)
