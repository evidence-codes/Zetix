"""Embedding service protocol + deterministic stub implementation."""

from __future__ import annotations

import hashlib
from typing import Protocol, runtime_checkable

import numpy as np

# CLIP ViT-B/32 produces 512-dim embeddings (PRD §7.3). The whole stack is pinned to
# this dimension; changing it is a contract change across server + apps.
EMBEDDING_DIM = 512


@runtime_checkable
class EmbeddingService(Protocol):
    """Generates a normalised embedding vector for an image.

    Real implementation (EPIC-1): OpenCLIP ViT-B/32, GPU-accelerated on the indexing
    path. The returned vector is L2-normalised so cosine similarity == dot product.
    """

    def embed_image(self, data: bytes) -> list[float]:
        """Embed raw image bytes into an ``EMBEDDING_DIM`` vector."""
        ...


def _seed_vector(seed: str) -> list[float]:
    """Deterministic, L2-normalised pseudo-embedding derived from a seed string.

    Stub-only: lets the indexing + search pipeline run end-to-end (and be tested)
    without a real model. Same seed always yields the same vector, so an item indexed
    from a given seed is retrievable by querying with that seed's vector.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    vec = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


class StubEmbeddingService:
    """Deterministic embedder for the Phase 1 foundation.

    Treats the input bytes as the seed, so callers can reproduce a vector by passing
    the same bytes (e.g. a product's image URL on the indexing path). Replaced by an
    OpenCLIP-backed service in EPIC-1.
    """

    def embed_image(self, data: bytes) -> list[float]:
        return _seed_vector(data.decode("utf-8", errors="replace"))
