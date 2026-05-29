import pytest
from fastapi.testclient import TestClient
from zetix_api import create_app
from zetix_embedding import EMBEDDING_DIM, StubEmbeddingService


@pytest.fixture
def client():
    return TestClient(create_app())


@pytest.fixture
def embedder():
    return StubEmbeddingService()


@pytest.fixture
def sample_products():
    return [
        {
            "id": "sku-1",
            "title": "Mid-century credenza",
            "price": 899.0,
            "currency": "USD",
            "availability": "in_stock",
            "image_url": "https://store.example/img/credenza.jpg",
            "product_url": "https://store.example/p/credenza",
            "store": "acme",
            "category": "furniture",
        },
        {
            "id": "sku-2",
            "title": "Running shoe, teal",
            "price": 120.0,
            "currency": "USD",
            "availability": "out_of_stock",
            "image_url": "https://store.example/img/shoe.jpg",
            "product_url": "https://store.example/p/shoe",
            "store": "acme",
            "category": "footwear",
        },
    ]


@pytest.fixture
def vector_for(embedder):
    """Reproduce the indexing vector for an item so search can target it exactly."""

    def _vector_for(image_url: str):
        vec = embedder.embed_image(image_url.encode("utf-8"))
        assert len(vec) == EMBEDDING_DIM
        return vec

    return _vector_for
