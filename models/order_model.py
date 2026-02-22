from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime
import uuid


def generate_order_number():
    """Generate order number unik dengan prefix INV"""
    return f"INV-{uuid.uuid4().hex[:10].upper()}"


class Order(Base):
    __tablename__ = "orders"

    # =========================
    # IDENTITAS ORDER
    # =========================
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, default=generate_order_number)

    # =========================
    # RELASI
    # =========================
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    user = relationship("User")
    product = relationship("Product")

    # =========================
    # DETAIL ORDER
    # =========================
    price = Column(Float, nullable=False)
    target_data = Column(JSON, nullable=True)   # contoh: nomor HP, akun game, dsb
    serial_number = Column(String, nullable=True)  # voucher/serial jika produk digital

    # =========================
    # STATUS ORDER
    # =========================
    status = Column(String, default="pending")  
    # pending / paid / processing / success / failed
    merchant_ref = Column(String, nullable=True)   # payment gateway reference
    vendor_name = Column(String, nullable=True)    # misal: "digiflazz"
    vendor_ref_id = Column(String, nullable=True)  # vendor order ID

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)