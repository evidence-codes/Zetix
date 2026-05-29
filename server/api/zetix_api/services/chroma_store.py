"""ChromaDB-backed vector store (EPIC-1, sub-task 1.B.3).

A ``VectorStore`` implementation backed by a persistent ChromaDB client. One Chroma
collection is used per ``store`` namespace, configured for cosine space. Product
payloads are stored as a JSON string in collection metadata (Chroma metadata values
must be flat scalars), and cosine *distance* is converted to a similarity *score* in
``[0, 1]`` on query. Selected at runtime via ``ZETIX_VECTOR_STORE=chroma``.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
from collections.abc import Callable

_PAYLOAD_KEY = "payload"


def _sanitise(store: str) -> str:
    """Map an arbitrary store namespace to a valid Chroma collection name.

    Chroma requires names of length 3-63, starting/ending with an alphanumeric, and
    containing only ``[a-zA-Z0-9._-]`` (no consecutive dots). We slug the input and pad
    so any non-empty store yields a stable, valid name.
    """

    slug = re.sub(r"[^a-zA-Z0-9._-]", "-", store).strip("-._")
    slug = re.sub(r"\.\.+", ".", slug)
    if not slug:
        slug = "store"
    slug = f"z-{slug}"
    if len(slug) < 3:
        slug = slug.ljust(3, "0")
    return slug[:63]


class ChromaVectorStore:
    """Per-store ChromaDB collections behind the ``VectorStore`` protocol."""

    def __init__(self) -> None:
        import chromadb

        path = os.getenv("ZETIX_CHROMA_PATH", "./.chroma")
        self._client = chromadb.PersistentClient(path=path)

    def _collection(self, store: str):
        return self._client.get_or_create_collection(
            name=_sanitise(store),
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, store: str, items: list[tuple[str, list[float], dict]]) -> int:
        if not items:
            return 0
        collection = self._collection(store)
        ids = [pid for pid, _vec, _payload in items]
        embeddings = [list(vec) for _pid, vec, _payload in items]
        metadatas = [{_PAYLOAD_KEY: json.dumps(payload)} for _pid, _vec, payload in items]
        collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)
        return len(items)

    def delete(self, store: str, ids: list[str]) -> int:
        if not ids:
            return 0
        collection = self._collection(store)
        existing = collection.get(ids=ids).get("ids", [])
        if not existing:
            return 0
        collection.delete(ids=existing)
        return len(existing)

    def clear(self, store: str) -> None:
        # Collection may not exist yet (e.g. the first full catalog push clears an
        # empty store) — suppress the not-found case.
        with contextlib.suppress(Exception):
            self._client.delete_collection(name=_sanitise(store))
        # Recreate so subsequent count/query/upsert calls work against an empty store.
        self._collection(store)

    def count(self, store: str) -> int:
        return self._collection(store).count()

    def query(
        self,
        store: str,
        vector: list[float],
        top_k: int,
        payload_filter: Callable[[dict], bool] | None = None,
    ) -> list[tuple[str, float, dict]]:
        if top_k <= 0:
            return []
        collection = self._collection(store)
        total = collection.count()
        if total == 0:
            return []

        # Over-fetch so we can apply ``payload_filter`` in Python and still honour top_k.
        n_results = min(total, max(top_k * 5, top_k + 20))
        res = collection.query(
            query_embeddings=[list(vector)],
            n_results=n_results,
            include=["distances", "metadatas"],
        )

        ids = (res.get("ids") or [[]])[0]
        distances = (res.get("distances") or [[]])[0]
        metadatas = (res.get("metadatas") or [[]])[0]

        scored: list[tuple[str, float, dict]] = []
        for pid, distance, metadata in zip(ids, distances, metadatas, strict=True):
            payload = json.loads((metadata or {}).get(_PAYLOAD_KEY, "{}"))
            if payload_filter is not None and not payload_filter(payload):
                continue
            score = max(0.0, 1.0 - float(distance))
            scored.append((pid, score, payload))

        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_k]
