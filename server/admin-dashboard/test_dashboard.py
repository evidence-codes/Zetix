"""Tests for the standalone admin dashboard.

The dashboard talks to the Zetix API over HTTP. These tests monkeypatch the
``httpx`` client factory so no live API is required: ``get_client`` is replaced
with a fake client returning canned responses.
"""

from __future__ import annotations

import json
from typing import Any

import app as dashboard
import pytest
from fastapi.testclient import TestClient


class _FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        return None


class _FakeClient:
    """Stand-in for ``httpx.Client`` used as a context manager."""

    def __init__(self) -> None:
        self.posted: dict[str, Any] | None = None

    def __enter__(self) -> _FakeClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get(self, path: str, params: dict[str, Any] | None = None) -> _FakeResponse:
        return _FakeResponse(
            {
                "store": (params or {}).get("store", "acme"),
                "product_count": 42,
                "last_indexed_at": "2026-05-29T10:00:00Z",
                "status": "ready",
            }
        )

    def post(self, path: str, json: dict[str, Any] | None = None) -> _FakeResponse:
        self.posted = json
        products = (json or {}).get("products", [])
        return _FakeResponse(
            {
                "job_id": "job_test",
                "accepted": True,
                "mode": (json or {}).get("mode", "full"),
                "indexed_count": len(products),
                "removed_count": 0,
            },
            status_code=202,
        )


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> _FakeClient:
    client = _FakeClient()
    monkeypatch.setattr(dashboard, "get_client", lambda: client)
    return client


@pytest.fixture
def test_client(fake_client: _FakeClient) -> TestClient:
    return TestClient(dashboard.app)


def test_index_renders_three_sections(test_client: TestClient) -> None:
    resp = test_client.get("/")
    assert resp.status_code == 200
    body = resp.text
    assert "Catalog Upload" in body
    assert "Index Status" in body
    assert "Search Logs" in body


def test_index_shows_live_index_status(test_client: TestClient) -> None:
    resp = test_client.get("/")
    assert resp.status_code == 200
    # product_count from the fake API response is rendered.
    assert "42" in resp.text
    assert "ready" in resp.text


def test_search_logs_labelled_as_stub(test_client: TestClient) -> None:
    resp = test_client.get("/")
    assert "Stub data" in resp.text
    assert "ADR-0002" in resp.text


def test_catalog_upload_json_pushes_to_api(
    test_client: TestClient, fake_client: _FakeClient
) -> None:
    products = [
        {
            "id": "sku-1",
            "title": "Thing",
            "price": 9.99,
            "currency": "USD",
            "product_url": "https://store.example/p/1",
            "store": "acme",
        }
    ]
    resp = test_client.post(
        "/catalog",
        data={"store": "acme", "mode": "full", "fmt": "json", "data": json.dumps(products)},
    )
    assert resp.status_code == 200
    assert "indexed 1" in resp.text
    assert fake_client.posted is not None
    assert fake_client.posted["mode"] == "full"
    assert len(fake_client.posted["products"]) == 1


def test_catalog_upload_invalid_json_shows_error(test_client: TestClient) -> None:
    resp = test_client.post(
        "/catalog",
        data={"store": "acme", "mode": "full", "fmt": "json", "data": "{not json"},
    )
    assert resp.status_code == 200
    assert "Could not parse JSON" in resp.text


def test_parse_csv_coerces_price() -> None:
    csv_text = (
        "id,title,price,currency,product_url,store\nsku-1,Thing,9.99,USD,https://x/p/1,acme\n"
    )
    parsed = dashboard.parse_products(csv_text, "csv")
    assert parsed.error is None
    assert parsed.products[0]["price"] == 9.99
    assert isinstance(parsed.products[0]["price"], float)


def test_parse_products_empty_input() -> None:
    parsed = dashboard.parse_products("   ", "json")
    assert parsed.error is not None
    assert parsed.products == []
