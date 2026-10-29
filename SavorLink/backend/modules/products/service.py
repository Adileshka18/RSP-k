from __future__ import annotations

from typing import List, Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Product
from backend.modules.products.repository import ProductRepository
from backend.modules.products.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, repo: ProductRepository | None = None) -> None:
        self.repo = repo or ProductRepository()

    async def list_products(
        self,
        session: AsyncSession,
        *,
        enterprise_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Product]:
        return await self.repo.list(session, enterprise_id=enterprise_id, limit=limit, offset=offset)

    async def list_products_by_enterprise_ids(
        self,
        session: AsyncSession,
        enterprise_ids: List[int],
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(Product.enterprise_id.in_(enterprise_ids))
            .options(
                selectinload(Product.enterprise),
                selectinload(Product.category),
            )
            .limit(limit)
            .offset(offset)
            .order_by(Product.id.desc())
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_product(self, session: AsyncSession, product_id: int) -> Product:
        product = await self.repo.get(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return product

    async def create_product(self, session: AsyncSession, data: ProductCreate, *, enterprise_id: int) -> Product:
        product = Product(
            name=data.name,
            description=data.description,
            price=data.price,
            min_order_qty=data.min_order_qty,
            quantity_in_stock=data.quantity_in_stock,
            enterprise_id=enterprise_id,
            category_id=data.category_id,
        )
        await self.repo.create(session, product)

        stmt = (
            select(Product)
            .where(Product.id == product.id)
            .options(
                selectinload(Product.category),
                selectinload(Product.enterprise),
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one()

    async def update_product(
        self,
        session: AsyncSession,
        product_id: int,
        data: ProductUpdate,
        *,
        enterprise_ids: List[int] | None = None,
    ) -> Product:
        product = await self.get_product(session, product_id)

        if enterprise_ids is not None and product.enterprise_id not in enterprise_ids:
            raise HTTPException(status_code=403, detail="У вас нет прав на редактирование этого товара")

        for field in ["name", "description", "price", "min_order_qty", "quantity_in_stock", "category_id"]:
            value = getattr(data, field)
            if value is not None:
                setattr(product, field, value)

        await session.flush()
        await session.refresh(product)

        stmt = (
            select(Product)
            .where(Product.id == product.id)
            .options(
                selectinload(Product.category),
                selectinload(Product.enterprise),
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one()

    async def delete_product(self, session: AsyncSession, product_id: int, *, enterprise_ids: List[int] | None = None) -> None:
        product = await self.get_product(session, product_id)

        if enterprise_ids is not None and product.enterprise_id not in enterprise_ids:
            raise HTTPException(status_code=403, detail="У вас нет прав на удаление этого товара")

        await self.repo.delete(session, product)
