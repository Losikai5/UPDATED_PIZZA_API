from fastapi import APIRouter, HTTPException, Depends
from .service import OrdersService
from .schemas import OrderCreate, OrderUpdate, OrderRead, OrderDetailRead
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import Rolechecker,get_current_user
from typing import List
from src.celery import (
    send_order_accepted_task,
    send_order_in_transit_task,
    send_order_completed_task
)
from src.db.models import Notification, NotificationType, OrderStatus
from pydantic import BaseModel
from src.db.models import NotificationType, Orders, Notification,OrderStatus
from src.celery import send_order_completed_task, send_order_confirmation_task,send_order_cancelled_task, send_order_accepted_task, send_order_in_transit_task,send_order_in_transit_task,send_order_completed_task   


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
    send_order_confirmation_task.delay(
        recipient=current_user.email,
        order_uid=str(create_order.uid),
        flavour=create_order.flavour,
        pizza_size=create_order.pizza_size,
        quantity=create_order.quantity,
        total_price=create_order.total_price,
    )

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


@Orders_router.post("/{order_id}/cancel", response_model=OrderRead, dependencies=[role])
async def cancel_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order_cancellation = await order_service.cancel_order(order_id, session)
    notification = Notification(
        user_uid=current_user.uid,
        message=f"Your order {order_cancellation.uid} has been cancelled successfully.",
        notification_type=NotificationType.order_cancelled,
    )
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
   
    send_order_cancelled_task.delay(
        recipient=current_user.email,
        order_uid=str(order_cancellation.uid),
        flavour=order_cancellation.flavour,
        pizza_size=order_cancellation.pizza_size,
        quantity=order_cancellation.quantity,
        total_price=order_cancellation.total_price,
    )
   
    return order_cancellation




@Orders_router.put("/{order_id}/accept", response_model=OrderRead, dependencies=[workers_role])
async def accept_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order_obj = await order_service.get_order_by_id(order_id, session)
    if order_obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order_obj.order_status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be accepted")
    order_obj.order_status = OrderStatus.in_transit
    session.add(order_obj)
    await session.commit()
    await session.refresh(order_obj)
    return order_obj





    
@Orders_router.put("/{order_id}/delivered", response_model=OrderRead, dependencies=[workers_role])
async def mark_order_as_delivered(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order_obj = await order_service.get_order_by_id(order_id, session)
    if order_obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order_obj.order_status != OrderStatus.in_transit:
        raise HTTPException(status_code=400, detail="Only orders that are in transit can be marked as delivered")
    order_obj.order_status = OrderStatus.completed
    session.add(order_obj)
    await session.commit()
    await session.refresh(order_obj)
    return order_obj




class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus

# Notification messages per status
STATUS_MESSAGES = {
    OrderStatus.order_accepted: "Your order {uid} has been accepted and is being prepared!",
    OrderStatus.in_transit: "Your order {uid} is on the way! Please be ready.",
    OrderStatus.completed: "Your order {uid} has been delivered. Enjoy your meal!",
}

# Celery tasks per status
STATUS_TASKS = {
    OrderStatus.order_accepted: send_order_accepted_task,
    OrderStatus.in_transit: send_order_in_transit_task,
    OrderStatus.completed: send_order_completed_task,
}

@Orders_router.patch("/{order_id}/status", response_model=OrderRead, dependencies=[workers_role])
async def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    updated_order = await order_service.update_order_status(order_id, payload.order_status, session)

    # Save notification to database if status has a message
    if payload in STATUS_MESSAGES:
        notification = Notification(
            user_uid=updated_order.user_id,
            message=STATUS_MESSAGES[payload].format(uid=updated_order.uid),
            notification_type=NotificationType.order_placed,
        )
        session.add(notification)
        await session.commit()

        # Fire the right Celery email task
        user = updated_order.user  # available because of selectin loading
        STATUS_TASKS[payload.order_status].delay(
            recipient=user.email,
            order_uid=str(updated_order.uid),
        )

    return updated_order