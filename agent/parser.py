from __future__ import annotations

import re
from typing import Any, Dict


def parse_query(query: str) -> Dict[str, Any]:
    original = query.strip()
    lowered = original.lower()

    if any(token in lowered for token in ["средн", "average", "статист"]):
        return {"action": "get_statistics"}

    if any(token in lowered for token in ["добав", "add"]):
        name_match = re.search(r"продукт\s*[:\-]?\s*([^,]+)", original, re.IGNORECASE)
        price_match = re.search(r"цен[ауы]?\s*([0-9]+(?:[\.,][0-9]+)?)", original, re.IGNORECASE)
        category_match = re.search(r"категори[яи]\s*([^,]+)", original, re.IGNORECASE)

        name = name_match.group(1).strip() if name_match else "Новый продукт"
        price = float(price_match.group(1).replace(",", ".")) if price_match else 0.0
        category = category_match.group(1).strip() if category_match else "Без категории"

        return {
            "action": "add_product",
            "name": name,
            "price": price,
            "category": category,
            "in_stock": True,
        }

    if any(token in lowered for token in ["скидк", "discount"]):
        percent_match = re.search(r"([0-9]+(?:[\.,][0-9]+)?)\s*%", lowered)
        id_match = re.search(r"id\s*(\d+)", lowered)
        percent = float(percent_match.group(1).replace(",", ".")) if percent_match else 0.0
        product_id = int(id_match.group(1)) if id_match else None
        return {
            "action": "discount",
            "percent": percent,
            "product_id": product_id,
        }

    if any(token in lowered for token in ["покаж", "list", "продукт"]):
        category_match = re.search(r"категори[яи]\s*([^,]+)", original, re.IGNORECASE)
        category = category_match.group(1).strip() if category_match else None
        return {"action": "list_products", "category": category}

    id_match = re.search(r"id\s*(\d+)", lowered)
    if id_match:
        return {"action": "get_product", "product_id": int(id_match.group(1))}

    return {"action": "unknown"}
