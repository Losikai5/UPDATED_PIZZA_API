from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException
from src.db.models import Reviews
from .schemas import ReviewCreate
from sqlmodel import select, desc
from src.auth.service import Auth_service
from src.Orders.service import OrdersService
auth_service = Auth_service()
orders_service = OrdersService()

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
             review = Reviews(**new_review)  
             session.add(review) 
             await session.commit()
             await session.refresh(review)
             return review
    async def add_review_to_order(self, review_data:ReviewCreate, order_uid: str, user_email: str, session: AsyncSession):
              try:
                  order = await orders_service.Get_order_by_id(order_uid, session)
                  user  = await auth_service.get_user_by_email(user_email, session)
                  reviews = Reviews(**review_data.model_dump())
                  if not order:
                    raise HTTPException(status_code=404, detail="Order not found")
                  if not user:
                    raise HTTPException(status_code=404, detail="User not found")
              
                  reviews.user = user
                  reviews.order = order
                  session.add(reviews)
                  await session.commit()
                  await session.refresh(reviews)
                  return reviews
              except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
              
    async def delete_review_to_from_order(self, review_uid: str, user_email: str, session: AsyncSession):
       
        user = await auth_service.get_user_by_email(user_email, session)
        review = await self.Get_review_by_id(review_uid, session)

        if not review or (review.user is not user):
            raise HTTPException(detail="Cannot delete this review",status_code=403)
        session.delete(review)
        await session.commit()   
        return {"detail":"Review deleted successfully"}           
              
