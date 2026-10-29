from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Order, OrderHistory, OrderItem, OrderStatus, Product, UserRole
from backend.modules.orders.repository import OrderRepository
from backend.modules.products.repository import ProductRepository
from backend.modules.orders.schemas import OrderCreate, OrderUpdateStatus


_EAGER_OPTIONS = [
    selectinload(Order.buyer_enterprise),
    selectinload(Order.seller_enterprise),
    selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.category),
    selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.enterprise),
    selectinload(Order.payment),
    selectinload(Order.documents),
]


class OrderService:
    def __init__(
        self,
        repo: OrderRepository | None = None,
        product_repo: ProductRepository | None = None,
    ) -> None:
        self.repo = repo or OrderRepository()
        self.product_repo = product_repo or ProductRepository()

    async def list_orders(
        self, session: AsyncSession, *, limit: int = 50, offset: int = 0
    ) -> Sequence[Order]:
        return await self.repo.list(session, limit=limit, offset=offset)

    async def list_orders_for_buyer(
        self,
        session: AsyncSession,
        *,
        buyer_enterprise_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.buyer_enterprise_id == buyer_enterprise_id)
            .options(*_EAGER_OPTIONS)
            .order_by(Order.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def list_orders_for_seller(
        self,
        session: AsyncSession,
        *,
        seller_enterprise_ids: list[int],
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.seller_enterprise_id.in_(seller_enterprise_ids))
            .options(*_EAGER_OPTIONS)
            .order_by(Order.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_order(self, session: AsyncSession, order_id: int) -> Order:
        order = await self.repo.get(session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return order

    async def create_order(
        self,
        session: AsyncSession,
        data: OrderCreate,
        *,
        buyer_enterprise_id: int,
        buyer_user_id: int | None = None,
    ) -> Order:
        if not buyer_enterprise_id:
            raise HTTPException(status_code=400, detail="Необходимо указать предприятие покупателя")

        quantity_by_product: dict[int, int] = {}
        for item in data.items:
            quantity_by_product[item.product_id] = quantity_by_product.get(item.product_id, 0) + item.quantity

        order = Order(
            status=OrderStatus.CREATED,
            buyer_enterprise_id=buyer_enterprise_id,
            seller_enterprise_id=data.seller_enterprise_id,
            items=[],
        )

        total = Decimal("0")
        for product_id, quantity in quantity_by_product.items():
            product = await self.product_repo.get(session, product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Товар не найден: {product_id}")
            if product.enterprise_id != data.seller_enterprise_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Товар {product.id} не принадлежит выбранному поставщику",
                )
            if product.min_order_qty and quantity < product.min_order_qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Для товара {product.id} требуется минимум {product.min_order_qty} шт.",
                )
            if product.quantity_in_stock is not None and quantity > product.quantity_in_stock:
                raise HTTPException(
                    status_code=409,
                    detail=f"Недостаточно товара на складе для позиции {product.id}",
                )

            price = Decimal(str(product.price))
            total += price * Decimal(quantity)
            order.items.append(
                OrderItem(
                    product_id=product_id,
                    quantity=quantity,
                    price=price,
                )
            )

        order.total_amount = total
        session.add(order)
        await session.flush()

        if buyer_user_id is not None:
            session.add(
                OrderHistory(
                    order_id=order.id,
                    status=OrderStatus.CREATED,
                    changed_by=buyer_user_id,
                )
            )
            await session.flush()

        return await self._reload_order(session, order.id)

    async def update_status(
        self,
        session: AsyncSession,
        order_id: int,
        data: OrderUpdateStatus,
        *,
        actor_user_id: int,
        actor_role: UserRole,
        actor_enterprise_ids: list[int] | None = None,
    ) -> Order:
        order = await self.get_order(session, order_id)
        new_status = data.status

        if new_status == order.status:
            return order

        self._validate_status_change(
            order=order,
            new_status=new_status,
            actor_role=actor_role,
            actor_enterprise_ids=actor_enterprise_ids or [],
        )

        if new_status == OrderStatus.CONFIRMED:
            await self._decrease_stock_for_order(session, order.id)

        order.status = new_status
        session.add(
            OrderHistory(
                order_id=order.id,
                status=new_status,
                changed_by=actor_user_id,
            )
        )
        await session.flush()
        return await self._reload_order(session, order.id)

    async def _reload_order(self, session: AsyncSession, order_id: int) -> Order:
        stmt = select(Order).where(Order.id == order_id).options(*_EAGER_OPTIONS)
        result = await session.execute(stmt)
        return result.scalar_one()

    async def _decrease_stock_for_order(self, session: AsyncSession, order_id: int) -> None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        result = await session.execute(stmt)
        order = result.scalar_one()
        for item in order.items:
            product = item.product
            if not product:
                raise HTTPException(status_code=404, detail=f"Товар не найден: {item.product_id}")
            if product.quantity_in_stock is None:
                continue
            if product.quantity_in_stock < item.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=f"Недостаточно товара на складе для позиции {product.id}",
                )
            product.quantity_in_stock -= item.quantity
            session.add(product)

    @staticmethod
    def _validate_status_change(
        *,
        order: Order,
        new_status: OrderStatus,
        actor_role: UserRole,
        actor_enterprise_ids: list[int],
    ) -> None:
        if new_status in {OrderStatus.CONFIRMED, OrderStatus.CANCELLED}:
            if order.status != OrderStatus.CREATED:
                raise HTTPException(
                    status_code=409,
                    detail="Подтвердить или отменить можно только заказы в статусе CREATED",
                )
            if actor_role != UserRole.SUPPLIER:
                raise HTTPException(status_code=403, detail="Подтвердить или отменить заказ может только поставщик")
            if order.seller_enterprise_id not in actor_enterprise_ids:
                raise HTTPException(status_code=403, detail="Заказ не относится к вашей организации")
            return

        if new_status == OrderStatus.COMPLETED:
            if order.status not in {OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS}:
                raise HTTPException(status_code=409, detail="Завершить можно только подтвержденный заказ")
            if actor_role != UserRole.BUYER:
                raise HTTPException(status_code=403, detail="Завершить заказ может только покупатель")
            if order.buyer_enterprise_id not in actor_enterprise_ids:
                raise HTTPException(status_code=403, detail="Заказ не относится к вашей организации")
            return

        raise HTTPException(status_code=400, detail="Переход в указанный статус запрещен")
