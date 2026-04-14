from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.Reviews.service import ReviewsService
from src.Orders.service import OrdersService
from .schemas import ReviewCreate, ReviewRead
from typing import List
from src.auth.dependencies import Rolechecker,get_current_user


user_role_checker = Depends(Rolechecker(["user","Admin","Staff"]))
reviews_router=APIRouter()
reviews_service = ReviewsService()

@reviews_router.get("/", response_model=List[ReviewRead])
async def read_reviews(session: AsyncSession = Depends(get_session)):
    
    return await reviews_service.get_reviews(session)

@reviews_router.post("/{orders_id}", response_model=ReviewRead)
async def create_review(
    orders_id: str,
    review: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    order_obj = await OrdersService().get_order_by_id(orders_id, session)
    if order_obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if str(order_obj.user_id) != str(current_user.uid):
        raise HTTPException(status_code=403, detail="You can only review your own order")
    return await reviews_service.create_review(current_user.uid, orders_id, review, session)

@reviews_router.get("/{review_uid}", response_model=ReviewRead, dependencies=[user_role_checker])
async def read_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    review = await reviews_service.get_review_by_id(review_uid, session)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@reviews_router.delete("/{review_uid}", dependencies=[user_role_checker])
async def delete_review(review_uid: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
        reviews_obj = await reviews_service.get_review_by_id(review_uid, session)
        if reviews_obj is None:
            raise HTTPException(status_code=404, detail="Review not found")
        if str(reviews_obj.user_id) != str(current_user.uid):
            raise HTTPException(status_code=403, detail="You can only delete your own review")
        await reviews_service.delete_review(review_uid, session)
        return {"detail": "Review deleted successfully"}
@reviews_router.get("/user/{user_uid}", response_model=List[ReviewRead], dependencies=[user_role_checker])
async def read_reviews_by_user_id(user_uid: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if current_user.role != "Admin" and str(user_uid) != str(current_user.uid):
        raise HTTPException(status_code=403, detail="You can only view your own reviews")
    return await reviews_service.get_reviews_made_by_user_id(user_uid, session)
