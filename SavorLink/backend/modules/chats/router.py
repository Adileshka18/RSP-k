from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user_id
from backend.modules.chats.schemas import ChatCreate, ChatListItem, ChatRead, MessageCreate, MessageRead
from backend.database.session import get_session
from backend.modules.chats.service import ChatService


router = APIRouter(prefix="/chats", tags=["chats"])
service = ChatService()


@router.get("", response_model=List[ChatListItem])
async def list_chats(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    chats = await service.list_chats(session, user_id=user_id, limit=limit, offset=offset)
    return chats


@router.post("", response_model=ChatRead, status_code=201)
async def create_chat(
    payload: ChatCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    chat = await service.create_chat(session, user_id=user_id, data=payload)
    await session.commit()
    chat = await service.get_chat(session, chat_id=chat.id, user_id=user_id)
    return chat


@router.get("/{chat_id}", response_model=ChatRead)
async def get_chat(
    chat_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    chat = await service.get_chat(session, chat_id=chat_id, user_id=user_id)
    return chat


@router.post("/{chat_id}/messages", response_model=MessageRead, status_code=201)
async def create_message(
    chat_id: int,
    payload: MessageCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    msg = await service.create_message(session, chat_id=chat_id, user_id=user_id, data=payload)
    await session.commit()
    return msg
