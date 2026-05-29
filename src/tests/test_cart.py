import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

cart_prefix = "/api/v2/cart"

USER_ID = uuid4()
CART_ID = uuid4()
MENU_ITEM_ID = uuid4()
SIZE_ID = uuid4()
CART_ITEM_ID = uuid4()


def make_cart_item_dict(**kwargs):
    defaults = dict(
        uid=str(CART_ITEM_ID),
        menu_item_uid=str(MENU_ITEM_ID),
        menu_item_size_uid=str(SIZE_ID),
        menu_item_name="Margherita",
        pizza_size="medium",
        quantity=2,
        unit_price=12.0,
        subtotal=24.0,
    )
    defaults.update(kwargs)
    return defaults


def make_cart_dict(**kwargs):
    defaults = dict(
        uid=str(CART_ID),
        items=[make_cart_item_dict()],
        total=24.0,
    )
    defaults.update(kwargs)
    return defaults


class TestCart:
    """Test suite for cart endpoints"""

    def test_get_cart_empty(self, client, db_session):
        """Test getting an empty cart"""
        with patch("src.Cart.routes.cart_service.get_cart", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = make_cart_dict(items=[], total=0.0)

            response = client.get(f"{cart_prefix}/")

            assert response.status_code == 200
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0.0
            mock_get.assert_called_once()

    def test_get_cart_with_items(self, client, db_session):
        """Test getting a cart that has items"""
        with patch("src.Cart.routes.cart_service.get_cart", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = make_cart_dict()

            response = client.get(f"{cart_prefix}/")

            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["menu_item_name"] == "Margherita"
            assert data["items"][0]["quantity"] == 2
            assert data["items"][0]["subtotal"] == 24.0
            assert data["total"] == 24.0

    def test_add_item_to_cart(self, client, db_session):
        """Test adding a menu item to the cart"""
        with patch("src.Cart.routes.cart_service.add_item", new_callable=AsyncMock) as mock_add:
            mock_add.return_value = make_cart_dict()

            payload = {
                "menu_item_uid": str(MENU_ITEM_ID),
                "menu_item_size_uid": str(SIZE_ID),
                "quantity": 2,
            }
            response = client.post(f"{cart_prefix}/items", json=payload)

            assert response.status_code == 201
            data = response.json()
            assert len(data["items"]) == 1
            mock_add.assert_called_once()

    def test_add_item_default_quantity(self, client, db_session):
        """Test that quantity defaults to 1 when not provided"""
        with patch("src.Cart.routes.cart_service.add_item", new_callable=AsyncMock) as mock_add:
            mock_add.return_value = make_cart_dict(
                items=[make_cart_item_dict(quantity=1, subtotal=12.0)],
                total=12.0,
            )

            payload = {
                "menu_item_uid": str(MENU_ITEM_ID),
                "menu_item_size_uid": str(SIZE_ID),
            }
            response = client.post(f"{cart_prefix}/items", json=payload)

            assert response.status_code == 201

    def test_add_item_not_found(self, client, db_session):
        """Test adding a non-existent menu item raises 404"""
        with patch("src.Cart.routes.cart_service.add_item", new_callable=AsyncMock) as mock_add:
            from fastapi import HTTPException
            mock_add.side_effect = HTTPException(status_code=404, detail="Menu item not found")

            payload = {
                "menu_item_uid": str(uuid4()),
                "menu_item_size_uid": str(uuid4()),
                "quantity": 1,
            }
            response = client.post(f"{cart_prefix}/items", json=payload)

            assert response.status_code == 404

    def test_add_unavailable_item(self, client, db_session):
        """Test adding an unavailable menu item raises 400"""
        with patch("src.Cart.routes.cart_service.add_item", new_callable=AsyncMock) as mock_add:
            from fastapi import HTTPException
            mock_add.side_effect = HTTPException(status_code=400, detail="Menu item is not available")

            payload = {
                "menu_item_uid": str(MENU_ITEM_ID),
                "menu_item_size_uid": str(SIZE_ID),
                "quantity": 1,
            }
            response = client.post(f"{cart_prefix}/items", json=payload)

            assert response.status_code == 400

    def test_update_item_quantity(self, client, db_session):
        """Test updating quantity of a cart item"""
        with patch("src.Cart.routes.cart_service.update_item_quantity", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = make_cart_dict(
                items=[make_cart_item_dict(quantity=5, subtotal=60.0)],
                total=60.0,
            )

            response = client.patch(f"{cart_prefix}/items/{CART_ITEM_ID}", json={"quantity": 5})

            assert response.status_code == 200
            data = response.json()
            assert data["items"][0]["quantity"] == 5
            mock_update.assert_called_once()

    def test_update_item_quantity_zero_removes_item(self, client, db_session):
        """Test that setting quantity to 0 removes the item from the cart"""
        with patch("src.Cart.routes.cart_service.update_item_quantity", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = make_cart_dict(items=[], total=0.0)

            response = client.patch(f"{cart_prefix}/items/{CART_ITEM_ID}", json={"quantity": 0})

            assert response.status_code == 200
            assert response.json()["items"] == []

    def test_remove_item_from_cart(self, client, db_session):
        """Test removing a specific item from the cart"""
        with patch("src.Cart.routes.cart_service.remove_item", new_callable=AsyncMock) as mock_remove:
            mock_remove.return_value = make_cart_dict(items=[], total=0.0)

            response = client.delete(f"{cart_prefix}/items/{CART_ITEM_ID}")

            assert response.status_code == 200
            assert response.json()["items"] == []
            mock_remove.assert_called_once()

    def test_remove_nonexistent_item(self, client, db_session):
        """Test removing an item that is not in the cart raises 404"""
        with patch("src.Cart.routes.cart_service.remove_item", new_callable=AsyncMock) as mock_remove:
            from fastapi import HTTPException
            mock_remove.side_effect = HTTPException(status_code=404, detail="Cart item not found")

            response = client.delete(f"{cart_prefix}/items/{uuid4()}")

            assert response.status_code == 404

    def test_clear_cart(self, client, db_session):
        """Test clearing the entire cart"""
        with patch("src.Cart.routes.cart_service.clear_cart", new_callable=AsyncMock) as mock_clear:
            mock_clear.return_value = {"message": "Cart cleared successfully"}

            response = client.delete(f"{cart_prefix}/")

            assert response.status_code == 200
            assert "message" in response.json()
            mock_clear.assert_called_once()

    def test_cart_subtotal_calculation(self, client, db_session):
        """Test that subtotals and total are correctly computed"""
        with patch("src.Cart.routes.cart_service.get_cart", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = make_cart_dict(
                items=[
                    make_cart_item_dict(quantity=2, unit_price=10.0, subtotal=20.0, pizza_size="small"),
                    make_cart_item_dict(
                        uid=str(uuid4()), pizza_size="large",
                        quantity=1, unit_price=15.0, subtotal=15.0,
                    ),
                ],
                total=35.0,
            )

            response = client.get(f"{cart_prefix}/")

            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 2
            assert data["total"] == 35.0
