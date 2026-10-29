from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Chat, Message, User


class ChatRepository:
    async def list_for_user(self, session: AsyncSession, user_id: int, *, limit: int = 50, offset: int = 0) -> Sequence[Chat]:
        stmt = (
            select(Chat)
            .where((Chat.user1_id == user_id) | (Chat.user2_id == user_id))
            .options(
                selectinload(Chat.user1).selectinload(User.enterprises),
                selectinload(Chat.user2).selectinload(User.enterprises),
                selectinload(Chat.messages).selectinload(Message.sender).selectinload(User.enterprises),
            )
            .order_by(Chat.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get(self, session: AsyncSession, chat_id: int) -> Chat | None:
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id)
            .options(
                selectinload(Chat.user1).selectinload(User.enterprises),
                selectinload(Chat.user2).selectinload(User.enterprises),
                selectinload(Chat.messages).selectinload(Message.sender).selectinload(User.enterprises),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().first()

    async def get_by_users(self, session: AsyncSession, user1_id: int, user2_id: int) -> Chat | None:
        user_min = min(user1_id, user2_id)
        user_max = max(user1_id, user2_id)
        stmt = select(Chat).where(Chat.user_min == user_min, Chat.user_max == user_max)
        res = await session.execute(stmt)
        return res.scalars().first()

    async def create(self, session: AsyncSession, chat: Chat) -> Chat:
        session.add(chat)
        await session.flush()
        await session.refresh(chat)
        return chat

    async def create_message(self, session: AsyncSession, message: Message) -> Message:
        session.add(message)
        await session.flush()
        stmt = (
            select(Message)
            .where(Message.id == message.id)
            .options(selectinload(Message.sender).selectinload(User.enterprises))
        )
        res = await session.execute(stmt)
        return res.scalar_one()
