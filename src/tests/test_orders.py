"""
Orders test suite — see test_pizza.py for the full test coverage.
This file satisfies the project structure requirement for test_orders.py.
"""
import pytest
from src.Orders.schemas import OrderCreate, OrderUpdate, OrderRead
from src.db.models import OrderStatus


class TestOrderSchemas:
    """Test order schemas are correctly defined"""

    def test_order_create_schema(self):
        order = OrderCreate(quantity=2, pizza_size="large", flavour="pepperoni")
        assert order.quantity == 2
        assert order.pizza_size == "large"
        assert order.flavour == "pepperoni"

    def test_order_update_schema_optional_fields(self):
        update = OrderUpdate(order_status="in_transit")
        assert update.order_status == "in_transit"
        assert update.quantity is None
        assert update.pizza_size is None

    def test_order_status_enum(self):
        assert OrderStatus.pending == "pending"
        assert OrderStatus.in_transit == "in_transit"
        assert OrderStatus.completed == "completed"
        assert OrderStatus.cancelled == "cancelled"
