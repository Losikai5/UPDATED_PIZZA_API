import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.Orders.schemas import OrderCreate, OrderUpdate
import uuid
from datetime import datetime

orders_prefix = "/api/v2/orders"


def make_order_dict(**kwargs):
    defaults = dict(
        uid=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        quantity=2,
        order_status="pending",
        pizza_size="medium",
        flavour="pepperoni",
        total_price=25.99,
        placed_at=datetime(2024, 1, 1, 12, 0, 0).isoformat(),
    )
    defaults.update(kwargs)
    return defaults


class TestOrders:
    """Test suite for order endpoints"""

    def test_get_all_orders_success(self, client, db_session):
        """Test getting all orders"""
        with patch('src.Orders.routes.order_service.get_orders', new_callable=AsyncMock) as mock_get_orders:
            mock_get_orders.return_value = [
                make_order_dict(quantity=2, pizza_size="medium", flavour="pepperoni"),
                make_order_dict(quantity=1, order_status="completed", pizza_size="large", flavour="margherita"),
            ]

            response = client.get(f"{orders_prefix}/")

            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) == 2
            mock_get_orders.assert_called_once()

    def test_get_all_orders_empty(self, client, db_session):
        """Test getting all orders when none exist"""
        with patch('src.Orders.routes.order_service.get_orders', new_callable=AsyncMock) as mock_get_orders:
            mock_get_orders.return_value = []

            response = client.get(f"{orders_prefix}/")

            assert response.status_code == 200
            assert response.json() == []

    def test_create_order_success(self, client, db_session):
        """Test successful order creation"""
        order_data = {
            "quantity": 2,
            "pizza_size": "medium",
            "flavour": "pepperoni"
        }

        with patch('src.Orders.routes.order_service.create_order', new_callable=AsyncMock) as mock_create:
            with patch('src.Orders.routes.send_order_confirmation_task') as mock_task:
                mock_task.delay = Mock()
                mock_order = Mock()
                mock_order.uid = uuid.uuid4()
                mock_order.user_id = uuid.uuid4()
                mock_order.quantity = 2
                mock_order.order_status = "pending"
                mock_order.pizza_size = "medium"
                mock_order.flavour = "pepperoni"
                mock_order.total_price = 25.99
                mock_order.placed_at = datetime(2024, 1, 1, 12, 0, 0)
                mock_create.return_value = mock_order

                response = client.post(f"{orders_prefix}/", json=order_data)

                assert response.status_code == 200
                result = response.json()
                assert result["quantity"] == order_data["quantity"]
                assert result["pizza_size"] == order_data["pizza_size"]
                assert result["flavour"] == order_data["flavour"]
                mock_create.assert_called_once()

    def test_create_order_invalid_data(self, client, db_session):
        """Test order creation with invalid data"""
        invalid_order_data = {
            "quantity": "invalid",
            "pizza_size": "medium"
        }

        response = client.post(f"{orders_prefix}/", json=invalid_order_data)

        assert response.status_code == 422

    def test_get_order_by_id_success(self, client, db_session):
        """Test getting order by ID"""
        order_uid = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.get_order_by_id', new_callable=AsyncMock) as mock_get_order:
            mock_get_order.return_value = {
                **make_order_dict(uid=order_uid, quantity=2, pizza_size="medium", flavour="pepperoni"),
                "reviews": [],
            }

            response = client.get(f"{orders_prefix}/{order_uid}")

            assert response.status_code == 200
            result = response.json()
            assert result["quantity"] == 2
            assert result["pizza_size"] == "medium"
            mock_get_order.assert_called_once()

    def test_get_order_by_id_not_found(self, client, db_session):
        """Test getting non-existent order by ID"""
        order_uid = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.get_order_by_id', new_callable=AsyncMock) as mock_get_order:
            mock_get_order.return_value = None

            response = client.get(f"{orders_prefix}/{order_uid}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_update_order_success(self, client, db_session):
        """Test successful order update"""
        order_id = str(uuid.uuid4())
        update_data = {
            "quantity": 5,
            "order_status": "in_transit",
            "pizza_size": "large"
        }

        with patch('src.Orders.routes.order_service.update_order', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = make_order_dict(
                uid=order_id, quantity=5, order_status="in_transit", pizza_size="large"
            )

            response = client.put(f"{orders_prefix}/{order_id}", json=update_data)

            assert response.status_code == 200
            result = response.json()
            assert result["quantity"] == 5
            assert result["order_status"] == "in_transit"
            mock_update.assert_called_once()

    def test_update_order_partial(self, client, db_session):
        """Test partial order update"""
        order_id = str(uuid.uuid4())
        update_data = {
            "order_status": "in_transit"
        }

        with patch('src.Orders.routes.order_service.update_order', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = make_order_dict(uid=order_id, order_status="in_transit")

            response = client.put(f"{orders_prefix}/{order_id}", json=update_data)

            assert response.status_code == 200
            result = response.json()
            assert result["order_status"] == "in_transit"

    def test_delete_order_success(self, client, db_session):
        """Test successful order deletion"""
        order_id = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.delete_order', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {"message": "Order deleted successfully"}

            response = client.delete(f"{orders_prefix}/{order_id}")

            assert response.status_code == 200
            mock_delete.assert_called_once()

    def test_delete_order_not_found(self, client, db_session):
        """Test deleting non-existent order"""
        order_id = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.get_order_by_id', new_callable=AsyncMock) as mock_get:
            from fastapi import HTTPException
            mock_get.side_effect = HTTPException(status_code=404, detail="Order not found")

            response = client.delete(f"{orders_prefix}/{order_id}")

            assert response.status_code == 404

    def test_order_status_transitions(self, client, db_session):
        """Test order status transitions"""
        order_id = str(uuid.uuid4())
        statuses = ["pending", "in_transit", "completed", "cancelled"]

        for status in statuses:
            update_data = {"order_status": status}

            with patch('src.Orders.routes.order_service.update_order', new_callable=AsyncMock) as mock_update:
                mock_update.return_value = make_order_dict(uid=order_id, order_status=status)

                response = client.put(f"{orders_prefix}/{order_id}", json=update_data)

                assert response.status_code == 200
                assert response.json()["order_status"] == status
