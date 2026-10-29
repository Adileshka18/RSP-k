from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Product
from backend.modules.cart.repository import CartRepository
from backend.modules.products.repository import ProductRepository
from backend.modules.cart.schemas import CartItemCreate, CartItemUpdate


class CartService:
    def __init__(self, cart_repo: CartRepository | None = None, product_repo: ProductRepository | None = None) -> None:
        self.cart_repo = cart_repo or CartRepository()
        self.product_repo = product_repo or ProductRepository()

    async def get_or_create_cart(self, session: AsyncSession, *, user_id: int):
        cart = await self.cart_repo.get_by_user_id(session, user_id)
        if cart:
            return cart
        return await self.cart_repo.create(session, user_id)

    async def get_cart(self, session: AsyncSession, *, user_id: int):
        cart = await self.cart_repo.get_by_user_id(session, user_id)
        if not cart:
            cart = await self.cart_repo.create(session, user_id)
        return cart

    async def add_item(self, session: AsyncSession, *, user_id: int, data: CartItemCreate):
        cart = await self.get_or_create_cart(session, user_id=user_id)

        product = await self.product_repo.get(session, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        existing = await self.cart_repo.get_item_by_product(session, cart.id, data.product_id)
        if existing:
            existing.quantity += data.quantity
            await session.flush()
            return await self.get_cart(session, user_id=user_id)

        await self.cart_repo.add_item(session, cart.id, data.product_id, data.quantity)
        return await self.get_cart(session, user_id=user_id)

    async def update_item(self, session: AsyncSession, *, user_id: int, item_id: int, data: CartItemUpdate):
        cart = await self.get_cart(session, user_id=user_id)
        item = await self.cart_repo.get_item(session, cart.id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Позиция корзины не найдена")
        item.quantity = data.quantity
        await session.flush()
        return await self.get_cart(session, user_id=user_id)

    async def delete_item(self, session: AsyncSession, *, user_id: int, item_id: int):
        cart = await self.get_cart(session, user_id=user_id)
        item = await self.cart_repo.get_item(session, cart.id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Позиция корзины не найдена")
        await self.cart_repo.delete_item(session, item)
        await session.flush()
        return await self.get_cart(session, user_id=user_id)

    async def clear(self, session: AsyncSession, *, user_id: int):
        cart = await self.get_cart(session, user_id=user_id)
        await self.cart_repo.clear(session, cart.id)
        await session.flush()
        return await self.get_cart(session, user_id=user_id)

    @staticmethod
    def calc_total_amount(cart) -> Decimal:
        total = Decimal("0")
        for item in getattr(cart, "items", []) or []:
            price = getattr(getattr(item, "product", None), "price", None)
            if price is None:
                continue
            total += Decimal(str(price)) * Decimal(item.quantity)
        return total
