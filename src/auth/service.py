from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.models import User
from sqlmodel import select
from fastapi import HTTPException, status
from .schemas import SignupModel
from .utils import create_hash


class Auth_service:
    async def get_user_by_email(self,email:str,session:AsyncSession):
         statement = select(User).where(User.email == email)
         result = await session.exec(statement)
         return result.first()
         
    async def check_user_exists(self,email:str,session:AsyncSession):
         user = await self.get_user_by_email(email,session)
         if user is not None:
              raise HTTPException(status_code=403,detail=" User exists")
    

    async def create_user(self, user_data: SignupModel, session: AsyncSession):
        new_user = User(**user_data.model_dump(exclude={'password'}),
                       password_hash=create_hash(user_data.password))
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    async def update_user(self,user:User,user_data:dict,session:AsyncSession):
         for key,value in user_data.items():
              setattr(user,key,value)
         session.add(user)
         await session.commit()
         await session.refresh(user)
         return user
          