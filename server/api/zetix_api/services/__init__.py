"""Service interfaces + in-memory reference implementations for the Phase 1 foundation."""

from .catalog import CatalogService
from .vector_store import InMemoryVectorStore, VectorStore

__all__ = ["CatalogService", "InMemoryVectorStore", "VectorStore"]
