from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import MenuItem, MenuItemSize
from .schemas import MenuItemCreate, MenuItemUpdate
from sqlmodel import select, desc
from fastapi import HTTPException

class MenuService:
     async def create_menu_item(self,data:MenuItemCreate,session:AsyncSession):
          menu_item = MenuItem(**data.model_dump(exclude={"sizes"}))
          session.add(menu_item)
          await session.commit()
          await session.refresh(menu_item)

          for size_data in data.sizes:
              size = MenuItemSize(
                  menu_item_uid=menu_item.uid,
                  pizza_size=size_data.pizza_size.value,
                  price=size_data.price,
              )
              session.add(size)
          await session.commit()
          await session.refresh(menu_item)
          return menu_item

     async def get_menu_items(self, session: AsyncSession):
          statement = select(MenuItem).order_by(desc(MenuItem.created_at))
          result = await session.exec(statement)
          return result.all()
     async def get_menu_item_by_id(self, uid: str, session: AsyncSession) -> MenuItem:
        item = await session.get(MenuItem, uid)
        if item is None:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return item
     async def update_menu_item(self, uid: str, data: MenuItemUpdate, session: AsyncSession) -> MenuItem:
        item = await self.get_menu_item_by_id(uid, session)
        
        # Only update fields that were actually sent in the request
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item    
     async def delete_menu_item(self, uid: str, session: AsyncSession) -> dict:
        item = await self.get_menu_item_by_id(uid, session)
        await session.delete(item)
        await session.commit()
        return {"message": f"Menu item {item.name} deleted successfully"}
     
     #helps change the aviability of an item to either available o not avialable
     async def toggle_availability(self, uid: str, session: AsyncSession) -> MenuItem:
        item = await self.get_menu_item_by_id(uid, session)
        # Flip the availability — if True make it False, if False make it True
        item.is_available = not item.is_available
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item  