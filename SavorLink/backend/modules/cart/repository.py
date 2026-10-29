from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Cart, CartItem, Product


class CartRepository:
    async def get_by_user_id(self, session: AsyncSession, user_id: int) -> Cart | None:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product)
                .selectinload(Product.enterprise),
                selectinload(Cart.items)
                .selectinload(CartItem.product)
                .selectinload(Product.category),
            )
        )

        res = await session.execute(stmt)
        return res.scalars().first()

    async def create(self, session: AsyncSession, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.flush()
        await session.refresh(cart)
        return cart

    async def get_item(self, session: AsyncSession, cart_id: int, item_id: int) -> CartItem | None:
        stmt = (
            select(CartItem)
            .where(
                CartItem.id == item_id,
                CartItem.cart_id == cart_id,
            )
            .options(
                selectinload(CartItem.product)
                .selectinload(Product.enterprise),
                selectinload(CartItem.product)
                .selectinload(Product.category),
            )
        )

        res = await session.execute(stmt)
        return res.scalars().first()

    async def get_item_by_product(self, session: AsyncSession, cart_id: int, product_id: int) -> CartItem | None:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
        res = await session.execute(stmt)
        return res.scalars().first()

    async def add_item(self, session: AsyncSession, cart_id: int, product_id: int, quantity: int) -> CartItem:
        item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def delete_item(self, session: AsyncSession, item: CartItem) -> None:
        await session.delete(item)

    async def clear(self, session: AsyncSession, cart_id: int) -> None:
        await session.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
