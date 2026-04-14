from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    comment: str
    rating: int = Field(ge=0, le=5)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "comment": "Great pizza, loved the crust!",
                "rating": 4
            }   
        }  

class ReviewRead(BaseModel):
    uid: uuid.UUID
    comment: str
    rating: int = Field(ge=0, le=5)
    created_at: datetime

          