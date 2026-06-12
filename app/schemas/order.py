from pydantic import BaseModel
from datetime import datetime


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    model_config = {
        "from_attributes": True
    }


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = {
        "from_attributes": True
    }