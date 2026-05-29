from uuid import UUID
from datetime import datetime
from sqlmodel import SQLModel
from src.db.models import NotificationType
from pydantic import BaseModel

class NotificationResponse(BaseModel):
    uid: UUID
    message: str
    notification_type: NotificationType
    is_read: bool
    created_at: datetime
    user_uid: UUID

    model_config = {"from_attributes": True}

class NotificationCreate(BaseModel):
    message: str
    notification_type: NotificationType


class NotificationMarkRead(BaseModel):
    uids: list[UUID]