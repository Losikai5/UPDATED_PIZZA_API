from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid
from typing import List
from src.Orders.schemas import OrderRead
from pydantic import EmailStr



class SignupModel(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    is_verified: bool = False
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
                "is_verified": False,
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
                "is_verified": False,
                "role": "user",
                "created_at": "2024-06-01T12:00:00",
                "orders": []
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
     orders: List[OrderRead]
        
     model_config = {
            "from_attributes": True,
            "json_schema_extra": {
                "example": {
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "johndoe@example.com",
                    "is_verified": False,
                    "role": "user",
                    "created_at": "2024-06-01T12:00:00",
                    "orders": []
                }
            }
        }
class EmailModel(BaseModel):
    addresses: List[EmailStr]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "addresses": ["user@example.com"]
            }
        }
    }
class PasswordResetModel(BaseModel):
    email: EmailStr

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "user@example.com"
            }
        }
    }  
class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "new_password": "newstrongpassword123",
                "confirm_password": "newstrongpassword123"
            }
        }
    }      