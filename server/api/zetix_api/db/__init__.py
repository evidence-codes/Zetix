"""Database layer for catalog metadata (EPIC-1, tasks 1.A.1 / 1.C.6).

Schema-only SQLAlchemy 2.0 models for catalog metadata, store configuration, and
sync state. Nothing here is wired into the running app yet — it backs the future
PostgreSQL-backed catalog store. See :mod:`zetix_api.db.models`.

GDPR/NDPA: these tables hold product/catalog metadata only and contain NO PII.
"""

from __future__ import annotations

from .models import Base, ProductRow, StoreConfig, SyncState, create_all

__all__ = ["Base", "ProductRow", "StoreConfig", "SyncState", "create_all"]
