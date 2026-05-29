"""Zetix embedding service.

The on-device path produces query vectors itself; this server-side service is used on
the *indexing* path (embed catalog images) and the server-side image-search path.

Phase 1 ships a deterministic stub so the full pipeline is runnable without heavy ML
deps. A real OpenCLIP-backed implementation replaces ``StubEmbeddingService`` in
EPIC-1 (sub-task 1.B.1) behind the same ``EmbeddingService`` protocol.
"""

from .service import EMBEDDING_DIM, EmbeddingService, StubEmbeddingService

__all__ = ["EMBEDDING_DIM", "EmbeddingService", "StubEmbeddingService"]
