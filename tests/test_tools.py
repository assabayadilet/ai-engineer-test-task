from __future__ import annotations

from agent.tools import calculator, formatter


def test_calculator_discount():
    assert calculator("100 * (1 - 15 / 100)") == 85.0


def test_formatter_currency():
    assert formatter("1500", "currency").endswith("RUB")
