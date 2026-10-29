from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Enterprise
from backend.modules.enterprises.repository import EnterpriseRepository
from backend.modules.enterprises.schemas import EnterpriseCreate, EnterpriseUpdate


class EnterpriseService:
    def __init__(self, repo: EnterpriseRepository | None = None) -> None:
        self.repo = repo or EnterpriseRepository()

    async def list_enterprises(self, session: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Enterprise]:
        ents = await self.repo.list(session, limit=limit, offset=offset, only_suppliers=True)
        for ent in ents:
            self._populate_computed_fields(ent)
        return ents

    async def get_enterprise(self, session: AsyncSession, enterprise_id: int) -> Enterprise:
        ent = await self.repo.get(session, enterprise_id)
        if not ent:
            raise HTTPException(status_code=404, detail="Предприятие не найдено")
        self._populate_computed_fields(ent)
        return ent

    def _populate_computed_fields(self, ent: Enterprise) -> None:
        ent.products_count = len(ent.products)
        reviews = getattr(ent, "reviews_as_target", [])
        ent.review_count = len(reviews)
        if reviews:
            ent.rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
        else:
            ent.rating = 0.0

    async def create_enterprise(self, session: AsyncSession, data: EnterpriseCreate, user_id: int | None = None) -> Enterprise:
        ent = Enterprise(
            short_name=data.short_name,
            inn=data.inn,
            region=data.region,
            city=data.city,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            description=data.description,
        )
        await self.repo.create(session, ent)

        if user_id:
            await self.link_user_to_enterprise(session, ent.id, user_id)

        await session.flush()
        await session.refresh(ent)
        return ent

    async def link_user_to_enterprise(self, session: AsyncSession, enterprise_id: int, user_id: int) -> None:
        from backend.database.models import User
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = select(User).where(User.id == user_id).options(selectinload(User.enterprises))
        res = await session.execute(stmt)
        user = res.scalars().first()

        ent = await self.repo.get(session, enterprise_id)

        if not user or not ent:
            raise HTTPException(status_code=404, detail="Пользователь или предприятие не найдены")

        if ent not in user.enterprises:
            user.enterprises.append(ent)
            await session.flush()

    async def update_enterprise(self, session: AsyncSession, enterprise_id: int, data: EnterpriseUpdate) -> Enterprise:
        ent = await self.get_enterprise(session, enterprise_id)

        if data.short_name is not None:
            ent.short_name = data.short_name
        if data.inn is not None:
            ent.inn = data.inn
        if data.region is not None:
            ent.region = data.region
        if data.city is not None:
            ent.city = data.city
        if data.phone is not None:
            ent.phone = data.phone
        if data.email is not None:
            ent.email = str(data.email)
        if data.description is not None:
            ent.description = data.description

        await session.flush()
        await session.refresh(ent)
        return ent

    async def delete_enterprise(self, session: AsyncSession, enterprise_id: int) -> None:
        ent = await self.get_enterprise(session, enterprise_id)
        await self.repo.delete(session, ent)
