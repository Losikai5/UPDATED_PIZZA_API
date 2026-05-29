from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import RoleChecker, get_current_user
from .service import MenuService
from .schemas import MenuItemCreate, MenuItemRead, MenuItemUpdate
from typing import List

menu_router = APIRouter()
menu_service = MenuService()

# Only admins can manage the menu
admin_only = Depends(RoleChecker(["Admin"]))

# Anyone can view the menu — even unauthenticated users
@menu_router.get("/", response_model=List[MenuItemRead])
async def get_menu(session: AsyncSession = Depends(get_session)):
    return await menu_service.get_menu_items(session)

# Anyone can view a single menu item
@menu_router.get("/{item_id}", response_model=MenuItemRead)
async def get_menu_item(item_id: str, session: AsyncSession = Depends(get_session)):
    return await menu_service.get_menu_item_by_id(item_id, session)

# Only admins can create menu items
@menu_router.post("/", response_model=MenuItemRead, status_code=201, dependencies=[admin_only])
async def create_menu_item(
    data: MenuItemCreate,
    session: AsyncSession = Depends(get_session)
):
    return await menu_service.create_menu_item(data, session)

# Only admins can update menu items
@menu_router.patch("/{item_id}", response_model=MenuItemRead, dependencies=[admin_only])
async def update_menu_item(
    item_id: str,
    data: MenuItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    return await menu_service.update_menu_item(item_id, data, session)

# Only admins can delete menu items
@menu_router.delete("/{item_id}", dependencies=[admin_only])
async def delete_menu_item(item_id: str, session: AsyncSession = Depends(get_session)):
    return await menu_service.delete_menu_item(item_id, session)

# Only admins can toggle availability
@menu_router.patch("/{item_id}/toggle-availability", response_model=MenuItemRead, dependencies=[admin_only])
async def toggle_availability(item_id: str, session: AsyncSession = Depends(get_session)):
    return await menu_service.toggle_availability(item_id, session)