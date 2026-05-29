import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import get_current_user
from .service import CartService
from .schemas import CartItemCreate, CartItemUpdate, CartRead

cart_router = APIRouter()
cart_service = CartService()


@cart_router.get("/", response_model=CartRead)
async def get_cart(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await cart_service.get_cart(current_user.uid, session)


@cart_router.post("/items", response_model=CartRead, status_code=201)
async def add_item(
    data: CartItemCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await cart_service.add_item(current_user.uid, data, session)


@cart_router.patch("/items/{item_id}", response_model=CartRead)
async def update_item(
    item_id: uuid.UUID,
    data: CartItemUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await cart_service.update_item_quantity(current_user.uid, item_id, data.quantity, session)


@cart_router.delete("/items/{item_id}", response_model=CartRead)
async def remove_item(
    item_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await cart_service.remove_item(current_user.uid, item_id, session)


@cart_router.delete("/")
async def clear_cart(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await cart_service.clear_cart(current_user.uid, session)
