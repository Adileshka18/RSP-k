from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from backend.database.models import PaymentStatus


class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentConfirm(BaseModel):
    pass


class PaymentCancel(BaseModel):
    reason: str = ""

    model_config = ConfigDict(from_attributes=True)
