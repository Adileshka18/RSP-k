from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.database.models import UserRole
from backend.modules.common.schemas import validate_phone
from backend.modules.enterprises.schemas import EnterpriseShort


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    enterprise_ids: List[int] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать не менее 8 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    old_password: Optional[str] = None
    enterprise_ids: Optional[List[int]] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 8:
            raise ValueError("Пароль должен содержать не менее 8 символов")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    created_at: datetime
    enterprise_id: Optional[int] = None
    enterprises: List[EnterpriseShort] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserListItem(BaseModel):
    id: int
    email: str
    role: UserRole
    enterprises: List[EnterpriseShort] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
