from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user
from backend.core.security import AuthService
from backend.database.models import User
from backend.database.session import get_session
from backend.modules.users.schemas import UserCreate, UserRead
from backend.modules.users.service import UserService


router = APIRouter(prefix="/auth", tags=["auth"])
service = UserService()
auth_service = AuthService()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserRead


class SimpleMessage(BaseModel):
    detail: str


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await service.register(session, payload)
    await session.commit()
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await service.login(session, email=str(payload.email), password=payload.password)
    token = auth_service.create_access_token(user.id, token_version=user.token_version)
    return LoginResponse(token=token, user=user)


@router.post("/logout", response_model=SimpleMessage)
async def logout(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await service.revoke_tokens(session, current_user)
    await session.commit()
    return SimpleMessage(detail="Токен отозван")
