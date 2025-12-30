from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class OrderCreate(BaseModel):
    quantity: int
    order_status: str
    pizza_size: str
    flavour: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 2,
                "order_status": "pending",
                "pizza_size": "medium",
                "flavour": "pepperoni",
            }
        }

class OrderUpdate(BaseModel):
    quantity: Optional[int] = None
    order_status: Optional[str] = None
    pizza_size: Optional[str] = None
    flavour: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 3,  # Example of updating quantity
                "order_status": "in_transit",  # Example of updating status
                "pizza_size": "large",  # Example of updating size
                "flavour": "mushroom",  # Example of updating flavour
            }
        }

class OrderRead(BaseModel):
    uid: uuid.UUID
    quantity: int
    order_status: str
    pizza_size: str
    flavour: str
    placed_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "quantity": 2,
                "order_status": "pending",
                "pizza_size": "medium",
                "flavour": "pepperoni",
                "placed_at": "2024-06-01T12:00:00"
            }
        }

