import pytest
from unittest.mock import AsyncMock, patch, Mock, MagicMock
from uuid import uuid4
from sqlmodel import select
from src.db.models import User, Orders, Reviews, MenuItem, MenuItemSize, Notification, OrderStatus, NotificationType


class TestDatabase:
    """Test suite for database models and operations"""

    def test_user_model_creation(self, db_session):
        """Test creating a user model instance"""
        user = User(
            uid=uuid4(),
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password_hash="hashed_password",
            role="user",
            is_verified=False
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.is_verified == False

    def test_orders_model_creation(self, db_session):
        """Test creating an orders model instance"""
        user_id = uuid4()
        order = Orders(
            uid=uuid4(),
            user_id=user_id,
            quantity=2,
            order_status=OrderStatus.pending,
            pizza_size="large",
            flavour="pepperoni",
            total_price=25.99
        )

        assert order.quantity == 2
        assert order.order_status == OrderStatus.pending
        assert order.pizza_size == "large"
        assert order.flavour == "pepperoni"
        assert order.total_price == 25.99

    def test_reviews_model_creation(self, db_session):
        """Test creating a reviews model instance"""
        user_id = uuid4()
        order_id = uuid4()
        review = Reviews(
            uid=uuid4(),
            user_id=user_id,
            orders_id=order_id,
            comment="Great pizza!",
            rating=5
        )

        assert review.comment == "Great pizza!"
        assert review.rating == 5
        assert review.user_id == user_id
        assert review.orders_id == order_id

    def test_notification_model_creation(self, db_session):
        """Test creating a notification model instance"""
        user_id = uuid4()
        notification = Notification(
            uid=uuid4(),
            user_uid=user_id,
            message="Your order has been placed",
            notification_type=NotificationType.order_placed,
            is_read=False
        )

        assert notification.message == "Your order has been placed"
        assert notification.notification_type == NotificationType.order_placed
        assert notification.is_read == False
        assert notification.user_uid == user_id

    def test_menu_item_model_creation(self, db_session):
        """Test creating a menu item model instance"""
        menu_item = MenuItem(
            uid=uuid4(),
            name="Margherita",
            flavour="tomato_cheese",
            description="Classic Italian pizza",
            is_available=True
        )

        assert menu_item.name == "Margherita"
        assert menu_item.flavour == "tomato_cheese"
        assert menu_item.is_available == True

    def test_menu_item_size_model_creation(self, db_session):
        """Test creating a menu item size model instance"""
        menu_item_id = uuid4()
        size = MenuItemSize(
            uid=uuid4(),
            menu_item_uid=menu_item_id,
            pizza_size="large",
            price=15.99
        )

        assert size.pizza_size == "large"
        assert size.price == 15.99
        assert size.menu_item_uid == menu_item_id

    def test_order_status_enum_values(self):
        """Test that all order status enum values are correct"""
        statuses = [
            OrderStatus.pending,
            OrderStatus.order_accepted,
            OrderStatus.in_transit,
            OrderStatus.completed,
            OrderStatus.cancelled
        ]

        assert len(statuses) == 5
        assert all(isinstance(s, OrderStatus) for s in statuses)

    def test_notification_type_enum_values(self):
        """Test that all notification type enum values are correct"""
        types = [
            NotificationType.verification,
            NotificationType.maintenance,
            NotificationType.order_placed,
            NotificationType.order_accepted,
            NotificationType.order_in_transit,
            NotificationType.order_completed,
            NotificationType.order_cancelled,
            NotificationType.new_order
        ]

        assert len(types) == 8

    def test_user_relationships(self, db_session):
        """Test user model relationships"""
        user = User(
            uid=uuid4(),
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password_hash="hashed",
            orders=[],
            reviews=[],
            notifications=[]
        )

        assert hasattr(user, 'orders')
        assert hasattr(user, 'reviews')
        assert hasattr(user, 'notifications')

    def test_order_relationships(self, db_session):
        """Test order model relationships"""
        order = Orders(
            uid=uuid4(),
            user_id=uuid4(),
            quantity=1,
            order_status=OrderStatus.pending,
            pizza_size="medium",
            flavour="pepperoni",
            total_price=12.99,
            reviews=[]
        )

        assert hasattr(order, 'user')
        assert hasattr(order, 'reviews')

    def test_review_relationships(self, db_session):
        """Test review model relationships"""
        review = Reviews(
            uid=uuid4(),
            user_id=uuid4(),
            orders_id=uuid4(),
            comment="Good",
            rating=4
        )

        assert hasattr(review, 'user')
        assert hasattr(review, 'orders')

    def test_user_repr(self, db_session):
        """Test user model string representation"""
        user = User(
            uid=uuid4(),
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password_hash="hashed",
            role="user"
        )

        repr_str = repr(user)
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str
        assert "user" in repr_str

    def test_order_repr(self, db_session):
        """Test order model string representation"""
        order = Orders(
            uid=uuid4(),
            user_id=uuid4(),
            quantity=2,
            order_status=OrderStatus.pending,
            pizza_size="large",
            flavour="margherita",
            total_price=18.99
        )

        repr_str = repr(order)
        assert "pending" in repr_str
        assert "large" in repr_str

    def test_menu_item_with_sizes(self, db_session):
        """Test menu item with associated sizes"""
        menu_item = MenuItem(
            uid=uuid4(),
            name="Pepperoni",
            flavour="pepperoni",
            description="Spicy pepperoni pizza",
            sizes=[]
        )

        assert menu_item.name == "Pepperoni"
        assert hasattr(menu_item, 'sizes')

    def test_default_values_in_models(self):
        """Test that models have correct default values"""
        user = User(
            uid=uuid4(),
            username="test",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password_hash="hash",
            role="user"
        )

        assert user.is_verified == False
        assert user.role == "user"

    def test_order_default_status(self):
        """Test that orders default to pending status"""
        order = Orders(
            uid=uuid4(),
            quantity=1,
            pizza_size="medium",
            flavour="test",
            total_price=10.0
        )

        assert order.order_status == OrderStatus.pending

    def test_notification_default_read_status(self):
        """Test that notifications default to unread"""
        notification = Notification(
            uid=uuid4(),
            user_uid=uuid4(),
            message="Test",
            notification_type=NotificationType.order_placed
        )

        assert notification.is_read == False

    def test_menu_item_availability_default(self):
        """Test that menu items default to available"""
        item = MenuItem(
            uid=uuid4(),
            name="Test",
            flavour="test",
            description="Test"
        )

        assert item.is_available == True
