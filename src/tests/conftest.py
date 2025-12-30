from src.db.main import get_session
from unittest.mock import Mock
from fastapi.testclient import TestClient
from src.auth.dependencies import Rolechecker,AccessTokenBearer,RefreshTokenBearer
from src import app
import pytest

mock_session = Mock()
mock_user_user_service = Mock()
mock_pizza_service = Mock()
def override_get_session():
    yield mock_session
role_checker = Rolechecker(["admin","user","staff"])
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
app.dependency_overrides[Rolechecker] = Mock()
app.dependency_overrides[AccessTokenBearer] = Mock()    
app.dependency_overrides[RefreshTokenBearer] = Mock()    
app.dependency_overrides[get_session] = override_get_session   

@pytest.fixture(autouse=True)
def fake_db_session():
    return mock_session


@pytest.fixture(autouse=True)
def fake_user_service():
    return mock_user_user_service

@pytest.fixture
def client():
    return TestClient(app)
@pytest.fixture()
def fake_pizza_service():
    return mock_pizza_service
        