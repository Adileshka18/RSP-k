from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user_id
from backend.modules.enterprises.schemas import EnterpriseRead
from backend.modules.products.schemas import ProductShort
from backend.database.session import get_session
from backend.modules.favorites.service import FavoriteService


router = APIRouter(prefix="/favorites", tags=["favorites"])
service = FavoriteService()


@router.get("/products", response_model=List[ProductShort])
async def list_favorite_products(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    return await service.list_favorite_products(session, user_id=user_id)


@router.post("/products/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    await service.add_favorite_product(session, user_id=user_id, product_id=product_id)
    await session.commit()
    return {"status": "ok"}


@router.delete("/products/{product_id}")
async def remove_favorite_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    await service.remove_favorite_product(session, user_id=user_id, product_id=product_id)
    await session.commit()
    return {"status": "ok"}


@router.get("/suppliers", response_model=List[EnterpriseRead])
async def list_favorite_suppliers(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    return await service.list_favorite_suppliers(session, user_id=user_id)


@router.post("/suppliers/{enterprise_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite_supplier(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    await service.add_favorite_supplier(session, user_id=user_id, enterprise_id=enterprise_id)
    await session.commit()
    return {"status": "ok"}


@router.delete("/suppliers/{enterprise_id}")
async def remove_favorite_supplier(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    await service.remove_favorite_supplier(session, user_id=user_id, enterprise_id=enterprise_id)
    await session.commit()
    return {"status": "ok"}
