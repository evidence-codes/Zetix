from zetix_embedding import EMBEDDING_DIM


def _index(client, products):
    client.post(
        "/admin/catalog",
        json={"store": "acme", "mode": "full", "products": products},
    )


def test_search_by_vector_ranks_exact_match_first(client, sample_products, vector_for):
    _index(client, sample_products)
    # Query with the exact vector the credenza was indexed from -> it should rank #1.
    q = vector_for(sample_products[0]["image_url"])
    resp = client.post("/search", json={"store": "acme", "vector": q, "top_k": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"][0]["product"]["id"] == "sku-1"
    assert body["results"][0]["score"] > 0.99
    assert "query_id" in body and body["latency_ms"] >= 0


def test_search_by_image_path(client, sample_products):
    _index(client, sample_products)
    # Server-side image path: seed matches the credenza's indexing seed (its image_url).
    import base64

    img = base64.b64encode(sample_products[0]["image_url"].encode()).decode()
    resp = client.post("/search", json={"store": "acme", "image": {"base64": img}, "top_k": 1})
    assert resp.status_code == 200
    assert resp.json()["results"][0]["product"]["id"] == "sku-1"


def test_in_stock_filter(client, sample_products, vector_for):
    _index(client, sample_products)
    q = vector_for(sample_products[1]["image_url"])  # the out_of_stock shoe
    resp = client.post(
        "/search",
        json={"store": "acme", "vector": q, "top_k": 10, "filters": {"in_stock_only": True}},
    )
    ids = [r["product"]["id"] for r in resp.json()["results"]]
    assert "sku-2" not in ids  # filtered out (out_of_stock)


def test_wrong_vector_dimension_rejected(client):
    resp = client.post("/search", json={"store": "acme", "vector": [0.0, 1.0]})
    assert resp.status_code == 422


def test_must_provide_vector_or_image(client):
    resp = client.post("/search", json={"store": "acme"})
    assert resp.status_code == 422
    # and not both
    resp = client.post(
        "/search",
        json={"store": "acme", "vector": [0.0] * EMBEDDING_DIM, "image": {"url": "x"}},
    )
    assert resp.status_code == 422
