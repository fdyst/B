from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.security import get_db, require_admin
from models.product_model import Product
from schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from services.product_service import (
    create_product,
    get_all_active_products,
    get_product_by_id,
    update_product,
    delete_product
)

router = APIRouter(prefix="/products", tags=["Products"])


# =========================
# PUBLIC - GET ALL ACTIVE PRODUCTS
# =========================

@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return get_all_active_products(db)


# =========================
# ADMIN - CREATE PRODUCT
# =========================

@router.post("/", response_model=ProductResponse)
def admin_create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return create_product(db, data)


# =========================
# ADMIN - UPDATE PRODUCT
# =========================

@router.put("/{product_id}", response_model=ProductResponse)
def admin_update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return update_product(db, product, data)


# =========================
# ADMIN - DELETE PRODUCT
# =========================

@router.delete("/{product_id}")
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    delete_product(db, product)

    return {"message": "Product deleted"}