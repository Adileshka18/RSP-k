from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.database.models import DocumentType, OrderStatus, PaymentStatus
from backend.modules.enterprises.schemas import EnterpriseShort
from backend.modules.products.schemas import ProductShort


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseSchema):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Количество должно быть не меньше 1")
        return v


class OrderCreate(BaseSchema):
    seller_enterprise_id: int
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[OrderItemCreate]) -> List[OrderItemCreate]:
        if not v:
            raise ValueError("Заказ должен содержать хотя бы одну позицию")
        return v


class OrderUpdateStatus(BaseSchema):
    status: OrderStatus


class OrderItemRead(BaseSchema):
    id: int
    product_id: int
    quantity: int
    price: Decimal
    product: Optional[ProductShort] = None


class PaymentShort(BaseSchema):
    status: PaymentStatus
    amount: Decimal


class DocumentShort(BaseSchema):
    type: DocumentType
    file_url: str


class OrderListItem(BaseSchema):
    id: int
    status: OrderStatus
    total_amount: Optional[Decimal] = None
    created_at: datetime
    seller_enterprise: EnterpriseShort
    buyer_enterprise: Optional[EnterpriseShort] = None
    buyer: Optional[EnterpriseShort] = None
    items: List[OrderItemRead] = Field(default_factory=list)


class OrderRead(BaseSchema):
    id: int
    status: OrderStatus
    total_amount: Optional[Decimal] = None
    buyer_enterprise_id: int
    seller_enterprise_id: int
    created_at: datetime
    buyer_enterprise: Optional[EnterpriseShort] = None
    seller_enterprise: EnterpriseShort
    items: List[OrderItemRead] = Field(default_factory=list)
    payment: Optional[PaymentShort] = None
    documents: List[DocumentShort] = Field(default_factory=list)
