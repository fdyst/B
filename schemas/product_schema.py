from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    cost_price: Optional[float] = None
    vendor: Optional[str] = None
    vendor_code: Optional[str] = None
    required_fields: Optional[List[Dict]] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    price: Optional[float]
    cost_price: Optional[float]
    vendor: Optional[str]
    vendor_code: Optional[str]
    required_fields: Optional[List[Dict]]
    is_active: Optional[bool]
    is_featured: Optional[bool]


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True