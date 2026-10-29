from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Enterprise, EnterpriseFavorite, Favorite, Product


class FavoriteService:
    async def list_favorite_products(self, session: AsyncSession, user_id: int) -> Sequence[Product]:
        stmt = (
            select(Product)
            .join(Favorite, Favorite.product_id == Product.id)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Product.enterprise),
                selectinload(Product.category),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def add_favorite_product(self, session: AsyncSession, user_id: int, product_id: int) -> None:
        stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        res = await session.execute(stmt)
        if res.scalars().first():
            return

        fav = Favorite(user_id=user_id, product_id=product_id)
        session.add(fav)
        await session.flush()

    async def remove_favorite_product(self, session: AsyncSession, user_id: int, product_id: int) -> None:
        stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        await session.execute(stmt)
        await session.flush()

    async def list_favorite_suppliers(self, session: AsyncSession, user_id: int) -> Sequence[Enterprise]:
        stmt = (
            select(Enterprise)
            .join(EnterpriseFavorite, EnterpriseFavorite.enterprise_id == Enterprise.id)
            .where(EnterpriseFavorite.user_id == user_id)
            .options(
                selectinload(Enterprise.products).selectinload(Product.category),
                selectinload(Enterprise.products).selectinload(Product.enterprise),
                selectinload(Enterprise.reviews_as_target),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def add_favorite_supplier(self, session: AsyncSession, user_id: int, enterprise_id: int) -> None:
        stmt = select(EnterpriseFavorite).where(
            EnterpriseFavorite.user_id == user_id,
            EnterpriseFavorite.enterprise_id == enterprise_id,
        )
        res = await session.execute(stmt)
        if res.scalars().first():
            return

        fav = EnterpriseFavorite(user_id=user_id, enterprise_id=enterprise_id)
        session.add(fav)
        await session.flush()

    async def remove_favorite_supplier(self, session: AsyncSession, user_id: int, enterprise_id: int) -> None:
        stmt = delete(EnterpriseFavorite).where(
            EnterpriseFavorite.user_id == user_id,
            EnterpriseFavorite.enterprise_id == enterprise_id,
        )
        await session.execute(stmt)
        await session.flush()
