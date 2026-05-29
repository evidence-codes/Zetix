from __future__ import annotations

from zetix_api.ingest import parse_csv, parse_json
from zetix_api.schemas import Availability, Product

CSV_TEXT = (
    "id,title,description,price,currency,availability,image_url,product_url,store,category\n"
    "sku-1,Credenza,Walnut sideboard,899.0,USD,in_stock,"
    "https://s.example/c.jpg,https://s.example/p/c,acme,furniture\n"
    "sku-2,Teal shoe,,120.5,USD,out_of_stock,"
    "https://s.example/s.jpg,https://s.example/p/s,acme,footwear\n"
)


def test_parse_csv_from_string() -> None:
    products = parse_csv(CSV_TEXT)
    assert [p.id for p in products] == ["sku-1", "sku-2"]
    assert all(isinstance(p, Product) for p in products)

    first = products[0]
    assert first.title == "Credenza"
    assert first.description == "Walnut sideboard"
    assert first.price == 899.0
    assert first.currency == "USD"
    assert first.availability is Availability.in_stock
    assert first.category == "furniture"

    # Empty description normalises to None; availability maps to the enum.
    assert products[1].description is None
    assert products[1].availability is Availability.out_of_stock


def test_parse_csv_from_path(tmp_path) -> None:
    csv_file = tmp_path / "catalog.csv"
    csv_file.write_text(CSV_TEXT, encoding="utf-8")
    products = parse_csv(str(csv_file))
    assert len(products) == 2
    assert products[0].id == "sku-1"


def test_parse_csv_from_bytes_skips_blank_rows() -> None:
    raw = (CSV_TEXT + ",,,,,,,,,\n").encode("utf-8")
    products = parse_csv(raw)
    assert [p.id for p in products] == ["sku-1", "sku-2"]


def test_parse_json_list() -> None:
    data = [
        {
            "id": "sku-1",
            "title": "Credenza",
            "price": 899.0,
            "currency": "USD",
            "availability": "in_stock",
            "product_url": "https://s.example/p/c",
            "store": "acme",
        },
        {
            "id": "sku-2",
            "title": "Teal shoe",
            "price": 120.5,
            "currency": "USD",
            "product_url": "https://s.example/p/s",
            "store": "acme",
        },
    ]
    products = parse_json(data)
    assert [p.id for p in products] == ["sku-1", "sku-2"]
    assert products[0].availability is Availability.in_stock
    # Default availability when omitted.
    assert products[1].availability is Availability.unknown


def test_parse_json_products_envelope_and_string() -> None:
    import json

    payload = {
        "products": [
            {
                "id": "sku-9",
                "title": "Lamp",
                "price": 49.0,
                "currency": "USD",
                "product_url": "https://s.example/p/l",
                "store": "acme",
            }
        ]
    }
    from_dict = parse_json(payload)
    from_str = parse_json(json.dumps(payload))
    assert from_dict[0].id == from_str[0].id == "sku-9"
    assert isinstance(from_dict[0], Product)
