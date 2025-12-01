from pydantic import BaseModel
from datetime import datetime
import uuid


class SignupModel(BaseModel):
    username:str
    first_name:str
    last_name:str
    email:str
    role:str 
    password:str 
    class Config:
        orm_mode = True  
        json_schema_extra = {
            "example":{
                    "username":"johndoe",
                    "first_name":"John",
                    "last_name":"Doe",
                    "email":"johndoe@example.com",
                    "role":"user",
                    "password":"strongpassword123"
            }
        }

class SignupResponse(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    email: str
    role: str
    created_at: datetime

class LoginModel(BaseModel):
     email: str
     password:str 

     class Config:
        from_attributes = True  
        json_schema_extra = {
            "example":{
                    "email":"johndoe@example.com",
                    "password":"strongpassword123"
            }
        }

 