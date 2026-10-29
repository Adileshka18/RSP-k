from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.modules.common.schemas import validate_inn, validate_phone

if TYPE_CHECKING:
    from backend.modules.products.schemas import ProductShort


class EnterpriseShort(BaseModel):
    id: int
    short_name: str

    model_config = ConfigDict(from_attributes=True)


class EnterpriseCreate(BaseModel):
    short_name: str
    inn: str
    region: str
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Название организации не может быть пустым")
        if len(v) > 200:
            raise ValueError("Название организации не должно превышать 200 символов")
        return v.strip()

    @field_validator("inn")
    @classmethod
    def validate_inn_field(cls, v: str) -> str:
        return validate_inn(v)

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    model_config = ConfigDict(from_attributes=True)


class EnterpriseUpdate(BaseModel):
    short_name: Optional[str] = None
    inn: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Название организации не может быть пустым")
            if len(v) > 200:
                raise ValueError("Название организации не должно превышать 200 символов")
            return v.strip()
        return v

    @field_validator("inn")
    @classmethod
    def validate_inn_field(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_inn(v)
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    model_config = ConfigDict(from_attributes=True)


class UserShort(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class EnterpriseRead(BaseModel):
    id: int
    short_name: str
    inn: str
    region: str
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    products_count: Optional[int] = None
    users: List[UserShort] = Field(default_factory=list)
    products: List["ProductShort"] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


from backend.modules.products.schemas import ProductShort

EnterpriseRead.model_rebuild()
