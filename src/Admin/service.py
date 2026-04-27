from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import func

from src.db.models import User, Orders, Reviews


class AdminService:
    async def get_dashboard_stats(self, session: AsyncSession) -> dict:
        users_count = (await session.exec(select(func.count()).select_from(User))).one()
        verified_users_count = (
            await session.exec(
                select(func.count()).select_from(User).where(User.is_verified.is_(True))
            )
        ).one()
        admins_count = (
            await session.exec(
                select(func.count()).select_from(User).where(User.role == "Admin")
            )
        ).one()

        order_statement = select(func.count()).select_from(Orders)
        orders_count = (await session.exec(order_statement)).one()
        reviews_count = (await session.exec(select(func.count()).select_from(Reviews))).one()

        return {
            "users_count": users_count,
            "verified_users_count": verified_users_count,
            "admins_count": admins_count,
            "orders_count": orders_count,
            "reviews_count": reviews_count,
        }

    async def get_users(self, session: AsyncSession) -> list[User]:
        statement = select(User).order_by(User.created_at.desc())
        result = await session.exec(statement)
        return result.all()

    async def get_user_by_id(self, user_id: str, session: AsyncSession) -> User:
        user = await session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user_role(self, user: User, role: str, session: AsyncSession) -> User:
        user.role = role
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update_user_verification(self, user: User, is_verified: bool, session: AsyncSession) -> User:
        user.is_verified = is_verified
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

