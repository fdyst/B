from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from datetime import datetime
from database.connection import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # credit / debit
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)