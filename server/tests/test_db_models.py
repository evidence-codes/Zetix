from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from zetix_api.db import ProductRow, StoreConfig, create_all  # noqa: E402


def _engine():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    create_all(engine)
    return engine


def test_create_all_and_roundtrip_product_row() -> None:
    engine = _engine()
    with Session(engine) as session:
        session.add(StoreConfig(store="acme", display_name="Acme"))
        session.add(
            ProductRow(
                store="acme",
                id="sku-1",
                title="Credenza",
                price=899.0,
                currency="USD",
                availability="in_stock",
                image_url="https://s.example/c.jpg",
                product_url="https://s.example/p/c",
                category="furniture",
                attributes={"color": "walnut"},
            )
        )
        session.commit()

    with Session(engine) as session:
        row = session.scalars(
            select(ProductRow).where(ProductRow.store == "acme", ProductRow.id == "sku-1")
        ).one()
        assert row.title == "Credenza"
        assert row.price == 899.0
        assert row.availability == "in_stock"
        assert row.attributes == {"color": "walnut"}


def test_no_pii_columns() -> None:
    # GDPR/NDPA guard (task 1.C.6): assert the catalog tables carry no PII columns.
    pii_markers = ("email", "phone", "name_first", "last_name", "address", "user", "customer")
    for table in (ProductRow, StoreConfig):
        cols = {c.name.lower() for c in table.__table__.columns}
        assert not any(marker in col for col in cols for marker in pii_markers)
