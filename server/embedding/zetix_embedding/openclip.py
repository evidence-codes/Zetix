"""OpenCLIP-backed embedding service (EPIC-1, sub-task 1.B.1).

Real ``EmbeddingService`` implementation: CLIP ViT-B/32 via open-clip-torch,
producing L2-normalised 512-dim image embeddings (so cosine similarity == dot
product). Selected at runtime with ``ZETIX_EMBEDDER=openclip`` (see
``zetix_api.factory``).

The heavy deps (torch, open_clip, PIL) are imported lazily inside ``__init__`` /
methods, so importing this module without the ``[ml]`` extra installed does not
crash — only constructing the service does.
"""

from __future__ import annotations

import io

from .service import EMBEDDING_DIM

# CLIP ViT-B/32 backbone. "laion2b_s34b_b79k" are the OpenCLIP LAION-2B weights;
# both this and "openai" yield 512-dim embeddings.
_MODEL_NAME = "ViT-B-32"
_PRETRAINED = "laion2b_s34b_b79k"


class OpenCLIPEmbeddingService:
    """Embeds image bytes with OpenCLIP ViT-B/32.

    The model and preprocessing transform are loaded once at construction and
    reused for every call. ``embed_image`` returns an L2-normalised, 512-dim
    Python list of floats.
    """

    def __init__(
        self,
        model_name: str = _MODEL_NAME,
        pretrained: str = _PRETRAINED,
    ) -> None:
        import open_clip
        import torch

        self._torch = torch
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        model.eval()
        self._model = model
        self._preprocess = preprocess

    def embed_image(self, data: bytes) -> list[float]:
        """Embed raw image bytes into an ``EMBEDDING_DIM`` vector."""
        from PIL import Image

        torch = self._torch
        with Image.open(io.BytesIO(data)) as img:
            image = img.convert("RGB")
            tensor = self._preprocess(image).unsqueeze(0)

        with torch.no_grad():
            features = self._model.encode_image(tensor)
            features = features / features.norm(dim=-1, keepdim=True)

        vector = features.squeeze().tolist()
        assert len(vector) == EMBEDDING_DIM, (
            f"expected {EMBEDDING_DIM}-dim embedding, got {len(vector)}"
        )
        return vector
