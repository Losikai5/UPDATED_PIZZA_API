from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config


engine= create_async_engine(Config.DATABASE_URL,echo=True)
local_session = sessionmaker(bind=engine,class_= AsyncSession,expire_on_commit=False)  
async def get_session():
    async with local_session() as session:
        yield session      