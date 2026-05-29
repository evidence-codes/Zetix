"""Tests for the OpenCLIP-backed embedder.

Skips cleanly when the optional ``[ml]`` deps (torch, open_clip) are absent.
"""

import io
import math

import pytest

pytest.importorskip("torch")
pytest.importorskip("open_clip")

from PIL import Image  # noqa: E402
from zetix_embedding import EMBEDDING_DIM  # noqa: E402
from zetix_embedding.openclip import OpenCLIPEmbeddingService  # noqa: E402


def _tiny_png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color=(120, 200, 60)).save(buf, format="PNG")
    return buf.getvalue()


def test_embed_image_returns_unit_norm_512_vector():
    service = OpenCLIPEmbeddingService()
    vector = service.embed_image(_tiny_png())

    assert len(vector) == EMBEDDING_DIM
    norm = math.sqrt(sum(component * component for component in vector))
    assert abs(norm - 1.0) < 1e-3
