from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from src.db.models import Orders
from .schemas import OrderCreate, OrderUpdate 
from sqlmodel import select, desc

class OrdersService:
    async def get_orders(self, session: AsyncSession):
        statement = select(Orders).order_by(desc(Orders.placed_at))
        result = await session.exec(statement)
        return result.all()
    
    async def get_order_by_id(self, uid: str, session: AsyncSession):
        statement = select(Orders).where(Orders.uid == uid)
        result = await session.exec(statement)
        return result.first()

    async def create_order(self, order_data: OrderCreate, session: AsyncSession, user_id):
        existing_order_statement = select(Orders).where(
            Orders.user_id == user_id,
            Orders.order_status == "pending",
        )
        existing_order_result = await session.exec(existing_order_statement)
        existing_order = existing_order_result.first()
        if existing_order is not None:
            raise HTTPException(status_code=400, detail="You already have a pending order. Complete it before creating a new one.")

        new_order = order_data.model_dump()
        new_order["user_id"] = user_id
        new_order["order_status"] = "pending"
        order = Orders(**new_order)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order
    
    async def update_order(self, uid: str, order_data: OrderUpdate, session: AsyncSession):
        order_update = await self.get_order_by_id(uid, session)
        if order_update is None:
            raise HTTPException(status_code=404, detail="Order is not available, please create an order")
        
        # Update only the fields that were provided in the request
        update_data = order_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(order_update, key, value)
        
        session.add(order_update)
        await session.commit()
        await session.refresh(order_update)
        return order_update

    async def delete_order(self, uid: str, session: AsyncSession):
        remove_order = await self.get_order_by_id(uid, session)
        if remove_order is not None:
            await session.delete(remove_order)
            await session.commit()
            return "Order removed successfully"
        raise HTTPException(status_code=404, detail="Order is not available, please create an order")
    async def get_orders_by_user_id(self, user_id: str, session: AsyncSession):
        statement = select(Orders).where(Orders.user_id == user_id).order_by(desc(Orders.placed_at))
        result = await session.exec(statement)
        return result.all()