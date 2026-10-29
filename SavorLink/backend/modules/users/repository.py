from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import User


class UserRepository:
    async def get(self, session: AsyncSession, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.enterprises))
        res = await session.execute(stmt)
        return res.scalars().first()

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.enterprises))
        res = await session.execute(stmt)
        return res.scalars().first()

    async def create(self, session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user
