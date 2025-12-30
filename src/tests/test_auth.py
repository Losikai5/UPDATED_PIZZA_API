import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.auth.schemas import SignupModel
from src.db.models import User
import uuid
from datetime import datetime

auth_prefix = "/api/v2/auth"


class TestAuthentication:
    """Test suite for authentication endpoints"""

    @pytest.mark.asyncio
    async def test_signup_success(self, client, db_session, mock_celery_tasks):
        """Test successful user signup with Celery email task"""
        signup_data = {
            "email": "johndoe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "strongpassword123",
            "role": "user",
            "username": "johndoe",
            "is_verified": False
        }

        with patch('src.auth.routes.auth_service.check_user_exists', new_callable=AsyncMock) as mock_check, \
             patch('src.auth.routes.auth_service.create_user', new_callable=AsyncMock) as mock_create:
            
            # Mock user doesn't exist
            mock_check.return_value = None
            
            # Mock user creation
            mock_user = Mock()
            mock_user.uid = uuid.uuid4()
            mock_user.email = signup_data["email"]
            mock_user.first_name = signup_data["first_name"]
            mock_user.last_name = signup_data["last_name"]
            mock_user.username = signup_data["username"]
            mock_user.role = signup_data["role"]
            mock_user.is_verified = False
            mock_user.created_at = datetime.now()
            mock_create.return_value = mock_user

            response = client.post(f"{auth_prefix}/signup", json=signup_data)

            assert response.status_code == 200
            assert "message" in response.json()
            assert "user" in response.json()
            mock_check.assert_called_once()
            mock_create.assert_called_once()
            # Verify Celery task was queued
            mock_celery_tasks.assert_called_once()
            call_kwargs = mock_celery_tasks.call_args[1]
            assert call_kwargs['recipients'] == [signup_data["email"]]
            assert "Welcome" in call_kwargs['body']

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client, db_session):
        """Test signup with existing email"""
        signup_data = {
            "email": "existing@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "strongpassword123",
            "role": "user",
            "username": "johndoe",
            "is_verified": False
        }

        with patch('src.auth.routes.auth_service.check_user_exists', new_callable=AsyncMock) as mock_check:
            # Mock user already exists
            mock_check.return_value = Mock()

            response = client.post(f"{auth_prefix}/signup", json=signup_data)

            assert response.status_code == 403
            assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_success(self, client, db_session):
        """Test successful login"""
        login_data = {
            "email": "johndoe@example.com",
            "password": "strongpassword123"
        }

        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user, \
             patch('src.auth.routes.Verify_hash') as mock_verify:
            
            # Mock user exists
            mock_user = Mock()
            mock_user.uid = uuid.uuid4()
            mock_user.email = login_data["email"]
            mock_user.password_hash = "hashed_password"
            mock_user.role = "user"
            mock_get_user.return_value = mock_user
            
            # Mock password verification
            mock_verify.return_value = True

            response = client.post(f"{auth_prefix}/login", json=login_data)

            assert response.status_code == 200
            assert "access_token" in response.json()
            assert "refresh_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, db_session):
        """Test login with invalid credentials"""
        login_data = {
            "email": "johndoe@example.com",
            "password": "wrongpassword"
        }

        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user, \
             patch('src.auth.routes.Verify_hash') as mock_verify:
            
            # Mock user exists
            mock_user = Mock()
            mock_user.password_hash = "hashed_password"
            mock_get_user.return_value = mock_user
            
            # Mock password verification fails
            mock_verify.return_value = False

            response = client.post(f"{auth_prefix}/login", json=login_data)

            assert response.status_code == 401
            assert "wrong credentials" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, client, db_session):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }

        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
            # Mock user doesn't exist
            mock_get_user.return_value = None

            response = client.post(f"{auth_prefix}/login", json=login_data)

            assert response.status_code == 401
            assert "wrong credentials" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_verify_email_success(self, client, db_session):
        """Test successful email verification"""
        token = "valid_token"

        with patch('src.auth.routes.verify_email_verification_token') as mock_verify_token, \
             patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user, \
             patch('src.auth.routes.auth_service.update_user', new_callable=AsyncMock) as mock_update:
            
            # Mock token verification
            mock_verify_token.return_value = {"email": "test@example.com"}
            
            # Mock user exists
            mock_user = Mock()
            mock_user.email = "test@example.com"
            mock_user.is_verified = False
            mock_get_user.return_value = mock_user

            response = client.get(f"{auth_prefix}/verify_email/{token}")

            assert response.status_code == 200
            assert "verified successfully" in response.json()["message"].lower()
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client, db_session):
        """Test email verification with invalid token"""
        token = "invalid_token"

        with patch('src.auth.routes.verify_email_verification_token') as mock_verify_token:
            # Mock token verification fails
            mock_verify_token.return_value = None

            response = client.get(f"{auth_prefix}/verify_email/{token}")

            assert response.status_code == 400
            assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_request_success(self, client, db_session, mock_celery_tasks):
        """Test password reset request with Celery email task"""
        reset_data = {"email": "test@example.com"}

        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
            
            # Mock user exists
            mock_user = Mock()
            mock_user.email = reset_data["email"]
            mock_get_user.return_value = mock_user

            response = client.post(f"{auth_prefix}/password-reset-request", json=reset_data)

            assert response.status_code == 200
            assert "queued" in response.json()["message"].lower()
            # Verify Celery task was queued
            mock_celery_tasks.assert_called()
            call_kwargs = mock_celery_tasks.call_args[1]
            assert call_kwargs['recipients'] == [reset_data["email"]]
            assert "reset" in call_kwargs['subject'].lower()

    @pytest.mark.asyncio
    async def test_password_reset_request_user_not_found(self, client, db_session):
        """Test password reset request for non-existent user"""
        reset_data = {"email": "nonexistent@example.com"}

        with patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
            # Mock user doesn't exist
            mock_get_user.return_value = None

            response = client.post(f"{auth_prefix}/password-reset-request", json=reset_data)

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_confirm_success(self, client, db_session):
        """Test password reset confirmation"""
        token = "valid_token"
        reset_data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }

        with patch('src.auth.routes.verify_email_verification_token') as mock_verify_token, \
             patch('src.auth.routes.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user, \
             patch('src.auth.routes.auth_service.update_user', new_callable=AsyncMock) as mock_update, \
             patch('src.auth.routes.Create_hash') as mock_hash:
            
            # Mock token verification
            mock_verify_token.return_value = {"email": "test@example.com"}
            
            # Mock user exists
            mock_user = Mock()
            mock_user.email = "test@example.com"
            mock_get_user.return_value = mock_user
            
            # Mock password hashing
            mock_hash.return_value = "hashed_new_password"

            response = client.post(f"{auth_prefix}/password-reset-confirm/{token}", json=reset_data)

            assert response.status_code == 200
            assert "reset successfully" in response.json()["message"].lower()
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_password_reset_confirm_mismatch(self, client, db_session):
        """Test password reset with mismatched passwords"""
        token = "valid_token"
        reset_data = {
            "new_password": "newpassword123",
            "confirm_password": "differentpassword"
        }

        response = client.post(f"{auth_prefix}/password-reset-confirm/{token}", json=reset_data)

        assert response.status_code == 400
        assert "do not match" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_logout_success(self, client, db_session):
        """Test successful logout"""
        with patch('src.auth.routes.add_token_to_blocklist', new_callable=AsyncMock) as mock_blocklist:
            response = client.get(f"{auth_prefix}/logout")

            assert response.status_code == 200
            assert "logged out" in response.json()["message"].lower()
            mock_blocklist.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client, db_session):
        """Test successful token refresh"""
        response = client.get(f"{auth_prefix}/refresh_token")

        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, db_session):
        """Test getting current user information"""
        response = client.get(f"{auth_prefix}/me")

        assert response.status_code == 200