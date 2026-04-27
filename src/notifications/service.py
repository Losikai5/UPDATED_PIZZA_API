from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Notification, NotificationType
import uuid
from fastapi import HTTPException

class NotificationService:

    # Create and save a notification to the database
    async def create_notification( self, user_uid: uuid.UUID, message: str,notification_type: NotificationType,session: AsyncSession) -> Notification:
        notification = Notification(
            user_uid=user_uid,
            message=message,
            notification_type=notification_type,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    # Get all notifications for a specific user, newest first
    async def get_user_notifications(
        self,
        user_uid: uuid.UUID,
        session: AsyncSession
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_uid == user_uid)
            .order_by(Notification.created_at.desc())  # newest first
        )
        result = await session.exec(statement)
        return result.all()

    # Get only unread notifications for a user
    async def get_unread_notifications(
        self,
        user_uid: uuid.UUID,
        session: AsyncSession
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_uid == user_uid)
            .where(Notification.is_read == False)  # only unread ones
        )
        result = await session.exec(statement)
        return result.all()

    # Mark a single notification as read
    async def mark_as_read(
        self,
        notification_uid: uuid.UUID,
        user_uid: uuid.UUID,
        session: AsyncSession
    ) -> Notification:
        statement = (
            select(Notification)
            .where(Notification.uid == notification_uid)
            .where(Notification.user_uid == user_uid)
        )
        result = await session.exec(statement)
        notification = result.first()
        if notification is None:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.is_read = True
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    # Mark ALL notifications for a user as read in one go
    async def mark_all_as_read(
        self,
        user_uid: uuid.UUID,
        session: AsyncSession
    ) -> dict:
        statement = (
            select(Notification)
            .where(Notification.user_uid == user_uid)
            .where(Notification.is_read == False)
        )
        result = await session.exec(statement)
        unread = result.all()

        for notification in unread:
            notification.is_read = True
            session.add(notification)

        await session.commit()
        return {"message": f"{len(unread)} notifications marked as read"}