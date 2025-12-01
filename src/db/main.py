from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config
from src.db.models import User,Orders,Reviews

engine= create_async_engine(Config.DATABASE_URL,echo=True)
async def init_db():
    async with engine.begin() as con:
        await con.run_sync(SQLModel.metadata.create_all)
local_session = sessionmaker(bind=engine,class_= AsyncSession,expire_on_commit=False)  
async def get_session():
    async with local_session() as session:
        yield session      