from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException
from src.db.models import Orders
from .schemas import OrderCreate, OrderUpdate 
from sqlmodel import select, desc

class OrdersService:
    async def Get_orders(self, session: AsyncSession):
        statement = select(Orders).order_by(desc(Orders.placed_at))
        result = await session.exec(statement)
        return result.all()
    
    async def Get_order_by_id(self, uid: str, session: AsyncSession):
        statement = select(Orders).where(Orders.uid == uid)
        result = await session.exec(statement)
        return result.first()
    
    async def Get_order_by_user(self, user_id: str, session: AsyncSession):
        statement = select(Orders).where(Orders.user_id == user_id).order_by(desc(Orders.placed_at))
        result = await session.exec(statement)
        return result.first()
    async def create_order(self, order_data: OrderCreate,user_id: str ,session: AsyncSession):
        new_order = order_data.model_dump()
        order = Orders(**new_order, user_id=user_id)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order
    
    async def update_order(self, uid: str, order_data: OrderUpdate, session: AsyncSession):
        order_update = await self.Get_order_by_id(uid, session)
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
        remove_order = await self.Get_order_by_id(uid, session)
        if remove_order is not None:
            await session.delete(remove_order)
            await session.commit()
            return "Order removed successfully"
        raise HTTPException(status_code=404, detail="Order is not available, please create an order")