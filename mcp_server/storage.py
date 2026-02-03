from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: float
    category: str
    in_stock: bool


class ProductStore:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._products: list[Product] = []
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._file_path):
            self._products = [
                Product(id=1, name="Ноутбук", price=50000, category="Электроника", in_stock=True),
                Product(id=2, name="Смартфон", price=30000, category="Электроника", in_stock=True),
                Product(id=3, name="Кофемашина", price=12000, category="Бытовая техника", in_stock=False),
            ]
            self._next_id = 4
            self._save()
            return

        with open(self._file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._products = [Product(**item) for item in data]
        self._next_id = (max((p.id for p in self._products), default=0) + 1)

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        data = [asdict(p) for p in self._products]
        directory = os.path.dirname(self._file_path)
        with tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, self._file_path)

    def list_products(self) -> list[dict]:
        return [asdict(p) for p in self._products]

    def get_product(self, product_id: int) -> dict:
        for product in self._products:
            if product.id == product_id:
                return asdict(product)
        raise ValueError(f"Product with id={product_id} not found")

    def add_product(self, name: str, price: float, category: str, in_stock: bool = True) -> dict:
        product = Product(
            id=self._next_id,
            name=name,
            price=price,
            category=category,
            in_stock=in_stock,
        )
        self._next_id += 1
        self._products.append(product)
        self._save()
        return asdict(product)

    def get_statistics(self) -> dict:
        count = len(self._products)
        avg = sum(p.price for p in self._products) / count if count else 0.0
        return {"count": count, "average_price": avg}

    def seed(self, items: Iterable[Product]) -> None:
        self._products = list(items)
        self._next_id = max((p.id for p in self._products), default=0) + 1
        self._save()
