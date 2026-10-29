from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.modules.users.schemas import UserListItem


class MessageCreate(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Сообщение не может быть пустым")
        if len(v) > 4000:
            raise ValueError("Сообщение не должно превышать 4000 символов")
        return v.strip()

    model_config = ConfigDict(from_attributes=True)


class MessageRead(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime
    sender: Optional[UserListItem] = None

    model_config = ConfigDict(from_attributes=True)


class ChatCreate(BaseModel):
    user2_id: int

    model_config = ConfigDict(from_attributes=True)


class ChatListItem(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    user1: Optional[UserListItem] = None
    user2: Optional[UserListItem] = None
    last_message: Optional[MessageRead] = None

    model_config = ConfigDict(from_attributes=True)


class ChatRead(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    user1: Optional[UserListItem] = None
    user2: Optional[UserListItem] = None
    messages: List[MessageRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
