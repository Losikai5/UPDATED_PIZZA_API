import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.Orders.schemas import OrderCreate, OrderUpdate
import uuid
from datetime import datetime

orders_prefix = "/api/v2/orders"


class TestOrders:
    """Test suite for order endpoints"""

    @pytest.mark.asyncio
    async def test_get_all_orders_success(self, client, db_session):
        """Test getting all orders"""
        with patch('src.Orders.routes.order_service.Get_orders', new_callable=AsyncMock) as mock_get_orders:
            # Mock orders list
            mock_order1 = Mock()
            mock_order1.uid = uuid.uuid4()
            mock_order1.Quantity = 2
            mock_order1.Order_status = "pending"
            mock_order1.pizza_size = "medium"
            mock_order1.flavour = "pepperoni"
            mock_order1.placed_at = datetime.now()

            mock_order2 = Mock()
            mock_order2.uid = uuid.uuid4()
            mock_order2.Quantity = 1
            mock_order2.Order_status = "completed"
            mock_order2.pizza_size = "large"
            mock_order2.flavour = "margherita"
            mock_order2.placed_at = datetime.now()

            mock_get_orders.return_value = [mock_order1, mock_order2]

            response = client.get(f"{orders_prefix}/")

            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) == 2
            mock_get_orders.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_orders_empty(self, client, db_session):
        """Test getting all orders when none exist"""
        with patch('src.Orders.routes.order_service.Get_orders', new_callable=AsyncMock) as mock_get_orders:
            mock_get_orders.return_value = []

            response = client.get(f"{orders_prefix}/")

            assert response.status_code == 200
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_order_success(self, client, db_session):
        """Test successful order creation"""
        order_data = {
            "Quantity": 2,
            "Order_status": "pending",
            "pizza_size": "medium",
            "flavour": "pepperoni"
        }

        with patch('src.Orders.routes.order_service.create_order', new_callable=AsyncMock) as mock_create:
            # Mock created order
            mock_order = Mock()
            mock_order.uid = uuid.uuid4()
            mock_order.Quantity = order_data["Quantity"]
            mock_order.Order_status = order_data["Order_status"]
            mock_order.pizza_size = order_data["pizza_size"]
            mock_order.flavour = order_data["flavour"]
            mock_order.placed_at = datetime.now()
            mock_create.return_value = mock_order

            response = client.post(f"{orders_prefix}/", json=order_data)

            assert response.status_code == 200
            result = response.json()
            assert result["Quantity"] == order_data["Quantity"]
            assert result["pizza_size"] == order_data["pizza_size"]
            assert result["flavour"] == order_data["flavour"]
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_order_invalid_data(self, client, db_session):
        """Test order creation with invalid data"""
        invalid_order_data = {
            "Quantity": "invalid",  # Should be int
            "Order_status": "pending",
            "pizza_size": "medium"
            # Missing flavour field
        }

        response = client.post(f"{orders_prefix}/", json=invalid_order_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_order_by_id_success(self, client, db_session):
        """Test getting order by ID"""
        order_uid = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.Get_order_by_id', new_callable=AsyncMock) as mock_get_order:
            # Mock order
            mock_order = Mock()
            mock_order.uid = order_uid
            mock_order.Quantity = 2
            mock_order.Order_status = "pending"
            mock_order.pizza_size = "medium"
            mock_order.flavour = "pepperoni"
            mock_order.placed_at = datetime.now()
            mock_get_order.return_value = mock_order

            response = client.get(f"{orders_prefix}/{order_uid}")

            assert response.status_code == 200
            result = response.json()
            assert result["Quantity"] == 2
            assert result["pizza_size"] == "medium"
            mock_get_order.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self, client, db_session):
        """Test getting non-existent order by ID"""
        order_uid = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.Get_order_by_id', new_callable=AsyncMock) as mock_get_order:
            mock_get_order.return_value = None

            response = client.get(f"{orders_prefix}/{order_uid}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_order_success(self, client, db_session):
        """Test successful order update"""
        order_id = str(uuid.uuid4())
        update_data = {
            "Quantity": 5,
            "Order_status": "in_transit",
            "pizza_size": "large"
        }

        with patch('src.Orders.routes.order_service.update_order', new_callable=AsyncMock) as mock_update:
            # Mock updated order
            mock_order = Mock()
            mock_order.uid = order_id
            mock_order.Quantity = update_data["Quantity"]
            mock_order.Order_status = update_data["Order_status"]
            mock_order.pizza_size = update_data["pizza_size"]
            mock_order.flavour = "pepperoni"
            mock_order.placed_at = datetime.now()
            mock_update.return_value = mock_order

            response = client.put(f"{orders_prefix}/{order_id}", json=update_data)

            assert response.status_code == 200
            result = response.json()
            assert result["Quantity"] == update_data["Quantity"]
            assert result["Order_status"] == update_data["Order_status"]
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_partial(self, client, db_session):
        """Test partial order update"""
        order_id = str(uuid.uuid4())
        update_data = {
            "Order_status": "delivered"
        }

        with patch('src.Orders.routes.order_service.update_order', new_callable=AsyncMock) as mock_update:
            # Mock updated order
            mock_order = Mock()
            mock_order.uid = order_id
            mock_order.Quantity = 2
            mock_order.Order_status = update_data["Order_status"]
            mock_order.pizza_size = "medium"
            mock_order.flavour = "pepperoni"
            mock_order.placed_at = datetime.now()
            mock_update.return_value = mock_order

            response = client.put(f"{orders_prefix}/{order_id}", json=update_data)

            assert response.status_code == 200
            result = response.json()
            assert result["Order_status"] == "delivered"

    @pytest.mark.asyncio
    async def test_delete_order_success(self, client, db_session):
        """Test successful order deletion"""
        order_id = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.delete_order', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {"message": "Order deleted successfully"}

            response = client.delete(f"{orders_prefix}/{order_id}")

            assert response.status_code == 200
            mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_order_not_found(self, client, db_session):
        """Test deleting non-existent order"""
        order_id = str(uuid.uuid4())

        with patch('src.Orders.routes.order_service.delete_order', new_callable=AsyncMock) as mock_delete:
            from fastapi import HTTPException
            mock_delete.side_effect = HTTPException(status_code=404, detail="Order not found")

            response = client.delete(f"{orders_prefix}/{order_id}")

            # The exception should be caught and returned as 404
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_order_status_transitions(self, client, db_session):
        """Test order status transitions"""
        order_id = str(uuid.uuid4())
        statuses = ["pending", "preparing", "in_transit", "delivered"]

        for status in statuses:
            update_data = {"Order_status": status}

            with patch('src.Orders.routes.order_service.update_order', new_callable=AsyncMock) as mock_update:
                mock_order = Mock()
                mock_order.uid = order_id
                mock_order.Quantity = 2
                mock_order.Order_status = status
                mock_order.pizza_size = "medium"
                mock_order.flavour = "pepperoni"
                mock_order.placed_at = datetime.now()
                mock_update.return_value = mock_order

                response = client.put(f"{orders_prefix}/{order_id}", json=update_data)

                assert response.status_code == 200
                assert response.json()["Order_status"] == status
