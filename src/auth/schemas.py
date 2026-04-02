from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


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
