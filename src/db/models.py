from sqlmodel import SQLModel, Field, Column, func, Relationship
from typing import Optional
import uuid
from datetime import datetime 
import sqlalchemy.dialects.postgresql as pg
from enum import Enum


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False))
    username: str
    first_name: str
    last_name: str
    email: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = Field(default=False)
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    orders: list["Orders"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: list["Reviews"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    # Inside your existing User model
    notifications: list["Notification"] = Relationship(back_populates="user",sa_relationship_kwargs={"lazy": "selectin"})
    
    def __repr__(self):
        return f"{self.username} with email:{self.email} with the role of {self.role}"
    


class OrderStatus(str, Enum):
    pending = "pending"
    order_accepted = "order_accepted"
    in_transit = "in_transit"
    completed = "completed"
    cancelled = "cancelled"    
    

class Orders(SQLModel, table=True):
    __tablename__ = "orders"
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False))
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid", nullable=True)
    quantity: int = Field(default=0, nullable=False)
    order_status: OrderStatus = Field(default=OrderStatus.pending, nullable=False)
    pizza_size: str
    flavour: str
    total_price: float = Field(default=0.0, nullable=False)
    placed_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    user: Optional["User"] = Relationship(back_populates="orders", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: list["Reviews"] = Relationship(back_populates="orders", sa_relationship_kwargs={"lazy": "selectin"})
    
    def __repr__(self):
        return f"The pizza is {self.order_status} and the size is {self.pizza_size}"




class Reviews(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False))
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    orders_id: Optional[uuid.UUID] = Field(default=None, foreign_key="orders.uid")
    comment: str = Field(sa_column=Column(pg.VARCHAR, default="", nullable=False))
    rating: int = Field(sa_column=Column(pg.INTEGER, default=0, nullable=False))  
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    user: Optional["User"] = Relationship(back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"})
    orders: Optional["Orders"] = Relationship(back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"})
    
    def __repr__(self):
        return f"The comment for {self.orders_id} and it was made by {self.user_id} at {self.created_at}"






class NotificationType(str, Enum):
    verification = "verification"
    maintenance = "maintenance"
    order_placed = "order_placed"
    order_accepted = "order_accepted"
    order_in_transit = "order_in_transit"
    order_completed = "order_completed"
    order_cancelled = "order_cancelled"
    new_order = "new_order"


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message: str                          # the notification content
    notification_type: NotificationType   # what kind of notification this is
    is_read: bool = Field(default=False)  # has the user seen this? defaults to unread
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key linking this notification to the user it belongs to
    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    user: Optional["User"] = Relationship(back_populates="notifications", sa_relationship_kwargs={"lazy": "selectin"})