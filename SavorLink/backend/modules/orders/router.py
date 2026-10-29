from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user
from backend.database.models import UserRole
from backend.modules.orders.schemas import OrderCreate, OrderListItem, OrderRead, OrderUpdateStatus
from backend.database.session import get_session
from backend.modules.orders.service import OrderService


router = APIRouter(prefix="/orders", tags=["orders"])
service = OrderService()


@router.get("", response_model=List[OrderListItem])
async def list_orders(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    orders = await service.list_orders(session, limit=limit, offset=offset)
    return orders


@router.get("/my-as-buyer", response_model=List[OrderListItem])
async def list_my_orders_as_buyer(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if user.role != UserRole.BUYER:
        raise HTTPException(status_code=403, detail="К заказам покупателя могут обращаться только покупатели")
    if not user.enterprise_id:
        return []

    orders = await service.list_orders_for_buyer(
        session,
        buyer_enterprise_id=user.enterprise_id,
        limit=limit,
        offset=offset,
    )
    return orders


@router.get("/my-as-supplier", response_model=List[OrderListItem])
async def list_my_orders_as_supplier(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if user.role != UserRole.SUPPLIER:
        raise HTTPException(status_code=403, detail="К заказам поставщика могут обращаться только поставщики")
    if not user.enterprise_id:
        return []

    orders = await service.list_orders_for_seller(
        session,
        seller_enterprise_ids=[e.id for e in user.enterprises],
        limit=limit,
        offset=offset,
    )
    return orders


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
):
    order = await service.get_order(session, order_id)
    return order


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(
    payload: OrderCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if user.role != UserRole.BUYER:
        raise HTTPException(status_code=403, detail="Создавать заказы могут только покупатели")
    if not user.enterprise_id:
        raise HTTPException(status_code=400, detail="Предприятие покупателя не привязано")

    order = await service.create_order(
        session,
        payload,
        buyer_enterprise_id=user.enterprise_id,
        buyer_user_id=user.id,
    )
    await session.commit()
    return order


@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int,
    payload: OrderUpdateStatus,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    order = await service.update_status(
        session,
        order_id,
        payload,
        actor_user_id=user.id,
        actor_role=user.role,
        actor_enterprise_ids=[e.id for e in user.enterprises],
    )
    await session.commit()
    return order
