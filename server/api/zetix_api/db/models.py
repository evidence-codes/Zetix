"""SQLAlchemy 2.0 catalog metadata models (EPIC-1, tasks 1.A.1 / 1.C.6).

Schema-only declarative models for the future PostgreSQL-backed catalog store:

- :class:`ProductRow`  — per-store product catalog metadata.
- :class:`StoreConfig` — per-store namespace + settings.
- :class:`SyncState`   — incremental-sync bookkeeping (cursor/etag/last sync).

GDPR/NDPA COMPLIANCE (NFR-S6, task 1.C.6)
-----------------------------------------
These tables intentionally contain **no personal data**: only product/catalog
metadata and store configuration. There are no customer, user, email, address, or
other PII columns. Any future PII would require consent gating and a new ADR. This
also aligns with ADR-0002 (no retention of fallback query vectors).

``sqlalchemy`` is imported lazily (module-level but optional via the ``[db]`` extra);
the rest of the app does not import this module.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all catalog-metadata models."""


class StoreConfig(Base):
    """Per-store namespace and free-form settings (no PII)."""

    __tablename__ = "store_config"

    store: Mapped[str] = mapped_column(String(128), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ProductRow(Base):
    """Catalog metadata for one product within a store (no PII).

    Composite-keyed on ``(store, id)`` so the same external id can exist across
    stores. Mirrors :class:`zetix_api.schemas.Product` minus the embedding vector
    (vectors live in the vector store, never here).
    """

    __tablename__ = "product"
    __table_args__ = (Index("ix_product_store_category", "store", "category"),)

    store: Mapped[str] = mapped_column(
        String(128), ForeignKey("store_config.store"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String(256), primary_key=True)
    title: Mapped[str] = mapped_column(String(1024))
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8))
    availability: Mapped[str] = mapped_column(String(32), default="unknown")
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    product_url: Mapped[str] = mapped_column(String(2048))
    category: Mapped[str | None] = mapped_column(String(256), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SyncState(Base):
    """Incremental-sync bookkeeping per store (no PII)."""

    __tablename__ = "sync_state"

    store: Mapped[str] = mapped_column(
        String(128), ForeignKey("store_config.store"), primary_key=True
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cursor: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    etag: Mapped[str | None] = mapped_column(String(512), nullable=True)


def create_all(engine) -> None:
    """Create all catalog-metadata tables on ``engine`` (idempotent).

    ``engine`` is a SQLAlchemy ``Engine``; left untyped to avoid importing the type.
    """
    Base.metadata.create_all(engine)
