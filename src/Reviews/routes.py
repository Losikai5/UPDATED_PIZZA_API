from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.Reviews.service import ReviewsService
from .schemas import ReviewCreate, ReviewRead
from typing import List
from src.auth.dependencies import Rolechecker, get_current_user


user_role_checker = Depends(Rolechecker(["user","admin","staff"]))
reviews_router=APIRouter()
reviews_service = ReviewsService()

@reviews_router.get("/", response_model=List[ReviewRead])
async def read_reviews(session: AsyncSession = Depends(get_session)):
    
    return await reviews_service.Get_reviews(session)

@reviews_router.post("/", response_model=ReviewRead)
async def create_review(review: ReviewCreate, session: AsyncSession = Depends(get_session)):
    return await reviews_service.Create_review(review, session)

@reviews_router.get("/{review_uid}", response_model=ReviewRead, dependencies=[user_role_checker])
async def read_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    review = await reviews_service.Get_review_by_id(review_uid, session)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@reviews_router.post("/order/{order_uid}", response_model=ReviewRead, dependencies=[user_role_checker])
async def add_review_to_order(review: ReviewCreate, order_uid: str, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await reviews_service.add_review_to_order(review, order_uid, current_user.email, session)

@reviews_router.delete("/{review_uid}", dependencies=[user_role_checker])
async def delete_review(review_uid: str, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await reviews_service.delete_review_to_from_order(review_uid, current_user.email, session)
    return {"detail": "Review deleted successfully"}