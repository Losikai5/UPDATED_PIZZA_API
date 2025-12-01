from pydantic import BaseModel
import uuid
from datetime import datetime
class ReviewCreate(BaseModel):
      Comment: str
      class Config:
          from_attributes = True
          json_schema_extra = {
              "example":{
                    
                    "Comment":"Great pizza, loved the crust!"
                    
                }   
            }  
class ReviewRead(BaseModel):
      uid: uuid.UUID
      Comment: str
      Created_at: datetime
          