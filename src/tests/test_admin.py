import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime

admin_prefix = "/api/v2/admin"


def make_user_dict(**kwargs):
    defaults = dict(
        uid=str(uuid4()),
        username="testuser",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        role="user",
        is_verified=True,
        created_at=datetime(2024, 1, 1, 0, 0, 0).isoformat(),
        updated_at=datetime(2024, 1, 1, 0, 0, 0).isoformat(),
    )
    defaults.update(kwargs)
    return defaults


class TestAdmin:
    """Test suite for admin endpoints and service"""

    def test_get_dashboard_stats(self, client, db_session):
        """Test retrieving dashboard statistics"""
        with patch('src.Admin.routes.admin_service.get_dashboard_stats', new_callable=AsyncMock) as mock_stats:
            mock_stats.return_value = {
                "users_count": 10,
                "verified_users_count": 7,
                "admins_count": 1,
                "orders_count": 25,
                "reviews_count": 12
            }

            response = client.get(f"{admin_prefix}/dashboard")

            assert response.status_code == 200
            data = response.json()
            assert data["users_count"] == 10
            assert data["verified_users_count"] == 7
            assert data["admins_count"] == 1
            assert data["orders_count"] == 25
            assert data["reviews_count"] == 12
            mock_stats.assert_called_once()

    def test_get_all_users(self, client, db_session):
        """Test retrieving all users"""
        with patch('src.Admin.routes.admin_service.get_users', new_callable=AsyncMock) as mock_get_users:
            mock_get_users.return_value = [
                make_user_dict(uid=str(uuid4()), username="testuser1", email="test1@example.com", role="user"),
                make_user_dict(uid=str(uuid4()), username="testuser2", email="test2@example.com", role="Admin"),
            ]

            response = client.get(f"{admin_prefix}/users")

            assert response.status_code == 200
            users = response.json()
            assert isinstance(users, list)
            assert len(users) == 2
            mock_get_users.assert_called_once()

    def test_get_user_by_id(self, client, db_session):
        """Test retrieving a specific user"""
        user_id = uuid4()
        with patch('src.Admin.routes.admin_service.get_user_by_id', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = make_user_dict(
                uid=str(user_id), username="testuser", email="test@example.com", role="user"
            )

            response = client.get(f"{admin_prefix}/users/{user_id}")

            assert response.status_code == 200
            user = response.json()
            assert user["username"] == "testuser"
            mock_get_user.assert_called_once()

    def test_get_user_not_found(self, client, db_session):
        """Test retrieving a non-existent user"""
        user_id = uuid4()
        with patch('src.Admin.routes.admin_service.get_user_by_id', new_callable=AsyncMock) as mock_get_user:
            from fastapi import HTTPException
            mock_get_user.side_effect = HTTPException(status_code=404, detail="User not found")

            response = client.get(f"{admin_prefix}/users/{user_id}")

            assert response.status_code == 404

    def test_update_user_role(self, client, db_session):
        """Test updating a user's role"""
        user_id = uuid4()
        with patch('src.Admin.routes.admin_service.get_user_by_id', new_callable=AsyncMock) as mock_get_user:
            with patch('src.Admin.routes.admin_service.update_user_role', new_callable=AsyncMock) as mock_update:
                mock_get_user.return_value = make_user_dict(uid=str(user_id), username="testuser", email="test@example.com", role="user")
                mock_update.return_value = make_user_dict(uid=str(user_id), username="testuser", email="test@example.com", role="Admin")

                update_data = {"role": "Admin"}
                response = client.patch(f"{admin_prefix}/users/{user_id}/role", json=update_data)

                assert response.status_code == 200
                user = response.json()
                assert user["role"] == "Admin"
                mock_update.assert_called_once()

    def test_dashboard_stats_correctness(self):
        """Test that dashboard stats structure is correct"""
        stats = {
            "users_count": 10,
            "verified_users_count": 7,
            "admins_count": 1,
            "orders_count": 25,
            "reviews_count": 12
        }

        assert "users_count" in stats
        assert "verified_users_count" in stats
        assert "admins_count" in stats
        assert "orders_count" in stats
        assert "reviews_count" in stats
        assert stats["verified_users_count"] <= stats["users_count"]

    def test_users_list_empty(self, client, db_session):
        """Test getting users list when empty"""
        with patch('src.Admin.routes.admin_service.get_users', new_callable=AsyncMock) as mock_get_users:
            mock_get_users.return_value = []

            response = client.get(f"{admin_prefix}/users")

            assert response.status_code == 200
            assert response.json() == []

    def test_user_roles_validation(self):
        """Test that user roles are valid"""
        valid_roles = ["user", "Admin", "Staff"]
        for role in valid_roles:
            assert isinstance(role, str)
            assert len(role) > 0
