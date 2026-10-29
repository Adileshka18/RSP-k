from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from backend.modules.enterprises.schemas import EnterpriseShort, UserShort
from backend.modules.products.schemas import ProductShort


class EnterpriseReviewCreate(BaseModel):
    target_enterprise_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("Комментарий не должен превышать 2000 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class EnterpriseReviewRead(BaseModel):
    id: int
    author_user_id: int
    target_enterprise_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    author_user: Optional[UserShort] = None
    target_enterprise: Optional[EnterpriseShort] = None

    model_config = ConfigDict(from_attributes=True)


class ProductReviewCreate(BaseModel):
    product_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("Комментарий не должен превышать 2000 символов")
        return v

    model_config = ConfigDict(from_attributes=True)


class ProductReviewRead(BaseModel):
    id: int
    author_enterprise_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    author_enterprise: Optional[EnterpriseShort] = None
    product: Optional[ProductShort] = None

    model_config = ConfigDict(from_attributes=True)
