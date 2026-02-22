from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class OrderCreate(BaseModel):
    product_id: int
    target_data: Optional[Dict] = None
    
class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    product_id: int
    price: float
    target_data: Optional[Dict]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True