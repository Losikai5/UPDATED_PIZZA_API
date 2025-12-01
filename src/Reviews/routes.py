from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.Reviews.service import ReviewsService
from .schemas import ReviewCreate, ReviewRead
from typing import List

reviews_router=APIRouter()
reviews_service = ReviewsService()

@reviews_router.get("/", response_model=List[ReviewRead])
async def read_reviews(session: AsyncSession = Depends(get_session)):
    
    return await reviews_service.Get_reviews(session)

@reviews_router.post("/", response_model=ReviewRead)
async def create_review(review: ReviewCreate, session: AsyncSession = Depends(get_session)):
    return await reviews_service.Create_review(review, session)