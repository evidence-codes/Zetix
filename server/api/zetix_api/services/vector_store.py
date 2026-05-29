"""Vector store protocol + an in-memory, numpy-backed reference implementation.

EPIC-1 (sub-task 1.B.3) replaces ``InMemoryVectorStore`` with a ChromaDB-backed store
behind the same ``VectorStore`` protocol. Vectors are assumed L2-normalised, so cosine
similarity reduces to a dot product.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class VectorStore(Protocol):
    def upsert(self, store: str, items: list[tuple[str, list[float], dict]]) -> int: ...
    def delete(self, store: str, ids: list[str]) -> int: ...
    def clear(self, store: str) -> None: ...
    def count(self, store: str) -> int: ...
    def query(
        self,
        store: str,
        vector: list[float],
        top_k: int,
        payload_filter=None,
    ) -> list[tuple[str, float, dict]]: ...


class InMemoryVectorStore:
    """Per-store {id -> (vector, payload)} held in memory. Not for production."""

    def __init__(self) -> None:
        self._stores: dict[str, dict[str, tuple[np.ndarray, dict]]] = {}

    def _ns(self, store: str) -> dict[str, tuple[np.ndarray, dict]]:
        return self._stores.setdefault(store, {})

    def upsert(self, store: str, items: list[tuple[str, list[float], dict]]) -> int:
        ns = self._ns(store)
        for pid, vec, payload in items:
            ns[pid] = (np.asarray(vec, dtype=np.float32), payload)
        return len(items)

    def delete(self, store: str, ids: list[str]) -> int:
        ns = self._ns(store)
        removed = 0
        for pid in ids:
            if ns.pop(pid, None) is not None:
                removed += 1
        return removed

    def clear(self, store: str) -> None:
        self._stores[store] = {}

    def count(self, store: str) -> int:
        return len(self._ns(store))

    def query(
        self,
        store: str,
        vector: list[float],
        top_k: int,
        payload_filter=None,
    ) -> list[tuple[str, float, dict]]:
        ns = self._ns(store)
        if not ns:
            return []
        q = np.asarray(vector, dtype=np.float32)
        qn = np.linalg.norm(q)
        if qn > 0:
            q = q / qn

        scored: list[tuple[str, float, dict]] = []
        for pid, (vec, payload) in ns.items():
            if payload_filter is not None and not payload_filter(payload):
                continue
            vn = np.linalg.norm(vec)
            denom = vn if vn > 0 else 1.0
            score = float(np.dot(q, vec / denom))
            scored.append((pid, score, payload))

        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_k]
