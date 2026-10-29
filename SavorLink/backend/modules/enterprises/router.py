from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user
from backend.database.models import EnterpriseReview, User, UserRole
from backend.modules.enterprises.schemas import EnterpriseCreate, EnterpriseRead, EnterpriseUpdate
from backend.modules.review.schemas import EnterpriseReviewCreate, EnterpriseReviewRead
from backend.database.session import get_session
from backend.modules.enterprises.service import EnterpriseService


router = APIRouter(prefix="/enterprises", tags=["enterprises"])
service = EnterpriseService()


@router.get("", response_model=List[EnterpriseRead])
async def list_enterprises(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    ents = await service.list_enterprises(session, limit=limit, offset=offset)
    return ents


@router.get("/{enterprise_id}", response_model=EnterpriseRead)
async def get_enterprise(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
):
    ent = await service.get_enterprise(session, enterprise_id)
    return ent


@router.post("", response_model=EnterpriseRead, status_code=201)
async def create_enterprise(
    payload: EnterpriseCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ent = await service.create_enterprise(session, payload, user_id=current_user.id)
    await session.commit()
    return ent


@router.post("/{enterprise_id}/join", response_model=EnterpriseRead)
async def join_enterprise(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await service.link_user_to_enterprise(session, enterprise_id, current_user.id)
    await session.commit()
    ent = await service.get_enterprise(session, enterprise_id)
    return ent


@router.patch("/{enterprise_id}", response_model=EnterpriseRead)
async def update_enterprise(
    enterprise_id: int,
    payload: EnterpriseUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_enterprise_ids = [e.id for e in current_user.enterprises]
    if enterprise_id not in user_enterprise_ids and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="У вас нет прав на редактирование этого предприятия")

    ent = await service.update_enterprise(session, enterprise_id, payload)
    await session.commit()
    return ent


@router.delete("/{enterprise_id}", status_code=204)
async def delete_enterprise(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
):
    await service.delete_enterprise(session, enterprise_id)
    await session.commit()
    return None


@router.post("/{enterprise_id}/reviews", response_model=EnterpriseReviewRead)
async def create_enterprise_review(
    enterprise_id: int,
    payload: EnterpriseReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.BUYER:
        raise HTTPException(status_code=403, detail="Только покупатели могут оставлять отзывы")

    from sqlalchemy import select
    existing_stmt = select(EnterpriseReview).where(
        EnterpriseReview.author_user_id == current_user.id,
        EnterpriseReview.target_enterprise_id == enterprise_id
    )
    existing_res = await session.execute(existing_stmt)
    if existing_res.scalars().first():
        raise HTTPException(status_code=400, detail="Вы уже оставляли отзыв об этом поставщике")

    review = EnterpriseReview(
        author_user_id=current_user.id,
        target_enterprise_id=enterprise_id,
        rating=payload.rating,
        comment=payload.comment
    )
    session.add(review)
    await session.commit()

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = select(EnterpriseReview).where(EnterpriseReview.id == review.id).options(
        selectinload(EnterpriseReview.author_user),
        selectinload(EnterpriseReview.target_enterprise)
    )
    res = await session.execute(stmt)
    return res.scalar_one()


@router.get("/{enterprise_id}/reviews", response_model=List[EnterpriseReviewRead])
async def list_enterprise_reviews(
    enterprise_id: int,
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = select(EnterpriseReview).where(
        EnterpriseReview.target_enterprise_id == enterprise_id
    ).options(
        selectinload(EnterpriseReview.author_user),
        selectinload(EnterpriseReview.target_enterprise)
    ).order_by(EnterpriseReview.created_at.desc())

    res = await session.execute(stmt)
    return res.scalars().all()
