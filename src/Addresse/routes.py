from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from src.db.main import get_session
from src.auth.dependencies import get_current_user, Rolechecker
from .service import AddressService
from .schema import AddressCreate, AddressUpdate, AddressRead

address_router = APIRouter()
address_service = AddressService()
role = Depends(Rolechecker(["user", "Admin", "Staff"]))


@address_router.get("/", response_model=List[AddressRead], dependencies=[role])
async def get_my_addresses(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await address_service.get_user_addresses(current_user.uid, session)


@address_router.post("/", response_model=AddressRead, status_code=201, dependencies=[role])
async def create_address(
    address_data: AddressCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await address_service.create_address(current_user.uid, address_data, session)


@address_router.get("/{address_id}", response_model=AddressRead, dependencies=[role])
async def get_address(
    address_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    address = await address_service.get_address_by_id(address_id, current_user.uid, session)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@address_router.put("/{address_id}", response_model=AddressRead, dependencies=[role])
async def update_address(
    address_id: uuid.UUID,
    address_data: AddressUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await address_service.update_address(address_id, current_user.uid, address_data, session)


@address_router.delete("/{address_id}", status_code=204, dependencies=[role])
async def delete_address(
    address_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await address_service.delete_address(address_id, current_user.uid, session)


@address_router.patch("/{address_id}/default", response_model=AddressRead, dependencies=[role])
async def set_default_address(
    address_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await address_service.set_default(address_id, current_user.uid, session)
