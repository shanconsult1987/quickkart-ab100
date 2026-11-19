from app.business import get_order_context


def get_order_status(order_id: str) -> dict:
    """
    Read-only tool that retrieves the current QuickKart order status.
    """
    return get_order_context(order_id)


def get_payment_status(order_id: str) -> dict:
    """
    Read-only tool that retrieves payment status.
    """
    order = get_order_context(order_id)

    return {
        "order_id": order_id,
        "payment_status": order["payment_status"],
    }


def get_inventory_status(order_id: str) -> dict:
    """
    Read-only tool that retrieves inventory status.
    """
    order = get_order_context(order_id)

    return {
        "order_id": order_id,
        "inventory_status": order["inventory_status"],
    }