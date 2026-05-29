from pydantic import BaseModel
from src.db.models import PizzaSize
from typing import Optional
import uuid
from datetime import datetime

# Schema for a single size+price combination
class MenuItemSizeCreate(BaseModel):
    pizza_size: PizzaSize   # must be one of the PizzaSize enum values
    price: float            # unit cost for this size in UGX

# Schema for reading a size back in responses
class MenuItemSizeRead(BaseModel):
    uid: uuid.UUID
    pizza_size: PizzaSize
    price: float

# Schema for creating a full menu item with sizes in one request
class MenuItemCreate(BaseModel):
    name: str
    flavour: str
    description: str
    is_available: bool = True
    sizes: list[MenuItemSizeCreate]  # list of size+price combinations

# Schema for reading a full menu item with its sizes in responses
class MenuItemRead(BaseModel):
    uid: uuid.UUID
    name: str
    flavour: str
    description: str
    is_available: bool
    created_at: datetime
    sizes: list[MenuItemSizeRead]  # sizes are always included in the response

# Schema for updating a menu item — all fields optional so admin can update just one field
class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    flavour: Optional[str] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None