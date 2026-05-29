"""Runtime selection of the embedder and vector-store backends.

Defaults to the Phase 1 reference implementations (deterministic stub embedder,
in-memory vector store). Set environment variables to use the real EPIC-1 backends:

    ZETIX_EMBEDDER=openclip       # zetix_embedding.openclip.OpenCLIPEmbeddingService
    ZETIX_VECTOR_STORE=chroma     # zetix_api.services.chroma_store.ChromaVectorStore

Imports of the heavy backends are lazy, so the defaults work without the optional
deps installed. The fleet agents add the concrete classes at the paths above; this
factory needs no edits when they land.
"""

from __future__ import annotations

import os

from zetix_embedding import EmbeddingService, StubEmbeddingService

from .services import InMemoryVectorStore, VectorStore


def build_embedder() -> EmbeddingService:
    kind = os.getenv("ZETIX_EMBEDDER", "stub").lower()
    if kind == "openclip":
        from zetix_embedding.openclip import OpenCLIPEmbeddingService

        return OpenCLIPEmbeddingService()
    return StubEmbeddingService()


def build_vector_store() -> VectorStore:
    kind = os.getenv("ZETIX_VECTOR_STORE", "memory").lower()
    if kind == "chroma":
        from .services.chroma_store import ChromaVectorStore

        return ChromaVectorStore()
    return InMemoryVectorStore()
