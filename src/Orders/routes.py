from fastapi import APIRouter, HTTPException, Depends
from .service import OrdersService
from .schemas import OrderCreate, OrderUpdate, OrderRead
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import Rolechecker
from typing import List

order_service = OrdersService()
Orders_router = APIRouter()
role = Depends(Rolechecker(["user", "admin", "staff"]))
workers_role = Depends(Rolechecker(["admin", "staff"]))

@Orders_router.get("/", response_model=List[OrderRead], dependencies=[workers_role])
async def read_orders(session: AsyncSession = Depends(get_session)):
    get_order = await order_service.get_orders(session)
    return get_order

@Orders_router.post("/", response_model=OrderRead, dependencies=[role])
async def create_order(order: OrderCreate, session: AsyncSession = Depends(get_session)):
    create_order = await order_service.create_order(order, session)
    return create_order  

@Orders_router.put("/{order_id}", response_model=OrderRead, dependencies=[role])
async def update_order(order_id: str, order: OrderUpdate, session: AsyncSession = Depends(get_session)):
    update_order = await order_service.update_order(order_id, order, session)
    return update_order

@Orders_router.delete("/{order_id}", dependencies=[role])
async def delete_order(order_id: str, session: AsyncSession = Depends(get_session)):
    remove_order = await order_service.delete_order(order_id, session)
    return remove_order

@Orders_router.get("/{order_uid}", response_model=OrderRead, dependencies=[workers_role])
async def read_orders_by_uid(order_uid: str, session: AsyncSession = Depends(get_session)):
    get_order_by_id = await order_service.get_order_by_id(order_uid, session)
    if get_order_by_id is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return get_order_by_id
