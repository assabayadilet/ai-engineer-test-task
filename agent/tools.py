from __future__ import annotations

import ast
from typing import Any


_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Num,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
)


def _validate_expression(node: ast.AST) -> None:
    for child in ast.walk(node):
        if not isinstance(child, _ALLOWED_NODES):
            raise ValueError("Unsupported expression")


def calculator(expression: str) -> float:
    """Safely evaluate a basic arithmetic expression."""
    parsed = ast.parse(expression, mode="eval")
    _validate_expression(parsed)
    return float(eval(compile(parsed, "<calculator>", "eval"), {"__builtins__": {}}, {}))


def formatter(text: str, style: str = "plain") -> str:
    """Format text with a simple style transform."""
    value = str(text)
    style = style.lower()
    if style == "upper":
        return value.upper()
    if style == "lower":
        return value.lower()
    if style == "title":
        return value.title()
    if style == "currency":
        try:
            number = float(value)
            return f"{number:,.2f} RUB".replace(",", " ")
        except ValueError:
            return value
    return value


def format_products(products: list[dict[str, Any]]) -> str:
    """Human-readable product list."""
    if not products:
        return "Нет продуктов по заданным условиям."

    lines = []
    for item in products:
        status = "в наличии" if item.get("in_stock") else "нет в наличии"
        lines.append(
            f"ID {item.get('id')}: {item.get('name')} | {item.get('category')} | "
            f"{item.get('price')} | {status}"
        )
    return "\n".join(lines)
