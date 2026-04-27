from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.Admin.schemas import (
    AdminDashboardStatsResponse,
    AdminUserRead,
    AdminUserRoleUpdate,
    AdminUserVerifyUpdate,
)
from src.Admin.service import AdminService
from src.auth.dependencies import Rolechecker
from src.db.main import get_session


admin_router = APIRouter()
admin_service = AdminService()
admin_only = Depends(Rolechecker(["Admin"]))
allowed_roles = {"user", "Admin", "Staff"}


@admin_router.get("/dashboard", response_model=AdminDashboardStatsResponse, dependencies=[admin_only])
async def get_admin_dashboard(session: AsyncSession = Depends(get_session)):
    return await admin_service.get_dashboard_stats(session)


@admin_router.get("/users", response_model=list[AdminUserRead], dependencies=[admin_only])
async def get_users(session: AsyncSession = Depends(get_session)):
    users = await admin_service.get_users(session)
    return users


@admin_router.get("/users/{user_id}", response_model=AdminUserRead, dependencies=[admin_only])
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    user = await admin_service.get_user_by_id(user_id, session)
    return user


@admin_router.patch("/users/{user_id}/role", response_model=AdminUserRead, dependencies=[admin_only])
async def set_user_role(
    user_id: str,
    payload: AdminUserRoleUpdate,
    session: AsyncSession = Depends(get_session),
):
    if payload.role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = await admin_service.get_user_by_id(user_id, session)
    return await admin_service.update_user_role(user, {"role": payload.role}, session)


@admin_router.patch("/users/{user_id}/verify", response_model=AdminUserRead, dependencies=[admin_only])
async def set_user_verification(
    user_id: str,
    payload: AdminUserVerifyUpdate,
    session: AsyncSession = Depends(get_session),
):
    user = await admin_service.get_user_by_id(user_id, session)
    return await admin_service.update_user_verification(user, payload.is_verified, session)
