from __future__ import annotations

import json

from mcp_server.storage import ProductStore, Product


def _empty_store(tmp_path):
    file_path = tmp_path / "products.json"
    file_path.write_text("[]", encoding="utf-8")
    return ProductStore(str(file_path))


def test_store_add_and_get(tmp_path):
    store = _empty_store(tmp_path)
    created = store.add_product(name="Мышка", price=1500, category="Электроника", in_stock=True)
    fetched = store.get_product(created["id"])
    assert fetched["name"] == "Мышка"
    assert fetched["price"] == 1500


def test_store_statistics(tmp_path):
    store = _empty_store(tmp_path)
    store.seed([
        Product(id=1, name="A", price=100, category="C", in_stock=True),
        Product(id=2, name="B", price=300, category="C", in_stock=False),
    ])
    stats = store.get_statistics()
    assert stats["count"] == 2
    assert stats["average_price"] == 200
