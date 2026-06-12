from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.category import CategoryResponse


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_ids: list[int]


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category_ids: list[int] | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    created_at: datetime
    categories: list[CategoryResponse]
    image_url: str | None = None

    model_config = {
        "from_attributes": True
    }