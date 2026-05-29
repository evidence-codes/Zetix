from __future__ import annotations

import pytest

pytest.importorskip("chromadb")

from zetix_api.services.chroma_store import ChromaVectorStore  # noqa: E402

STORE = "acme"


@pytest.fixture
def chroma_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ZETIX_CHROMA_PATH", str(tmp_path / "chroma"))
    return ChromaVectorStore()


def test_upsert_query_delete_clear(chroma_store):
    items = [
        ("sku-1", [1.0, 0.0, 0.0], {"id": "sku-1", "title": "credenza"}),
        ("sku-2", [0.0, 1.0, 0.0], {"id": "sku-2", "title": "shoe"}),
    ]
    assert chroma_store.upsert(STORE, items) == 2
    assert chroma_store.count(STORE) == 2

    # Query with sku-1's exact vector -> it ranks first with a high score.
    results = chroma_store.query(STORE, [1.0, 0.0, 0.0], top_k=2)
    assert results[0][0] == "sku-1"
    assert results[0][1] > 0.99
    assert results[0][2]["title"] == "credenza"

    # payload_filter is applied in Python.
    filtered = chroma_store.query(
        STORE,
        [1.0, 0.0, 0.0],
        top_k=2,
        payload_filter=lambda p: p["id"] == "sku-2",
    )
    assert [r[0] for r in filtered] == ["sku-2"]

    # Delete drops the count by one.
    assert chroma_store.delete(STORE, ["sku-1"]) == 1
    assert chroma_store.count(STORE) == 1

    # Clear empties the store.
    chroma_store.clear(STORE)
    assert chroma_store.count(STORE) == 0
    assert chroma_store.query(STORE, [1.0, 0.0, 0.0], top_k=5) == []


def test_clear_on_empty_store_is_idempotent(chroma_store):
    # A full catalog push clears before indexing; the collection may not exist yet,
    # so clear() on a fresh store must not raise.
    chroma_store.clear("never-seen")
    assert chroma_store.count("never-seen") == 0
