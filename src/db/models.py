from sqlmodel import SQLModel, Field, Column, func
import uuid
from datetime import datetime 
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False))
    username: str
    first_name: str
    last_name: str
    email: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = Field(default=False)
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    
    def __repr__(self):
        return f"{self.username} with email:{self.email} with the role of {self.role}"
    

class Orders(SQLModel, table=True):
    __tablename__ = "orders"
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False))
    quantity: int
    order_status: str
    pizza_size: str
    flavour: str
    placed_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    
    def __repr__(self):
        return f"The pizza is {self.order_status} and the size is {self.pizza_size}"




class Reviews(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False))
    comment: str
    rating: int = Field(sa_column=Column(pg.INTEGER, nullable=False))  
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=func.now()))
    
    def __repr__(self):
        return f"The comment is {self.comment} and it was created at {self.created_at}"

