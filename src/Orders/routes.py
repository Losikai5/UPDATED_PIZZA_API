from fastapi import APIRouter, HTTPException, Depends
from .service import OrdersService
from .schemas import OrderCreate, OrderUpdate, OrderRead, OrderDetailRead
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import Rolechecker,get_current_user
from typing import List
from src.db.models import Orders


order_service = OrdersService()
Orders_router = APIRouter()
role = Depends(Rolechecker(["user", "Admin", "Staff"]))
workers_role = Depends(Rolechecker(["Admin", "Staff"]))

@Orders_router.get("/", response_model=List[OrderRead], dependencies=[workers_role])
async def read_orders(session: AsyncSession = Depends(get_session)):
    get_order = await order_service.get_orders(session)
    return get_order

@Orders_router.post("/", response_model=OrderRead, dependencies=[role])
async def create_order(order: OrderCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    
    create_order = await order_service.create_order(order, session, current_user.uid)
    return create_order  

@Orders_router.put("/{order_id}", response_model=OrderRead, dependencies=[role])
async def update_order(order_id: str, order: OrderUpdate, session: AsyncSession = Depends(get_session),current_user =Depends(get_current_user)):
    order_obj =  await session.get(Orders, order_id)
    if order_obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "Admin" and str(order_obj.user_id ) != str(current_user.uid):
        raise HTTPException(403,detail="You are not allowed to update this order")
     
    
    update_order = await order_service.update_order(order_id, order, session)
    return update_order

@Orders_router.delete("/{order_id}", dependencies=[role])
async def delete_order(order_id: str,session: AsyncSession = Depends(get_session),current_user=Depends(get_current_user),):
    order_obj = await order_service.get_order_by_id(order_id, session)
    if order_obj is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "Admin" and str(order_obj.user_id) != str(current_user.uid):
        raise HTTPException(status_code=403, detail="You can only delete your own order")

    remove_order = await order_service.delete_order(order_id, session)
    return remove_order

@Orders_router.get("/{order_uid}", response_model=OrderDetailRead, dependencies=[workers_role])
async def read_orders_by_uid(order_uid: str, session: AsyncSession = Depends(get_session)):
    get_order_by_id = await order_service.get_order_by_id(order_uid, session)
    if get_order_by_id is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return get_order_by_id

@Orders_router.get("/user/{user_id}", response_model=List[OrderRead], dependencies=[role])
async def read_orders_by_user_id(user_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if current_user.role != "Admin" and str(user_id) != str(current_user.uid):
        raise HTTPException(status_code=403, detail="You can only view your own orders")
    get_orders_by_user_id = await order_service.get_orders_by_user_id(user_id, session)
    return get_orders_by_user_id
