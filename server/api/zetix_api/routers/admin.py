"""Admin catalog endpoints (FR-35): push catalog + report index status."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import get_catalog
from ..schemas import CatalogPushRequest, CatalogPushResponse, IndexStatus
from ..services import CatalogService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/catalog", status_code=202, response_model=CatalogPushResponse)
def push_catalog(
    req: CatalogPushRequest,
    catalog: CatalogService = Depends(get_catalog),
) -> CatalogPushResponse:
    return catalog.push(req)


@router.get("/index/status", response_model=IndexStatus)
def index_status(
    store: str,
    catalog: CatalogService = Depends(get_catalog),
) -> IndexStatus:
    count = catalog.count(store)
    return IndexStatus(
        store=store,
        product_count=count,
        last_indexed_at=catalog.last_indexed_at(store),
        status="ready" if count > 0 else "empty",
    )
