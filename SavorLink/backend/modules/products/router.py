from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user
from backend.database.models import Category, User, UserRole
from backend.modules.category.schemas import CategoryRead
from backend.modules.products.schemas import ProductCreate, ProductRead, ProductShort, ProductUpdate
from backend.database.session import get_session
from backend.modules.products.service import ProductService


router = APIRouter(prefix="/products", tags=["products"])
service = ProductService()


@router.get("/categories", response_model=List[CategoryRead])
async def list_categories(
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import select

    res = await session.execute(select(Category).order_by(Category.name))
    return res.scalars().all()

from pydantic import BaseModel
class CategoryCreate(BaseModel):
    name: str

@router.post("/categories", response_model=CategoryRead)
async def create_category(
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может создавать категории")
    
    category = Category(name=payload.name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

@router.patch("/categories/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может изменять категории")
    
    from sqlalchemy import select
    res = await session.execute(select(Category).where(Category.id == category_id))
    category = res.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
        
    category.name = payload.name
    await session.commit()
    await session.refresh(category)
    return category


@router.get("", response_model=List[ProductShort])
async def list_products(
    enterprise_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    products = await service.list_products(session, enterprise_id=enterprise_id, limit=limit, offset=offset)
    return products


@router.get("/my", response_model=List[ProductShort])
async def list_my_products(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.SUPPLIER:
        raise HTTPException(status_code=403, detail="Только поставщики могут просматривать свои товары")

    enterprise_ids = [e.id for e in current_user.enterprises]
    if not enterprise_ids:
        return []

    products = await service.list_products_by_enterprise_ids(session, enterprise_ids, limit=limit, offset=offset)
    return products


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await service.get_product(session, product_id)
    return product


@router.post("", response_model=ProductRead, status_code=201)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.SUPPLIER:
        raise HTTPException(status_code=403, detail="Только поставщики могут создавать товары")

    if not current_user.enterprises:
        raise HTTPException(status_code=400, detail="У пользователя не привязано ни одно предприятие")

    enterprise_id = current_user.enterprises[0].id

    product = await service.create_product(session, payload, enterprise_id=enterprise_id)
    await session.commit()
    return product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    enterprise_ids = [e.id for e in current_user.enterprises]
    product = await service.update_product(session, product_id, payload, enterprise_ids=enterprise_ids)
    await session.commit()
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        # Admins can delete any product
        await service.delete_product(session, product_id, enterprise_ids=None)
    else:
        enterprise_ids = [e.id for e in current_user.enterprises]
        await service.delete_product(session, product_id, enterprise_ids=enterprise_ids)
        
    await session.commit()
    return None
