from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException
from src.db.models import Address
from .schema import AddressCreate, AddressUpdate
import uuid


class AddressService:
    async def get_user_addresses(self, user_uid: uuid.UUID, session: AsyncSession):
        statement = select(Address).where(Address.user_uid == user_uid)
        result = await session.exec(statement)
        return result.all()

    async def get_address_by_id(self, address_uid: uuid.UUID, user_uid: uuid.UUID, session: AsyncSession):
        statement = select(Address).where(
            Address.uid == address_uid,
            Address.user_uid == user_uid,
        )
        result = await session.exec(statement)
        return result.first()

    async def create_address(self, user_uid: uuid.UUID, address_data: AddressCreate, session: AsyncSession):
        if address_data.is_default:
            await self._clear_default(user_uid, session)

        address = Address(user_uid=user_uid, **address_data.model_dump())
        session.add(address)
        await session.commit()
        await session.refresh(address)
        return address

    async def update_address(
        self,
        address_uid: uuid.UUID,
        user_uid: uuid.UUID,
        address_data: AddressUpdate,
        session: AsyncSession,
    ):
        address = await self.get_address_by_id(address_uid, user_uid, session)
        if address is None:
            raise HTTPException(status_code=404, detail="Address not found")

        if address_data.is_default:
            await self._clear_default(user_uid, session)

        for key, value in address_data.model_dump(exclude_unset=True).items():
            setattr(address, key, value)

        session.add(address)
        await session.commit()
        await session.refresh(address)
        return address

    async def delete_address(self, address_uid: uuid.UUID, user_uid: uuid.UUID, session: AsyncSession):
        address = await self.get_address_by_id(address_uid, user_uid, session)
        if address is None:
            raise HTTPException(status_code=404, detail="Address not found")

        await session.delete(address)
        await session.commit()

    async def set_default(self, address_uid: uuid.UUID, user_uid: uuid.UUID, session: AsyncSession):
        address = await self.get_address_by_id(address_uid, user_uid, session)
        if address is None:
            raise HTTPException(status_code=404, detail="Address not found")

        await self._clear_default(user_uid, session)
        address.is_default = True
        session.add(address)
        await session.commit()
        await session.refresh(address)
        return address

    async def _clear_default(self, user_uid: uuid.UUID, session: AsyncSession):
        statement = select(Address).where(
            Address.user_uid == user_uid,
            Address.is_default == True,
        )
        result = await session.exec(statement)
        current_default = result.first()
        if current_default:
            current_default.is_default = False
            session.add(current_default)
            await session.commit()
