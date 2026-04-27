from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr


class AdminDashboardStatsResponse(BaseModel):
    users_count: int
    verified_users_count: int
    admins_count: int
    orders_count: int
    reviews_count: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "users_count": 100,
                "verified_users_count": 80,
                "admins_count": 5,
                "orders_count": 500,
                "reviews_count": 200
            }
        }
    }


class AdminUserRead(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "role": "User",
                "is_verified": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }

    }


class AdminUserRoleUpdate(BaseModel):
    role: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "Admin"
            }
        }
    }



class AdminUserVerifyUpdate(BaseModel):
    is_verified: bool
    model_config = {
        "json_schema_extra": {
            "example": {
                "is_verified": True
            }
        }
    }
