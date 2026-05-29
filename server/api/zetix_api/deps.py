"""FastAPI dependency accessors — pull singletons off app.state.

Wiring lives in ``main.create_app`` so tests can construct an app with swapped
implementations (e.g. a ChromaDB store) without touching the routers.
"""

from __future__ import annotations

from fastapi import Request
from zetix_embedding import EmbeddingService

from .config import Settings
from .services import CatalogService, VectorStore


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_embedder(request: Request) -> EmbeddingService:
    return request.app.state.embedder


def get_catalog(request: Request) -> CatalogService:
    return request.app.state.catalog
