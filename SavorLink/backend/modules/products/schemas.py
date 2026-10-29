from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from backend.modules.category.schemas import CategoryRead
from backend.modules.enterprises.schemas import EnterpriseShort


class ReviewsSummary(BaseModel):
    avg: Optional[float] = None
    count: int = 0


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    min_order_qty: Optional[int] = None
    quantity_in_stock: Optional[int] = None
    category_id: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название товара не может быть пустым")
        if len(v) > 200:
            raise ValueError("Название товара не должно превышать 200 символов")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 4000:
            raise ValueError("Описание не должно превышать 4000 символов")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Цена должна быть больше 0")
        return v

    @field_validator("min_order_qty", "quantity_in_stock")
    @classmethod
    def validate_quantity(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Количество не может быть отрицательным")
        return v

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    min_order_qty: Optional[int] = None
    quantity_in_stock: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Название товара не может быть пустым")
            if len(v) > 200:
                raise ValueError("Название товара не должно превышать 200 символов")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 4000:
            raise ValueError("Описание не должно превышать 4000 символов")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Цена должна быть больше 0")
        return v

    @field_validator("min_order_qty", "quantity_in_stock")
    @classmethod
    def validate_quantity(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Количество не может быть отрицательным")
        return v

    model_config = ConfigDict(from_attributes=True)


class ProductShort(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    min_order_qty: Optional[int] = None
    quantity_in_stock: Optional[int] = None
    category: CategoryRead
    enterprise: EnterpriseShort

    model_config = ConfigDict(from_attributes=True)


class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    min_order_qty: Optional[int] = None
    quantity_in_stock: Optional[int] = None
    category: CategoryRead
    enterprise: EnterpriseShort
    created_at: datetime
    reviews_summary: Optional[ReviewsSummary] = None
    category_name: Optional[str] = None
    enterprise_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


from backend.modules.enterprises.schemas import EnterpriseRead

ProductRead.model_rebuild()
ProductShort.model_rebuild()
