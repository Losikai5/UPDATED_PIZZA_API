from sqlmodel import SQLModel, Field, Column, func, Relationship
from typing import Optional,List
import uuid
from datetime import datetime 
import sqlalchemy.dialects.postgresql as pg
from enum import Enum  
from sqlalchemy import Column, Enum as SAEnum, ForeignKey  # SAEnum is SQLAlchemy's Enum, not Python's


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
    notifications: list["Notification"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    addresses: list["Address"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

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
    message: str
    notification_type: NotificationType
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    user: Optional["User"] = Relationship(back_populates="notifications", sa_relationship_kwargs={"lazy": "selectin"})




class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    user_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey("users.uid"), nullable=False, unique=True)
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    items: List["CartItem"] = Relationship(
        back_populates="cart",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    cart_uid: uuid.UUID = Field(foreign_key="carts.uid", nullable=False)
    menu_item_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey("menu_items.uid"), nullable=False)
    )
    menu_item_size_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey("menu_item_sizes.uid"), nullable=False)
    )
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    cart: Optional["Cart"] = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class PizzaSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"
    extra_large = "extra_large"

class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_items"
    
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    name: str = Field(nullable=False)
    flavour: str = Field(nullable=False)
    description: str = Field(nullable=False)
    is_available: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, server_default=func.now())
    )
    
    # Use List["MenuItemSize"] for the relationship
    sizes: List["MenuItemSize"] = Relationship(
        back_populates="menu_item", 
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"}
    )

class MenuItemSize(SQLModel, table=True):
    __tablename__ = "menu_item_sizes"
    
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    # Use the Enum here for validation
    pizza_size: PizzaSize = Field(sa_column=Column(SAEnum(PizzaSize, name="pizzasize", create_type=False), nullable=False))
    price: float = Field(nullable=False)

    menu_item_uid: uuid.UUID = Field(foreign_key="menu_items.uid", nullable=False)

    menu_item: Optional["MenuItem"] = Relationship(
        back_populates="sizes",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class Address(SQLModel, table=True):
    __tablename__ = "addresses"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    user_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey("users.uid"), nullable=False)
    )
    street_address: str = Field(nullable=False)
    city: str = Field(nullable=False)
    state: str = Field(nullable=False)
    country: str = Field(nullable=False)
    postal_code: str = Field(nullable=False)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    user: Optional["User"] = Relationship(
        back_populates="addresses",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
