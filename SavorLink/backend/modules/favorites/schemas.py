from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from backend.modules.products.schemas import ProductShort


class FavoriteCreate(BaseModel):
    product_id: int

    model_config = ConfigDict(from_attributes=True)


class FavoriteRead(BaseModel):
    id: int
    product_id: int
    created_at: datetime
    product: Optional[ProductShort] = None

    model_config = ConfigDict(from_attributes=True)
