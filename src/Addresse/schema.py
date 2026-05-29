from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class AddressCreate(BaseModel):
    street_address: str
    city: str
    state: str
    country: str
    postal_code: str
    is_default: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "street_address": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "postal_code": "10001",
                "is_default": True,
            }
        }
    }


class AddressUpdate(BaseModel):
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    is_default: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "city": "Brooklyn",
                "postal_code": "11201",
            }
        }
    }


class AddressRead(BaseModel):
    uid: uuid.UUID
    user_uid: uuid.UUID
    street_address: str
    city: str
    state: str
    country: str
    postal_code: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
