from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Chat, Message
from backend.modules.chats.repository import ChatRepository
from backend.modules.chats.schemas import ChatCreate, MessageCreate


class ChatService:
    def __init__(self, repo: ChatRepository | None = None) -> None:
        self.repo = repo or ChatRepository()

    async def list_chats(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> Sequence[Chat]:
        return await self.repo.list_for_user(session, user_id, limit=limit, offset=offset)

    async def get_chat(self, session: AsyncSession, *, chat_id: int, user_id: int) -> Chat:
        chat = await self.repo.get(session, chat_id)

        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")

        if user_id not in (chat.user1_id, chat.user2_id):
            raise HTTPException(status_code=403, detail="Нет доступа к чату")

        return chat

    async def create_chat(self, session: AsyncSession, *, user_id: int, data: ChatCreate) -> Chat:
        if data.user2_id == user_id:
            raise HTTPException(status_code=400, detail="Нельзя создать чат с самим собой")

        existing = await self.repo.get_by_users(session, user_id, data.user2_id)

        if existing:
            return existing

        chat = Chat(
            user1_id=user_id,
            user2_id=data.user2_id
        )

        return await self.repo.create(session, chat)

    async def create_message(
        self,
        session: AsyncSession,
        *,
        chat_id: int,
        user_id: int,
        data: MessageCreate
    ) -> Message:
        chat = await self.get_chat(session, chat_id=chat_id, user_id=user_id)

        msg = Message(
            chat_id=chat.id,
            sender_id=user_id,
            content=data.content,
            is_read=False
        )

        return await self.repo.create_message(session, msg)
