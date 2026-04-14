from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from src.db.models import Reviews,User,Orders
from .schemas import ReviewCreate
from sqlmodel import select, desc
from sqlalchemy.exc import IntegrityError

class ReviewsService:
    async def get_reviews(self, session: AsyncSession):
        statement = select(Reviews).order_by(desc(Reviews.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def get_review_by_id(self, uid: str, session: AsyncSession):
        statement = select(Reviews).where(Reviews.uid == uid)
        result = await session.exec(statement)
        return result.first()
    
    async def create_review(self,user_id:str,orders_id:str, review_data: ReviewCreate, session: AsyncSession):
        try:
            new_review = review_data.model_dump()
            new_review["user_id"] = user_id
            new_review["orders_id"] = orders_id
            review = Reviews(**new_review)
            session.add(review)
            await session.commit()
            await session.refresh(review)
            return review
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Invalid review data")

    async def delete_review(self, review_uid: str, session: AsyncSession):
        review = await self.get_review_by_id(review_uid, session)

        if not review:
            raise HTTPException(detail="Review not found", status_code=404)
        await session.delete(review)
        await session.commit()
        return {"detail": "Review deleted successfully"}

    async def get_reviews_made_by_user_id(self,user_uid:str,session:AsyncSession):
               statement = select(Reviews).where(Reviews.user_id == user_uid).order_by(desc(Reviews.created_at))
               result = await session.exec(statement)
               return result.all()