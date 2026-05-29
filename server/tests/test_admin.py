def test_full_push_then_status(client, sample_products):
    resp = client.post(
        "/admin/catalog",
        json={"store": "acme", "mode": "full", "products": sample_products},
    )
    assert resp.status_code == 202
    body = resp.json()
    assert body["accepted"] is True
    assert body["indexed_count"] == 2
    assert body["mode"] == "full"

    status = client.get("/admin/index/status", params={"store": "acme"}).json()
    assert status["product_count"] == 2
    assert status["status"] == "ready"


def test_delta_removes_product(client, sample_products):
    client.post(
        "/admin/catalog",
        json={"store": "acme", "mode": "full", "products": sample_products},
    )
    resp = client.post(
        "/admin/catalog",
        json={"store": "acme", "mode": "delta", "products": [], "removed_ids": ["sku-2"]},
    )
    assert resp.status_code == 202
    assert resp.json()["removed_count"] == 1

    status = client.get("/admin/index/status", params={"store": "acme"}).json()
    assert status["product_count"] == 1


def test_empty_store_status(client):
    status = client.get("/admin/index/status", params={"store": "nobody"}).json()
    assert status["product_count"] == 0
    assert status["status"] == "empty"
