from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    # === RELATION CATEGORY ===
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category")

    # === TYPE ===
    product_type = Column(String, nullable=False, default="manual")

    # === PRICING ===
    price_base = Column(Float, nullable=True)
    margin_type = Column(String, nullable=True)
    margin_value = Column(Float, nullable=True)
    price_sell = Column(Float, nullable=False)

    # === VENDOR ===
    vendor = Column(String, nullable=True)
    vendor_code = Column(String, nullable=True)

    required_fields = Column(JSON, nullable=True)

    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # === STOCK RELATION ===
    stocks = relationship("ProductStock", backref="product")