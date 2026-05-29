"""Pydantic request/response models mirroring packages/contracts/openapi.yaml.

The OpenAPI spec is the source of truth; these models must stay in sync (codegen
planned in EPIC-0.5 / 1.C). Keep field names and enums identical to the contract.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator
from zetix_embedding import EMBEDDING_DIM


class Availability(StrEnum):
    in_stock = "in_stock"
    out_of_stock = "out_of_stock"
    preorder = "preorder"
    unknown = "unknown"


class Health(BaseModel):
    status: str = "ok"
    version: str


class Product(BaseModel):
    id: str
    title: str
    description: str | None = None
    price: float
    currency: str
    availability: Availability = Availability.unknown
    image_url: str | None = None
    product_url: str
    store: str
    category: str | None = None
    attributes: dict | None = None


class ScoredProduct(BaseModel):
    product: Product
    score: float = Field(description="Cosine similarity in [0, 1]")


class SearchFilters(BaseModel):
    category: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    in_stock_only: bool = False


class ImageInput(BaseModel):
    base64: str | None = None
    url: str | None = None


class SearchRequest(BaseModel):
    store: str
    vector: list[float] | None = None
    image: ImageInput | None = None
    top_k: int = Field(default=10, ge=1, le=100)
    filters: SearchFilters | None = None

    @model_validator(mode="after")
    def _validate_query(self) -> SearchRequest:
        if (self.vector is None) == (self.image is None):
            raise ValueError("provide exactly one of 'vector' or 'image'")
        if self.vector is not None and len(self.vector) != EMBEDDING_DIM:
            raise ValueError(f"vector must have {EMBEDDING_DIM} elements")
        return self


class SearchResponse(BaseModel):
    results: list[ScoredProduct]
    # Ephemeral trace id only; NOT a key into stored data — vectors are not persisted
    # (ADR-0002 / D-7).
    query_id: str
    latency_ms: float


class CatalogPushMode(StrEnum):
    full = "full"
    delta = "delta"


class CatalogPushRequest(BaseModel):
    store: str
    mode: CatalogPushMode
    products: list[Product] = Field(default_factory=list)
    removed_ids: list[str] = Field(default_factory=list)


class CatalogPushResponse(BaseModel):
    job_id: str
    accepted: bool
    mode: CatalogPushMode
    indexed_count: int
    removed_count: int = 0


class IndexStatus(BaseModel):
    store: str
    product_count: int
    last_indexed_at: str | None = None
    status: str = Field(description="empty | indexing | ready")
