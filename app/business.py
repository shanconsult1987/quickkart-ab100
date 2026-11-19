import json

from app.config import DATA_DIR


def get_orders():
    path = DATA_DIR / "orders.json"

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_order(order_id):
    for order in get_orders():
        if order["order_id"] == order_id:
            return order

    return None


def get_order_context(order_id):
    order = get_order(order_id)

    if order is None:
        raise ValueError(f"Order {order_id} was not found.")

    return {
        "order_id": order["order_id"],
        "status": order["status"],
        "payment_status": order["payment_status"],
        "inventory_status": order["inventory_status"],
        "delivery_minutes": order["delivery_minutes"],
        "issue": order["issue"],
        "region": order["region"],
    }