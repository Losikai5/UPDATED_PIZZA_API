import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.Reviews.schemas import ReviewCreate
import uuid
from datetime import datetime
from src.tests.conftest import TEST_USER_ID

reviews_prefix = "/api/v2/review"


def make_review_dict(**kwargs):
    defaults = dict(
        uid=str(uuid.uuid4()),
        comment="Great pizza!",
        rating=5,
        created_at=datetime(2024, 1, 1, 0, 0, 0).isoformat(),
    )
    defaults.update(kwargs)
    return defaults


class TestReviews:
    """Test suite for review endpoints"""

    def test_get_all_reviews_success(self, client, db_session):
        """Test getting all reviews"""
        with patch('src.Reviews.routes.reviews_service.get_reviews', new_callable=AsyncMock) as mock_get_reviews:
            mock_get_reviews.return_value = [
                make_review_dict(comment="Great pizza!", rating=5),
                make_review_dict(comment="Good but could be better", rating=3),
            ]

            response = client.get(f"{reviews_prefix}/")

            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) == 2
            mock_get_reviews.assert_called_once()

    def test_get_all_reviews_empty(self, client, db_session):
        """Test getting all reviews when none exist"""
        with patch('src.Reviews.routes.reviews_service.get_reviews', new_callable=AsyncMock) as mock_get_reviews:
            mock_get_reviews.return_value = []

            response = client.get(f"{reviews_prefix}/")

            assert response.status_code == 200
            assert response.json() == []

    def test_create_review_success(self, client, db_session):
        """Test successful review creation"""
        order_id = str(uuid.uuid4())
        review_data = {"comment": "Excellent pizza, loved the crust!", "rating": 5}

        with patch('src.Reviews.routes.OrdersService') as mock_order_service_cls:
            with patch('src.Reviews.routes.reviews_service.create_review', new_callable=AsyncMock) as mock_create:
                mock_order_service = AsyncMock()
                mock_order = Mock()
                mock_order.user_id = TEST_USER_ID
                mock_order_service.get_order_by_id.return_value = mock_order
                mock_order_service_cls.return_value = mock_order_service

                mock_create.return_value = make_review_dict(**review_data)

                response = client.post(f"{reviews_prefix}/{order_id}", json=review_data)

                assert response.status_code == 200
                result = response.json()
                assert result["comment"] == review_data["comment"]
                assert result["rating"] == review_data["rating"]
                mock_create.assert_called_once()

    def test_create_review_invalid_rating_too_high(self, client, db_session):
        """Test review creation with rating > 5"""
        order_id = str(uuid.uuid4())
        review_data = {"comment": "Great pizza!", "rating": 6}

        response = client.post(f"{reviews_prefix}/{order_id}", json=review_data)

        assert response.status_code == 422

    def test_create_review_invalid_rating_too_low(self, client, db_session):
        """Test review creation with rating < 0"""
        order_id = str(uuid.uuid4())
        review_data = {"comment": "Terrible pizza!", "rating": -1}

        response = client.post(f"{reviews_prefix}/{order_id}", json=review_data)

        assert response.status_code == 422

    def test_create_review_missing_comment(self, client, db_session):
        """Test review creation without comment"""
        order_id = str(uuid.uuid4())
        review_data = {"rating": 4}

        response = client.post(f"{reviews_prefix}/{order_id}", json=review_data)

        assert response.status_code == 422

    def test_get_review_by_id_success(self, client, db_session):
        """Test getting review by ID"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.get_review_by_id', new_callable=AsyncMock) as mock_get_review:
            mock_get_review.return_value = make_review_dict(uid=review_uid, comment="Amazing pizza!", rating=5)

            response = client.get(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 200
            result = response.json()
            assert result["comment"] == "Amazing pizza!"
            assert result["rating"] == 5
            mock_get_review.assert_called_once()

    def test_get_review_by_id_not_found(self, client, db_session):
        """Test getting non-existent review by ID"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.get_review_by_id', new_callable=AsyncMock) as mock_get_review:
            mock_get_review.return_value = None

            response = client.get(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_delete_review_success(self, client, db_session):
        """Test successful review deletion"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.get_review_by_id', new_callable=AsyncMock) as mock_get:
            with patch('src.Reviews.routes.reviews_service.delete_review', new_callable=AsyncMock) as mock_delete:
                mock_review = Mock()
                mock_review.user_id = TEST_USER_ID
                mock_get.return_value = mock_review
                mock_delete.return_value = None

                response = client.delete(f"{reviews_prefix}/{review_uid}")

                assert response.status_code == 200
                assert "deleted successfully" in response.json()["detail"].lower()
                mock_delete.assert_called_once()

    def test_delete_review_not_found(self, client, db_session):
        """Test deleting non-existent review"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.get_review_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            response = client.delete(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 404

    def test_review_rating_boundaries(self, client, db_session):
        """Test review creation with boundary ratings (0 and 5)"""
        order_id = str(uuid.uuid4())

        with patch('src.Reviews.routes.OrdersService') as mock_order_service_cls:
            with patch('src.Reviews.routes.reviews_service.create_review', new_callable=AsyncMock) as mock_create:
                mock_order_service = AsyncMock()
                mock_order = Mock()
                mock_order.user_id = TEST_USER_ID
                mock_order_service.get_order_by_id.return_value = mock_order
                mock_order_service_cls.return_value = mock_order_service

                for rating in [0, 5]:
                    mock_create.return_value = make_review_dict(rating=rating)
                    review_data = {"comment": "Test comment", "rating": rating}
                    response = client.post(f"{reviews_prefix}/{order_id}", json=review_data)
                    assert response.status_code == 200
                    assert response.json()["rating"] == rating

    def test_review_with_long_comment(self, client, db_session):
        """Test review creation with long comment"""
        order_id = str(uuid.uuid4())
        long_comment = "This is an excellent pizza! " * 50
        review_data = {"comment": long_comment, "rating": 5}

        with patch('src.Reviews.routes.OrdersService') as mock_order_service_cls:
            with patch('src.Reviews.routes.reviews_service.create_review', new_callable=AsyncMock) as mock_create:
                mock_order_service = AsyncMock()
                mock_order = Mock()
                mock_order.user_id = TEST_USER_ID
                mock_order_service.get_order_by_id.return_value = mock_order
                mock_order_service_cls.return_value = mock_order_service

                mock_create.return_value = make_review_dict(comment=long_comment)

                response = client.post(f"{reviews_prefix}/{order_id}", json=review_data)

                assert response.status_code == 200
                assert len(response.json()["comment"]) == len(long_comment)
