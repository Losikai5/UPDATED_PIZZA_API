import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.Reviews.schemas import ReviewCreate
import uuid
from datetime import datetime

reviews_prefix = "/api/v2/reviews"


class TestReviews:
    """Test suite for review endpoints"""

    @pytest.mark.asyncio
    async def test_get_all_reviews_success(self, client, db_session):
        """Test getting all reviews"""
        with patch('src.Reviews.routes.reviews_service.Get_reviews', new_callable=AsyncMock) as mock_get_reviews:
            # Mock reviews list
            mock_review1 = Mock()
            mock_review1.uid = uuid.uuid4()
            mock_review1.Comment = "Great pizza!"
            mock_review1.Rating = 5
            mock_review1.Created_at = datetime.now()

            mock_review2 = Mock()
            mock_review2.uid = uuid.uuid4()
            mock_review2.Comment = "Good but could be better"
            mock_review2.Rating = 3
            mock_review2.Created_at = datetime.now()

            mock_get_reviews.return_value = [mock_review1, mock_review2]

            response = client.get(f"{reviews_prefix}/")

            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) == 2
            mock_get_reviews.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_reviews_empty(self, client, db_session):
        """Test getting all reviews when none exist"""
        with patch('src.Reviews.routes.reviews_service.Get_reviews', new_callable=AsyncMock) as mock_get_reviews:
            mock_get_reviews.return_value = []

            response = client.get(f"{reviews_prefix}/")

            assert response.status_code == 200
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_review_success(self, client, db_session):
        """Test successful review creation"""
        review_data = {
            "Comment": "Excellent pizza, loved the crust!",
            "Rating": 5
        }

        with patch('src.Reviews.routes.reviews_service.Create_review', new_callable=AsyncMock) as mock_create:
            # Mock created review
            mock_review = Mock()
            mock_review.uid = uuid.uuid4()
            mock_review.Comment = review_data["Comment"]
            mock_review.Rating = review_data["Rating"]
            mock_review.Created_at = datetime.now()
            mock_create.return_value = mock_review

            response = client.post(f"{reviews_prefix}/", json=review_data)

            assert response.status_code == 200
            result = response.json()
            assert result["Comment"] == review_data["Comment"]
            assert result["Rating"] == review_data["Rating"]
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_review_invalid_rating_too_high(self, client, db_session):
        """Test review creation with rating > 5"""
        review_data = {
            "Comment": "Great pizza!",
            "Rating": 6  # Invalid: should be 1-5
        }

        response = client.post(f"{reviews_prefix}/", json=review_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_review_invalid_rating_too_low(self, client, db_session):
        """Test review creation with rating < 1"""
        review_data = {
            "Comment": "Terrible pizza!",
            "Rating": 0  # Invalid: should be 1-5
        }

        response = client.post(f"{reviews_prefix}/", json=review_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_review_missing_comment(self, client, db_session):
        """Test review creation without comment"""
        review_data = {
            "Rating": 4
            # Missing Comment field
        }

        response = client.post(f"{reviews_prefix}/", json=review_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_review_by_id_success(self, client, db_session):
        """Test getting review by ID"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.Get_review_by_id', new_callable=AsyncMock) as mock_get_review:
            # Mock review
            mock_review = Mock()
            mock_review.uid = review_uid
            mock_review.Comment = "Amazing pizza!"
            mock_review.Rating = 5
            mock_review.Created_at = datetime.now()
            mock_get_review.return_value = mock_review

            response = client.get(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 200
            result = response.json()
            assert result["Comment"] == "Amazing pizza!"
            assert result["Rating"] == 5
            mock_get_review.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_review_by_id_not_found(self, client, db_session):
        """Test getting non-existent review by ID"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.Get_review_by_id', new_callable=AsyncMock) as mock_get_review:
            mock_get_review.return_value = None

            response = client.get(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_add_review_to_order_success(self, client, db_session):
        """Test adding review to an order"""
        order_uid = str(uuid.uuid4())
        review_data = {
            "Comment": "Great pizza and fast delivery!",
            "Rating": 4
        }

        with patch('src.Reviews.routes.reviews_service.add_review_to_order', new_callable=AsyncMock) as mock_add_review:
            # Mock created review
            mock_review = Mock()
            mock_review.uid = uuid.uuid4()
            mock_review.Comment = review_data["Comment"]
            mock_review.Rating = review_data["Rating"]
            mock_review.Created_at = datetime.now()
            mock_add_review.return_value = mock_review

            response = client.post(f"{reviews_prefix}/order/{order_uid}", json=review_data)

            assert response.status_code == 200
            result = response.json()
            assert result["Comment"] == review_data["Comment"]
            assert result["Rating"] == review_data["Rating"]
            mock_add_review.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_review_to_order_not_found(self, client, db_session):
        """Test adding review to non-existent order"""
        order_uid = str(uuid.uuid4())
        review_data = {
            "Comment": "Great pizza!",
            "Rating": 5
        }

        with patch('src.Reviews.routes.reviews_service.add_review_to_order', new_callable=AsyncMock) as mock_add_review:
            from fastapi import HTTPException
            mock_add_review.side_effect = HTTPException(status_code=404, detail="Order not found")

            response = client.post(f"{reviews_prefix}/order/{order_uid}", json=review_data)

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_review_success(self, client, db_session):
        """Test successful review deletion"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.delete_review_to_from_order', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            response = client.delete(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 200
            assert "deleted successfully" in response.json()["detail"].lower()
            mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_review_not_found(self, client, db_session):
        """Test deleting non-existent review"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.delete_review_to_from_order', new_callable=AsyncMock) as mock_delete:
            from fastapi import HTTPException
            mock_delete.side_effect = HTTPException(status_code=404, detail="Review not found")

            response = client.delete(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_review_unauthorized(self, client, db_session):
        """Test deleting review by unauthorized user"""
        review_uid = str(uuid.uuid4())

        with patch('src.Reviews.routes.reviews_service.delete_review_to_from_order', new_callable=AsyncMock) as mock_delete:
            from fastapi import HTTPException
            mock_delete.side_effect = HTTPException(status_code=403, detail="Not authorized to delete this review")

            response = client.delete(f"{reviews_prefix}/{review_uid}")

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_review_rating_boundaries(self, client, db_session):
        """Test review creation with boundary ratings (1 and 5)"""
        # Test rating = 1
        review_data_low = {
            "Comment": "Not good",
            "Rating": 1
        }

        with patch('src.Reviews.routes.reviews_service.Create_review', new_callable=AsyncMock) as mock_create:
            mock_review = Mock()
            mock_review.uid = uuid.uuid4()
            mock_review.Comment = review_data_low["Comment"]
            mock_review.Rating = review_data_low["Rating"]
            mock_review.Created_at = datetime.now()
            mock_create.return_value = mock_review

            response = client.post(f"{reviews_prefix}/", json=review_data_low)

            assert response.status_code == 200
            assert response.json()["Rating"] == 1

        # Test rating = 5
        review_data_high = {
            "Comment": "Perfect!",
            "Rating": 5
        }

        with patch('src.Reviews.routes.reviews_service.Create_review', new_callable=AsyncMock) as mock_create:
            mock_review = Mock()
            mock_review.uid = uuid.uuid4()
            mock_review.Comment = review_data_high["Comment"]
            mock_review.Rating = review_data_high["Rating"]
            mock_review.Created_at = datetime.now()
            mock_create.return_value = mock_review

            response = client.post(f"{reviews_prefix}/", json=review_data_high)

            assert response.status_code == 200
            assert response.json()["Rating"] == 5

    @pytest.mark.asyncio
    async def test_review_with_long_comment(self, client, db_session):
        """Test review creation with long comment"""
        long_comment = "This is an excellent pizza! " * 50  # Long comment
        review_data = {
            "Comment": long_comment,
            "Rating": 5
        }

        with patch('src.Reviews.routes.reviews_service.Create_review', new_callable=AsyncMock) as mock_create:
            mock_review = Mock()
            mock_review.uid = uuid.uuid4()
            mock_review.Comment = review_data["Comment"]
            mock_review.Rating = review_data["Rating"]
            mock_review.Created_at = datetime.now()
            mock_create.return_value = mock_review

            response = client.post(f"{reviews_prefix}/", json=review_data)

            assert response.status_code == 200
            assert len(response.json()["Comment"]) == len(long_comment)
