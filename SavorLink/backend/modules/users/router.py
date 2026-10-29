from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user_id, get_current_user
from backend.modules.users.schemas import UserRead, UserUpdate, UserListItem
from backend.database.session import get_session
from backend.database.models import UserRole, User
from backend.modules.users.service import UserService
from typing import List


router = APIRouter(prefix="/users", tags=["users"])
service = UserService()


@router.get("/me", response_model=UserRead)
async def get_me(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    user = await service.get_me(session, user_id)
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    user = await service.update_me(session, user_id=user_id, data=payload)
    await session.commit()
    return user


@router.get("", response_model=List[UserListItem])
async def list_users(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from fastapi import HTTPException
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может просматривать всех пользователей")

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    stmt = select(User).options(selectinload(User.enterprises)).order_by(User.id.desc())
    res = await session.execute(stmt)
    return res.scalars().all()

from pydantic import BaseModel
class RoleUpdate(BaseModel):
    role: UserRole

@router.patch("/{user_id}/role", response_model=UserRead)
async def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from fastapi import HTTPException
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор может изменять роли")

    user = await service.get_me(session, user_id)
    user.role = payload.role
    await session.commit()
    await session.refresh(user)
    return user
