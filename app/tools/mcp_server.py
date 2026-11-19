from mcp.server.fastmcp import FastMCP

from app.tools.order_tools import (
    get_order_status,
    get_payment_status,
    get_inventory_status,
)

mcp = FastMCP("QuickKart Operations Tools")


@mcp.tool()
def lookup_order(order_id: str) -> dict:
    """
    Retrieve read-only order details.
    """
    return get_order_status(order_id)


@mcp.tool()
def lookup_payment(order_id: str) -> dict:
    """
    Retrieve read-only payment status.
    """
    return get_payment_status(order_id)


@mcp.tool()
def lookup_inventory(order_id: str) -> dict:
    """
    Retrieve read-only inventory status.
    """
    return get_inventory_status(order_id)


if __name__ == "__main__":
    mcp.run()