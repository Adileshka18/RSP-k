from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Order, OrderItem, Product


class OrderRepository:
    async def list(self, session: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Order]:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.buyer_enterprise),
                selectinload(Order.seller_enterprise),
                selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.category),
                selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.enterprise),
                selectinload(Order.payment),
                selectinload(Order.documents),
            )
            .order_by(Order.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get(self, session: AsyncSession, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.buyer_enterprise),
                selectinload(Order.seller_enterprise),
                selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.category),
                selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.enterprise),
                selectinload(Order.payment),
                selectinload(Order.documents),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().first()

    async def create(self, session: AsyncSession, order: Order) -> Order:
        session.add(order)
        await session.flush()
        stmt = (
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.buyer_enterprise),
                selectinload(Order.seller_enterprise),
                selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.category),
                selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.enterprise),
                selectinload(Order.payment),
                selectinload(Order.documents),
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one()
