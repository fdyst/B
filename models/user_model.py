from sqlalchemy import Column, Integer, String, DateTime
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