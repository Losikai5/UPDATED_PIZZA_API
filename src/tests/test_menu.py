import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime

menu_prefix = "/api/v2/menu"


def make_size_dict(**kwargs):
    defaults = dict(uid=str(uuid4()), pizza_size="small", price=10.0)
    defaults.update(kwargs)
    return defaults


def make_item_dict(**kwargs):
    defaults = dict(
        uid=str(uuid4()),
        name="Margherita",
        flavour="tomato_cheese",
        description="Classic pizza",
        is_available=True,
        created_at=datetime.now().isoformat(),
        sizes=[],
    )
    defaults.update(kwargs)
    return defaults


class TestMenu:
    """Test suite for menu endpoints and service"""

    def test_get_all_menu_items(self, client, db_session):
        """Test retrieving all menu items"""
        with patch('src.Menu.routes.menu_service.get_menu_items', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                make_item_dict(),
                make_item_dict(name="Pepperoni", flavour="pepperoni"),
            ]

            response = client.get(f"{menu_prefix}/")

            assert response.status_code == 200

    def test_get_menu_item_by_id(self, client, db_session):
        """Test retrieving a specific menu item"""
        item_id = str(uuid4())
        with patch('src.Menu.routes.menu_service.get_menu_item_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = make_item_dict(uid=item_id)

            response = client.get(f"{menu_prefix}/{item_id}")

            assert response.status_code == 200
            mock_get.assert_called_once()

    def test_get_menu_item_not_found(self, client, db_session):
        """Test retrieving non-existent menu item"""
        item_id = str(uuid4())
        with patch('src.Menu.routes.menu_service.get_menu_item_by_id', new_callable=AsyncMock) as mock_get:
            from fastapi import HTTPException
            mock_get.side_effect = HTTPException(status_code=404, detail="Menu item not found")

            response = client.get(f"{menu_prefix}/{item_id}")

            assert response.status_code == 404

    def test_create_menu_item(self, client, db_session):
        """Test creating a new menu item"""
        with patch('src.Menu.routes.menu_service.create_menu_item', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = make_item_dict(
                name="New Pizza",
                flavour="custom",
                description="A custom pizza",
                sizes=[
                    make_size_dict(pizza_size="small", price=10.0),
                    make_size_dict(pizza_size="large", price=15.0),
                ],
            )

            menu_data = {
                "name": "New Pizza",
                "flavour": "custom",
                "description": "A custom pizza",
                "sizes": [
                    {"pizza_size": "small", "price": 10.0},
                    {"pizza_size": "large", "price": 15.0},
                ],
            }

            response = client.post(f"{menu_prefix}/", json=menu_data)

            assert response.status_code == 201
            mock_create.assert_called_once()

    def test_update_menu_item(self, client, db_session):
        """Test updating a menu item"""
        item_id = str(uuid4())
        with patch('src.Menu.routes.menu_service.update_menu_item', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = make_item_dict(
                uid=item_id,
                name="Updated Pizza",
                description="Updated description",
                is_available=False,
            )

            update_data = {
                "name": "Updated Pizza",
                "description": "Updated description",
                "is_available": False,
            }

            response = client.patch(f"{menu_prefix}/{item_id}", json=update_data)

            assert response.status_code == 200
            mock_update.assert_called_once()

    def test_delete_menu_item(self, client, db_session):
        """Test deleting a menu item"""
        item_id = str(uuid4())
        with patch('src.Menu.routes.menu_service.delete_menu_item', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {"message": "Menu item deleted successfully"}

            response = client.delete(f"{menu_prefix}/{item_id}")

            assert response.status_code == 200
            mock_delete.assert_called_once()

    def test_menu_item_availability(self, client, db_session):
        """Test toggling menu item availability"""
        item_id = str(uuid4())
        with patch('src.Menu.routes.menu_service.toggle_availability', new_callable=AsyncMock) as mock_toggle:
            mock_toggle.return_value = make_item_dict(uid=item_id, is_available=False)

            response = client.patch(f"{menu_prefix}/{item_id}/toggle-availability")

            assert response.status_code == 200

    def test_menu_item_sizes(self, client, db_session):
        """Test that menu items have multiple sizes"""
        with patch('src.Menu.routes.menu_service.create_menu_item', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = make_item_dict(
                sizes=[
                    make_size_dict(pizza_size="small", price=10.0),
                    make_size_dict(pizza_size="medium", price=12.0),
                    make_size_dict(pizza_size="large", price=15.0),
                    make_size_dict(pizza_size="extra_large", price=18.0),
                ]
            )

            menu_data = {
                "name": "Pizza",
                "flavour": "test",
                "description": "Test",
                "sizes": [
                    {"pizza_size": "small", "price": 10.0},
                    {"pizza_size": "medium", "price": 12.0},
                    {"pizza_size": "large", "price": 15.0},
                    {"pizza_size": "extra_large", "price": 18.0},
                ],
            }

            response = client.post(f"{menu_prefix}/", json=menu_data)

            assert response.status_code == 201

    def test_menu_empty_list(self, client, db_session):
        """Test retrieving menu when no items exist"""
        with patch('src.Menu.routes.menu_service.get_menu_items', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            response = client.get(f"{menu_prefix}/")

            assert response.status_code == 200
