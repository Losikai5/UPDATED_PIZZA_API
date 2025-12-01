from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class PizzaSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"

class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"

class OrderCreate(BaseModel):
    Quantity: int
    Order_status: OrderStatus
    pizza_size: PizzaSize
    flavour: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "Quantity": 2,
                "Order_status": "pending",
                "pizza_size": "medium",
                "flavour": "pepperoni",
            }
        }

class OrderUpdate(BaseModel):
    Quantity: Optional[int] = None
    Order_status: Optional[OrderStatus] = None
    pizza_size: Optional[PizzaSize] = None
    flavour: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "Quantity": 3,  # Example of updating quantity
                "Order_status": "in_transit",  # Example of updating status
                "pizza_size": "large",  # Example of updating size
                "flavour": "mushroom",  # Example of updating flavour
            }
        }

class OrderRead(BaseModel):
    uid: uuid.UUID
    Quantity: int
    Order_status: OrderStatus
    pizza_size: PizzaSize
    flavour: str
    placed_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "Quantity": 2,
                "Order_status": "pending",
                "pizza_size": "medium",
                "flavour": "pepperoni",
                "placed_at": "2024-06-01T12:00:00"
            }
        }