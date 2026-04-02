from src.db.main import get_session
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from src.auth.dependencies import Rolechecker, AccessTokenBearer, RefreshTokenBearer, get_current_user
from src import app
import pytest

# Create mock session
mock_session = AsyncMock()

# Mock dependency functions
def override_get_session():
    yield mock_session

def override_role_checker():
    return True

def override_access_token():
    return {
        "uid": "test-user-id",
        "email": "test@example.com",
        "role": "user",
        "jti": "test-jti"
    }

def override_refresh_token():
    return {
        "uid": "test-user-id",
        "email": "test@example.com",
        "role": "user",
        "exp": 9999999999
    }

def override_current_user():
    return Mock(
        uid="test-user-id",
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        role="user",
        is_verified=True
    )

# Override dependencies
app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[Rolechecker] = override_role_checker
app.dependency_overrides[AccessTokenBearer] = override_access_token
app.dependency_overrides[RefreshTokenBearer] = override_refresh_token
app.dependency_overrides[get_current_user] = override_current_user

@pytest.fixture
def db_session():
    """Fixture to provide mock database session"""
    mock_session.reset_mock()
    return mock_session

@pytest.fixture
def client():
    """Fixture to provide test client"""
    return TestClient(app)
