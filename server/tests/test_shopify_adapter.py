from __future__ import annotations

import json

import pytest
from zetix_api.ingest import fetch_shopify
from zetix_api.schemas import Availability

httpx = pytest.importorskip("httpx")

SHOPIFY_PAYLOAD = {
    "products": [
        {
            "id": 111,
            "title": "Mid-century credenza",
            "handle": "mid-century-credenza",
            "body_html": "<p>Walnut sideboard</p>",
            "product_type": "furniture",
            "vendor": "Acme",
            "tags": "wood, storage",
            "image": {"src": "https://cdn.shopify.test/credenza.jpg"},
            "variants": [
                {
                    "id": 555,
                    "title": "Default Title",
                    "price": "899.00",
                    "sku": "CRED-1",
                    "inventory_quantity": 4,
                    "inventory_policy": "deny",
                }
            ],
        },
        {
            "id": 222,
            "title": "Running shoe",
            "handle": "running-shoe",
            "product_type": "footwear",
            "images": [{"src": "https://cdn.shopify.test/shoe.jpg"}],
            "variants": [
                {
                    "id": 777,
                    "title": "Teal",
                    "price": "120.00",
                    "inventory_quantity": 0,
                    "inventory_policy": "deny",
                },
                {
                    "id": 778,
                    "title": "Red",
                    "price": "125.00",
                    "inventory_quantity": 0,
                    "inventory_policy": "continue",
                },
            ],
        },
    ]
}


def _handler(request: httpx.Request) -> httpx.Response:
    assert request.url.path.endswith("/products.json")
    assert request.headers["X-Shopify-Access-Token"] == "shptoken"
    return httpx.Response(200, content=json.dumps(SHOPIFY_PAYLOAD))


def test_fetch_shopify_maps_products_and_variants() -> None:
    transport = httpx.MockTransport(_handler)
    products = fetch_shopify("acme.myshopify.com", "shptoken", "acme", transport=transport)

    # Single-variant product keeps the bare product id; multi-variant gets suffixes.
    ids = [p.id for p in products]
    assert ids == ["111", "222:777", "222:778"]

    credenza = products[0]
    assert credenza.title == "Mid-century credenza"
    assert credenza.price == 899.0
    assert credenza.availability is Availability.in_stock
    assert credenza.image_url == "https://cdn.shopify.test/credenza.jpg"
    assert credenza.product_url == "https://acme.myshopify.com/products/mid-century-credenza"
    assert credenza.store == "acme"
    assert credenza.category == "furniture"
    assert credenza.attributes["shopify_variant_id"] == "555"

    teal = products[1]
    assert teal.title == "Running shoe - Teal"
    assert teal.availability is Availability.out_of_stock
    assert teal.image_url == "https://cdn.shopify.test/shoe.jpg"

    # inventory_policy "continue" with zero stock -> preorder.
    red = products[2]
    assert red.availability is Availability.preorder
    assert red.price == 125.0
