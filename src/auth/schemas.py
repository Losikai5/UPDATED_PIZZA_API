from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid
from typing import Optional, List
from src.Reviews.schemas import ReviewRead
from src.Orders.schemas import OrderRead


class SignupModel(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "role": "user",
                "password": "strongpassword123"
            }
        }
    }


class SignupResponse(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    is_verified: bool
    role: str
    created_at: datetime
   

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "is_verified": True,
                "role": "user",
                "created_at": "2024-06-01T12:00:00"
            }
        }
    }

class LoginModel(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "johndoe@example.com",
                "password": "strongpassword123"
            }
        }
    }

class UserRead(SignupResponse):
     model_config = {
            "from_attributes": True,
            "json_schema_extra": {
                "example": {
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "johndoe@example.com",
                    "is_verified": True,
                    "role": "user",
                    "created_at": "2024-06-01T12:00:00"
                }
            }
        }


class SignupSuccessResponse(BaseModel):
    message: str
    user: UserRead

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "message": "User created successfully please verify your email.",
                "user": {
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "johndoe@example.com",
                    "is_verified": False,
                    "role": "user",
                    "created_at": "2024-06-01T12:00:00"
                }
            }
        }
    }


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class AccessTokenResponse(BaseModel):
    access_token: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class MessageResponse(BaseModel):
    message: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "message": "Operation completed successfully."
            }
        }
    }


class UserDetailRead(UserRead):
    orders: List[OrderRead]
    reviews: List[ReviewRead]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "is_verified": True,
                "role": "user",
                "created_at": "2024-06-01T12:00:00",
                "orders": [],
                "reviews": []
            }
        }
    }

class EmailModel(BaseModel):
    addresses : List[str]    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "addresses": ["johndoe@example.com"]
            }
        }
    }

class PasswordResetRequestModel(BaseModel):
    email: str
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "johndoe@example.com"
            }
        }
    }


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "new_password": "newpassword123",
                "confirm_new_password": "newpassword123"
            }
        }
    }