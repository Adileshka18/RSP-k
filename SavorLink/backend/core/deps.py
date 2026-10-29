from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import AuthService
from backend.database.models import User
from backend.database.session import get_session
from backend.modules.users.repository import UserRepository


auth_service = AuthService()


async def get_current_user_id(
    authorization: str | None = Header(None),
    session: AsyncSession = Depends(get_session),
) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Отсутствует заголовок Authorization")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Неверный формат токена")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        token_data = auth_service.verify_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    repo = UserRepository()
    user = await repo.get(session, token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.token_version != token_data.token_version:
        raise HTTPException(status_code=401, detail="Токен отозван")

    return user.id


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> User:
    repo = UserRepository()
    user = await repo.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
