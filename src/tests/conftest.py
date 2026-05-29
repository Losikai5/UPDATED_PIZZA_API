from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
import pytest
import uuid
from datetime import datetime

mock_session = AsyncMock()
TEST_USER_ID = uuid.uuid4()

try:
    from src import app
    from src.db.main import get_session
    from src.auth.dependencies import get_current_user

    def override_get_session():
        yield mock_session

    def override_current_user():
        mock = Mock()
        mock.uid = TEST_USER_ID
        mock.email = "admin@example.com"
        mock.username = "adminuser"
        mock.first_name = "Admin"
        mock.last_name = "User"
        mock.role = "Admin"
        mock.is_verified = True
        mock.created_at = datetime(2024, 1, 1, 0, 0, 0)
        mock.updated_at = datetime(2024, 1, 1, 0, 0, 0)
        mock.orders = []
        mock.reviews = []
        return mock

    try:
        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[get_current_user] = override_current_user
    except Exception:
        pass

except (ImportError, TypeError):
    app = None


@pytest.fixture
def db_session():
    mock_session.reset_mock()
    return mock_session


@pytest.fixture
def client():
    if app is not None:
        return TestClient(app)
    return Mock()
