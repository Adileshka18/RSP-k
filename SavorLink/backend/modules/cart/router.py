from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user_id
from backend.modules.cart.schemas import CartItemCreate, CartItemUpdate, CartRead
from backend.database.session import get_session
from backend.modules.cart.service import CartService


router = APIRouter(prefix="/cart", tags=["cart"])
service = CartService()


@router.get("/me", response_model=CartRead)
async def get_my_cart(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    cart = await service.get_cart(session, user_id=user_id)
    cart.total_amount = service.calc_total_amount(cart)  # type: ignore[attr-defined]
    return cart


@router.post("/me/items", response_model=CartRead)
async def add_cart_item(
    payload: CartItemCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    cart = await service.add_item(session, user_id=user_id, data=payload)
    await session.commit()
    cart.total_amount = service.calc_total_amount(cart)  # type: ignore[attr-defined]
    return cart


@router.patch("/me/items/{item_id}", response_model=CartRead)
async def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    cart = await service.update_item(session, user_id=user_id, item_id=item_id, data=payload)
    await session.commit()
    cart.total_amount = service.calc_total_amount(cart)  # type: ignore[attr-defined]
    return cart


@router.delete("/me/items/{item_id}", response_model=CartRead)
async def delete_cart_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    cart = await service.delete_item(session, user_id=user_id, item_id=item_id)
    await session.commit()
    cart.total_amount = service.calc_total_amount(cart)  # type: ignore[attr-defined]
    return cart


@router.post("/me/clear", response_model=CartRead)
async def clear_cart(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    cart = await service.clear(session, user_id=user_id)
    await session.commit()
    cart.total_amount = service.calc_total_amount(cart)  # type: ignore[attr-defined]
    return cart
