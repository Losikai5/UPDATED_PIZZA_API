from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends
from src.db.models import Reviews
from .schemas import ReviewCreate
from sqlmodel import select, desc

class ReviewsService:
    async def Get_reviews(self, session: AsyncSession):
        statement = select(Reviews).order_by(desc(Reviews.Created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def Get_review_by_id(self, uid: str, session: AsyncSession):
        statement = select(Reviews).where(Reviews.uid == uid)
        result = await session.exec(statement)
        return result.first()
    
    async def Create_review(self, review_data: ReviewCreate, session: AsyncSession):
             new_review = review_data.model_dump()
             review = Reviews(**new_review)  # Create the model instance
             session.add(review)  # Add the instance, not unpack it with **
             await session.commit()
             await session.refresh(review)
             return review