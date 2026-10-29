from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Enterprise, User, UserRole


class EnterpriseRepository:
    async def list(self, session: AsyncSession, *, limit: int = 50, offset: int = 0, only_suppliers: bool = False) -> Sequence[Enterprise]:
        stmt = (
            select(Enterprise)
            .options(
                selectinload(Enterprise.products),
                selectinload(Enterprise.users),
                selectinload(Enterprise.reviews_as_target),
            )
        )

        if only_suppliers:
            stmt = stmt.join(Enterprise.users).where(User.role == UserRole.SUPPLIER).distinct()

        stmt = stmt.order_by(Enterprise.id.desc()).limit(limit).offset(offset)
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get(self, session: AsyncSession, enterprise_id: int) -> Enterprise | None:
        stmt = (
            select(Enterprise)
            .options(
                selectinload(Enterprise.products),
                selectinload(Enterprise.users),
                selectinload(Enterprise.reviews_as_target),
            )
            .where(Enterprise.id == enterprise_id)
        )
        res = await session.execute(stmt)
        return res.scalars().first()

    async def create(self, session: AsyncSession, enterprise: Enterprise) -> Enterprise:
        session.add(enterprise)
        await session.flush()
        await session.refresh(enterprise)
        return enterprise

    async def delete(self, session: AsyncSession, enterprise: Enterprise) -> None:
        await session.delete(enterprise)
