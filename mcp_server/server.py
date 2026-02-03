from __future__ import annotations

import logging
import os
from fastmcp import FastMCP

from .storage import ProductStore


DATA_PATH = os.environ.get("PRODUCTS_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "products.json"))

store = ProductStore(os.path.abspath(DATA_PATH))

mcp = FastMCP("ProductMCP")
logger = logging.getLogger(__name__)


@mcp.tool()
def list_products() -> list[dict]:
    """Return all available products."""
    logger.info("list_products called")
    return store.list_products()


@mcp.tool()
def get_product(product_id: int) -> dict:
    """Return a single product by ID.

    Raises:
        ValueError: If the product is not found.
    """
    logger.info("get_product called id=%s", product_id)
    return store.get_product(product_id)


@mcp.tool()
def add_product(name: str, price: float, category: str, in_stock: bool = True) -> dict:
    """Add a new product and return it."""
    logger.info("add_product called name=%s price=%s category=%s in_stock=%s", name, price, category, in_stock)
    return store.add_product(name=name, price=price, category=category, in_stock=in_stock)


@mcp.tool()
def get_statistics() -> dict:
    """Return product statistics (count and average price)."""
    logger.info("get_statistics called")
    return store.get_statistics()


if __name__ == "__main__":
    # FastMCP uses stdio transport by default for CLI execution.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    mcp.run()
