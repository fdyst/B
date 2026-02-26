from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from database.connection import Base
from datetime import datetime

class ProductStock(Base):
    __tablename__ = "product_stocks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    credential = Column(String, nullable=False)
    is_sold = Column(Boolean, default=False)
    sold_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)