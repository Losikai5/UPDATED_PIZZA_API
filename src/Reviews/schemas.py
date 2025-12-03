from pydantic import BaseModel,Field
import uuid
from datetime import datetime
class ReviewCreate(BaseModel):
      Comment: str
      Rating: int = Field(lt=5)
      class Config:
          from_attributes = True
          json_schema_extra = {
              "example":{
                    
                    "Comment":"Great pizza, loved the crust!",
                    "Rating":4
                    
                }   
            }  
class ReviewRead(BaseModel):
      uid: uuid.UUID
      Comment: str
      Rating: int = Field(lt=5)
      Created_at: datetime
          