from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.main import get_session
from src.notifications.service import NotificationService
from src.notifications.schemas import NotificationRead
from src.auth.dependencies import get_current_user  # your existing auth dependency
from src.db.models import User
import uuid

notification_router = APIRouter()
notification_service = NotificationService()

# Get all notifications for the logged in user
@notification_router.get("/", response_model=list[NotificationRead])
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await notification_service.get_user_notifications(current_user.uid, session)

# Get only unread notifications
@notification_router.get("/unread", response_model=list[NotificationRead])
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await notification_service.get_unread_notifications(current_user.uid, session)

# Mark a single notification as read
@notification_router.patch("/{notification_uid}/read", response_model=NotificationRead)
async def mark_notification_as_read(
    notification_uid: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await notification_service.mark_as_read(notification_uid, current_user.uid, session)

# Mark all notifications as read
@notification_router.patch("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await notification_service.mark_all_as_read(current_user.uid, session)