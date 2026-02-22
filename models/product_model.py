from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from database.connection import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

    price = Column(Float, nullable=False)         # harga jual
    cost_price = Column(Float, nullable=True)     # harga dari vendor (optional)

    vendor = Column(String, nullable=True)        # digiflazz / manual / dll
    vendor_code = Column(String, nullable=True)   # kode produk di vendor

    required_fields = Column(JSON, nullable=True) # dynamic input field

    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)