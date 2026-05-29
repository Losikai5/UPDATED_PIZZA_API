from pydantic import BaseModel
import uuid


class CartItemCreate(BaseModel):
    menu_item_uid: uuid.UUID
    menu_item_size_uid: uuid.UUID
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemRead(BaseModel):
    uid: uuid.UUID
    menu_item_uid: uuid.UUID
    menu_item_size_uid: uuid.UUID
    menu_item_name: str
    pizza_size: str
    quantity: int
    unit_price: float
    subtotal: float


class CartRead(BaseModel):
    uid: uuid.UUID
    items: list[CartItemRead]
    total: float
