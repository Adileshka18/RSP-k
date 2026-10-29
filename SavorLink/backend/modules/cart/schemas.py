from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from backend.modules.products.schemas import ProductShort


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не меньше 1")
        return v

    model_config = ConfigDict(from_attributes=True)


class CartItemUpdate(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не меньше 1")
        return v

    model_config = ConfigDict(from_attributes=True)


class CartItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductShort

    model_config = ConfigDict(from_attributes=True)


class CartRead(BaseModel):
    id: int
    updated_at: datetime
    items: List[CartItemRead]
    total_amount: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)
