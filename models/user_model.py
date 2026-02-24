from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")
    reset_token = Column(String, nullable=True)
    reset_token_expire = Column(DateTime, nullable=True)

    wallet = relationship("Wallet", back_populates="user", uselist=False)