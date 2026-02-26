from pydantic import BaseModel
from typing import Optional, List, Dict, Literal
from datetime import datetime


# =========================
# BASE
# =========================

class ProductBase(BaseModel):
    name: str
    category_id: int   # 🔥 ganti dari category: str

    product_type: Literal["manual", "api"]

    price_base: Optional[float] = None
    margin_type: Optional[Literal["percent", "fixed"]] = None
    margin_value: Optional[float] = None

    vendor: Optional[str] = None
    vendor_code: Optional[str] = None

    required_fields: Optional[List[Dict]] = None

    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False


# =========================
# CREATE
# =========================

class ProductCreate(ProductBase):
    pass


# =========================
# UPDATE
# =========================

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None   # 🔥 ganti

    product_type: Optional[Literal["manual", "api"]] = None

    price_base: Optional[float] = None
    margin_type: Optional[Literal["percent", "fixed"]] = None
    margin_value: Optional[float] = None

    vendor: Optional[str] = None
    vendor_code: Optional[str] = None

    required_fields: Optional[List[Dict]] = None

    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


# =========================
# RESPONSE
# =========================

class ProductResponse(BaseModel):
    id: int
    name: str
    category_id: int
    product_type: str

    price_base: Optional[float]
    margin_type: Optional[str]
    margin_value: Optional[float]
    price_sell: float

    vendor: Optional[str]
    vendor_code: Optional[str]
    required_fields: Optional[List[Dict]]

    is_active: bool
    is_featured: bool

    created_at: datetime
    updated_at: datetime

    stock_count: Optional[int] = 0   # 🔥 tambahin biar frontend aman

    class Config:
        from_attributes = True