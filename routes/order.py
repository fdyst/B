from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.security import get_db, get_current_user, require_admin
from schemas.order_schema import OrderCreate, OrderResponse
from services.order_service import (
    create_order,
    get_user_orders,
    get_all_orders
)

router = APIRouter(prefix="/orders", tags=["Orders"])


# =========================
# USER - CREATE ORDER
# =========================
@router.post("/", response_model=OrderResponse)
def user_create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Buat order baru.
    - User hanya butuh product_id & target_data (misal: nomor HP, akun game, dsb)
    - Mengembalikan order yang berhasil dibuat
    """
    order = create_order(
        db,
        user_id=current_user.id,
        product_id=data.product_id,
        target_data=data.target_data
    )

    if not order:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    return order


# =========================
# USER - VIEW OWN ORDERS
# =========================
@router.get("/me", response_model=List[OrderResponse])
def view_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Lihat semua order milik user saat ini
    """
    return get_user_orders(db, current_user.id)


# =========================
# ADMIN - VIEW ALL ORDERS
# =========================
@router.get("/", response_model=List[OrderResponse])
def admin_view_orders(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Admin bisa lihat semua order dari seluruh user
    """
    return get_all_orders(db)