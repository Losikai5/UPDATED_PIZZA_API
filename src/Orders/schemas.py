from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid
from src.Reviews.schemas import ReviewRead
from src.celery import send_order_accepted_task, send_order_completed_task, send_order_in_transit_task, send_order_in_transit_task,send_order_cancelled_task, send_order_confirmation_task
from src.db.models import Notification, NotificationType, OrderStatus


class OrderCreate(BaseModel):
    quantity: int
    pizza_size: str
    flavour: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 2,
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
    user_id: Optional[uuid.UUID] = None
    quantity: int
    order_status: str
    pizza_size: str
    flavour: str
    total_price: float
    placed_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "quantity": 2,
                "order_status": "pending",
                "pizza_size": "medium",
                "flavour": "pepperoni",
                "total_price": 30.0,
                "placed_at": "2024-06-01T12:00:00"
            }
        }

class OrderDetailRead(OrderRead):
    reviews: List[ReviewRead]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "quantity": 2,
                "order_status": "pending",
                "pizza_size": "medium",
                "flavour": "pepperoni",
                "total_price": 30.0,
                "placed_at": "2024-06-01T12:00:00",
                "reviews": []
            }
        }


