"""FastAPI application factory.

``create_app`` wires the service singletons onto ``app.state`` using the Phase 1
in-memory reference implementations. EPIC-1 agents pass real implementations
(ChromaDB store, OpenCLIP embedder) without changing routers.
"""

from __future__ import annotations

from fastapi import FastAPI
from zetix_embedding import EmbeddingService

from .config import Settings
from .factory import build_embedder, build_vector_store
from .routers import admin, search
from .schemas import Health
from .services import CatalogService, VectorStore


def create_app(
    *,
    settings: Settings | None = None,
    vector_store: VectorStore | None = None,
    embedder: EmbeddingService | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    vector_store = vector_store or build_vector_store()
    embedder = embedder or build_embedder()

    app = FastAPI(title="Zetix API", version=settings.version)
    app.state.settings = settings
    app.state.vector_store = vector_store
    app.state.embedder = embedder
    app.state.catalog = CatalogService(vector_store, embedder)

    @app.get("/health", response_model=Health, tags=["meta"])
    def health() -> Health:
        return Health(version=settings.version)

    app.include_router(search.router)
    app.include_router(admin.router)
    return app


app = create_app()
