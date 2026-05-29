"""Shopify ingestion adapter (EPIC-1, task 1.A.4).

Fetches products from the Shopify Admin REST API (version 2024-01) and maps each
product/variant pair onto :class:`Product`. ``httpx`` is imported lazily so the
adapter only pulls the ``[ingest]`` extra when actually used; tests inject a fake
transport/client so no network I/O occurs.

Mapping notes
-------------
- One Zetix product is emitted per Shopify *variant* (variants carry price and
  inventory), keyed ``"<product_id>:<variant_id>"`` so SKUs stay unique.
- Single-variant products keep the bare product id for a clean deep link.
- ``availability`` is derived from inventory/availability fields, never PII.
"""

from __future__ import annotations

from typing import Any

from ..schemas import Availability, Product

_API_VERSION = "2024-01"


def _build_client(shop_domain: str, token: str, transport: Any | None):
    # Lazy import: only require httpx ([ingest] extra) when the adapter runs.
    import httpx

    base_url = f"https://{shop_domain}/admin/api/{_API_VERSION}"
    headers = {
        "X-Shopify-Access-Token": token,
        "Accept": "application/json",
    }
    return httpx.Client(base_url=base_url, headers=headers, transport=transport, timeout=30.0)


def _variant_availability(variant: dict[str, Any]) -> Availability:
    policy = (variant.get("inventory_policy") or "").lower()
    qty = variant.get("inventory_quantity")
    if qty is not None and qty > 0:
        return Availability.in_stock
    # "continue" means the store keeps selling when out of stock.
    if policy == "continue":
        return Availability.preorder
    if qty is not None and qty <= 0:
        return Availability.out_of_stock
    return Availability.unknown


def _first_image_url(product: dict[str, Any]) -> str | None:
    image = product.get("image") or {}
    if image.get("src"):
        return image["src"]
    images = product.get("images") or []
    if images and images[0].get("src"):
        return images[0]["src"]
    return None


def _map_variant(
    product: dict[str, Any],
    variant: dict[str, Any],
    store: str,
    shop_domain: str,
    single_variant: bool,
) -> Product:
    product_id = str(product.get("id", ""))
    variant_id = str(variant.get("id", ""))
    sku = product_id if single_variant else f"{product_id}:{variant_id}"

    title = product.get("title", "")
    if not single_variant and variant.get("title") and variant["title"] != "Default Title":
        title = f"{title} - {variant['title']}"

    handle = product.get("handle") or product_id
    product_url = f"https://{shop_domain}/products/{handle}"

    price_raw = variant.get("price")
    price = float(price_raw) if price_raw not in (None, "") else 0.0

    attributes = {
        "shopify_product_id": product_id,
        "shopify_variant_id": variant_id,
        "vendor": product.get("vendor"),
        "tags": product.get("tags"),
        "sku": variant.get("sku"),
    }
    # Drop empty attribute values to keep snapshots tidy.
    attributes = {k: v for k, v in attributes.items() if v not in (None, "")}

    return Product(
        id=sku,
        title=title,
        description=product.get("body_html") or None,
        price=price,
        currency=variant.get("currency") or product.get("currency") or "USD",
        availability=_variant_availability(variant),
        image_url=_first_image_url(product),
        product_url=product_url,
        store=store,
        category=product.get("product_type") or None,
        attributes=attributes or None,
    )


def _map_product(product: dict[str, Any], store: str, shop_domain: str) -> list[Product]:
    variants = product.get("variants") or [{}]
    single = len(variants) == 1
    return [_map_variant(product, v, store, shop_domain, single) for v in variants]


def fetch_shopify(
    shop_domain: str,
    token: str,
    store: str,
    *,
    transport: Any | None = None,
) -> list[Product]:
    """Fetch and map a Shopify catalog into a list of products.

    Parameters
    ----------
    shop_domain:
        The ``*.myshopify.com`` domain (no scheme).
    token:
        Admin API access token (``X-Shopify-Access-Token``).
    store:
        The Zetix store namespace to tag each product with.
    transport:
        Optional ``httpx`` transport for dependency injection in tests; when
        supplied no real network request is made.
    """
    products: list[Product] = []
    with _build_client(shop_domain, token, transport) as client:
        resp = client.get("/products.json", params={"limit": 250})
        resp.raise_for_status()
        payload = resp.json()
        for product in payload.get("products", []):
            products.extend(_map_product(product, store, shop_domain))
    return products
