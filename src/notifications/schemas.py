import uuid
from datetime import datetime
from sqlmodel import SQLModel
from src.db.models import NotificationType

# What we return when reading a notification
class NotificationRead(SQLModel):
    uid: uuid.UUID
    message: str
    notification_type: NotificationType
    is_read: bool
    created_at: datetime

# What we accept when marking a notification as read
class NotificationUpdateRead(SQLModel):
    is_read: bool