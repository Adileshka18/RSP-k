from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        },
    )


def validate_inn(value: str) -> str:
    if not value.isdigit():
        raise ValueError("ИНН должен содержать только цифры")
    if len(value) not in (10, 12):
        raise ValueError("ИНН должен содержать 10 или 12 цифр")
    return value


def validate_phone(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    if cleaned.startswith("8"):
        cleaned = "7" + cleaned[1:]
    if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
        raise ValueError("Неверный формат телефона")
    return value
