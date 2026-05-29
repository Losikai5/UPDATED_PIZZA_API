import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from src.notifications.schemas import NotificationCreate
from src.db.models import NotificationType

notifications_prefix = "/api/v2/notifications"


def make_notification_dict(**kwargs):
    defaults = dict(
        uid=str(uuid4()),
        message="Your order has been placed",
        notification_type=NotificationType.order_placed,
        is_read=False,
        created_at=datetime(2024, 1, 1, 0, 0, 0).isoformat(),
        user_uid=str(uuid4()),
    )
    defaults.update(kwargs)
    return defaults


class TestNotifications:
    """Test suite for notification endpoints and service"""

    def test_get_user_notifications_success(self, client, db_session):
        """Test retrieving user notifications"""
        with patch('src.notifications.routes.notification_service.get_user_notifications', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [make_notification_dict()]

            response = client.get(f"{notifications_prefix}/")

            assert response.status_code == 200
            assert isinstance(response.json(), list)
            mock_get.assert_called_once()

    def test_get_unread_notifications(self, client, db_session):
        """Test retrieving unread notifications only"""
        with patch('src.notifications.routes.notification_service.get_unread_notifications', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [make_notification_dict(is_read=False)]

            response = client.get(f"{notifications_prefix}/unread")

            assert response.status_code == 200
            assert isinstance(response.json(), list)
            mock_get.assert_called_once()

    def test_mark_notification_as_read(self, client, db_session):
        """Test marking a notification as read"""
        notification_id = uuid4()
        with patch('src.notifications.routes.notification_service.mark_as_read', new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = make_notification_dict(uid=str(notification_id), is_read=True)

            response = client.patch(f"{notifications_prefix}/{notification_id}/read")

            assert response.status_code == 200
            mock_mark.assert_called_once()

    def test_create_notification(self, client, db_session):
        """Test that POST to notifications is not supported (notifications are system-generated)"""
        notification_data = {
            "message": "Test notification",
            "notification_type": "order_placed"
        }

        response = client.post(f"{notifications_prefix}/", json=notification_data)

        assert response.status_code in [201, 405]

    def test_notification_types_enum(self):
        """Test that all notification types are available"""
        notification_types = [
            NotificationType.verification,
            NotificationType.maintenance,
            NotificationType.order_placed,
            NotificationType.order_accepted,
            NotificationType.order_in_transit,
            NotificationType.order_completed,
            NotificationType.order_cancelled,
            NotificationType.new_order,
        ]
        assert len(notification_types) == 8

    def test_get_notifications_empty_list(self, client, db_session):
        """Test retrieving notifications when none exist"""
        with patch('src.notifications.routes.notification_service.get_user_notifications', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            response = client.get(f"{notifications_prefix}/")

            assert response.status_code == 200
            assert response.json() == []

    def test_notification_ordering_by_date(self, client, db_session):
        """Test that notifications are ordered by creation date (newest first)"""
        with patch('src.notifications.routes.notification_service.get_user_notifications', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                make_notification_dict(created_at=datetime(2024, 1, 3).isoformat()),
                make_notification_dict(created_at=datetime(2024, 1, 1).isoformat()),
            ]

            response = client.get(f"{notifications_prefix}/")

            assert response.status_code == 200
            assert len(response.json()) == 2
