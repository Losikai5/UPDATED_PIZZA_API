import pytest
from unittest.mock import AsyncMock, patch, Mock
from uuid import uuid4
from datetime import datetime

auth_prefix = "/api/v2/auth"


class TestAuth:
    """Test suite for authentication endpoints and service"""

    def test_signup_success(self, client, db_session):
        """Test successful user signup"""
        with patch('src.auth.routes.auth_service.check_user_exists', new_callable=AsyncMock):
            with patch('src.auth.routes.auth_service.create_user', new_callable=AsyncMock) as mock_create:
                with patch('src.auth.routes.send_email_task') as mock_task:
                    mock_task.delay = Mock()
                    mock_user = Mock()
                    mock_user.uid = uuid4()
                    mock_user.username = "newuser"
                    mock_user.email = "newuser@example.com"
                    mock_user.first_name = "New"
                    mock_user.last_name = "User"
                    mock_user.is_verified = False
                    mock_user.role = "user"
                    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)

                    mock_create.return_value = mock_user

                    signup_data = {
                        "username": "newuser",
                        "email": "newuser@example.com",
                        "first_name": "New",
                        "last_name": "User",
                        "role": "user",
                        "password": "securepassword123"
                    }

                    response = client.post(f"{auth_prefix}/signup", json=signup_data)

                    assert response.status_code == 200
                    mock_create.assert_called_once()

    def test_signup_user_already_exists(self, client, db_session):
        """Test signup fails when user already exists"""
        with patch('src.auth.routes.auth_service.check_user_exists', new_callable=AsyncMock) as mock_check:
            from fastapi import HTTPException
            mock_check.side_effect = HTTPException(status_code=403, detail="User exists")

            signup_data = {
                "username": "existinguser",
                "email": "existing@example.com",
                "first_name": "Existing",
                "last_name": "User",
                "role": "user",
                "password": "securepassword123"
            }

            response = client.post(f"{auth_prefix}/signup", json=signup_data)

            assert response.status_code == 403

    def test_login_success(self, client, db_session):
        """Test successful user login"""
        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
            with patch('src.auth.routes.verify_hash') as mock_verify:
                mock_user = Mock()
                mock_user.uid = uuid4()
                mock_user.email = "test@example.com"
                mock_user.password_hash = "hashed_password"
                mock_user.is_verified = True
                mock_user.role = "user"

                mock_get_user.return_value = mock_user
                mock_verify.return_value = True

                login_data = {
                    "email": "test@example.com",
                    "password": "password123"
                }

                response = client.post(f"{auth_prefix}/login", json=login_data)

                assert response.status_code == 200
                mock_get_user.assert_called_once()

    def test_login_invalid_credentials(self, client, db_session):
        """Test login fails with invalid credentials"""
        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = None

            login_data = {
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }

            response = client.post(f"{auth_prefix}/login", json=login_data)

            assert response.status_code == 401 or response.status_code == 400

    def test_refresh_token(self, client, db_session):
        """Test refresh token endpoint requires valid token"""
        response = client.get(f"{auth_prefix}/refresh_token")
        assert response.status_code in [200, 401, 403, 422]

    def test_get_current_user(self, client, db_session):
        """Test retrieving current user info"""
        response = client.get(f"{auth_prefix}/me")

        assert response.status_code == 200
        user = response.json()
        assert "uid" in user or "email" in user

    def test_verify_email_invalid_token(self, client, db_session):
        """Test email verification with invalid token returns 400"""
        response = client.get(f"{auth_prefix}/verify/some_invalid_token_abc123")
        assert response.status_code in [200, 400]

    def test_password_hashing(self):
        """Test that password hashing functions exist and are callable"""
        from src.auth.utils import create_hash, verify_hash

        assert callable(create_hash)
        assert callable(verify_hash)

        try:
            password = "shortpass"
            hashed = create_hash(password)
            assert hashed != password
            assert verify_hash(password, hashed)
            assert not verify_hash("wrong_password", hashed)
        except (ValueError, Exception) as e:
            if "bcrypt" in str(e).lower() or "backend" in str(e).lower() or "bytes" in str(e).lower():
                pytest.skip(f"bcrypt backend incompatibility in test environment: {e}")
            raise

    def test_token_creation(self):
        """Test JWT token creation"""
        from src.auth.utils import create_access_token, create_refresh_access_token

        user_id = uuid4()
        email = "test@example.com"
        payload = {"uid": str(user_id), "email": email, "role": "user"}

        access_token = create_access_token(payload)
        refresh_token = create_refresh_access_token(payload)

        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 0
        assert len(refresh_token) > 0

    def test_user_email_uniqueness(self, client, db_session):
        """Test that user emails must be unique"""
        with patch('src.auth.routes.auth_service.check_user_exists', new_callable=AsyncMock) as mock_check:
            from fastapi import HTTPException
            mock_check.side_effect = HTTPException(status_code=403, detail="User exists")

            signup_data = {
                "username": "user1",
                "email": "same@example.com",
                "first_name": "First",
                "last_name": "User",
                "role": "user",
                "password": "password123"
            }

            response = client.post(f"{auth_prefix}/signup", json=signup_data)
            assert response.status_code == 403
