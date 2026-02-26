import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database.connection import Base
from datetime import datetime

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=True)  # simpan path file
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)