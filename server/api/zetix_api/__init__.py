"""Zetix search API (FastAPI). Phase 1 / EPIC-1.

Foundation skeleton: routers, schemas, and service *interfaces* with in-memory
reference implementations. The parallel EPIC-1 agents swap the in-memory vector store
for ChromaDB and the stub embedder for OpenCLIP, behind the same protocols.
"""

from .main import create_app

__all__ = ["create_app"]
