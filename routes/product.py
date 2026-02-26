from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from models.product_model import Product
from models.product_stock_model import ProductStock
from schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from services.product_stock_service import add_stock_bulk, count_available_stock
from sqlalchemy import func

router = APIRouter(prefix="/products", tags=["Products"])

# =========================
# GET ALL (ADMIN VIEW)
# =========================
@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):

    products = db.query(Product).all()
    result = []

    for p in products:
        stock_count = db.query(func.count(ProductStock.id)).filter(
            ProductStock.product_id == p.id,
            ProductStock.is_sold == False
        ).scalar()

        result.append({
            **p.__dict__,
            "stock_count": stock_count
        })

    return result


# =========================
# GET ACTIVE (USER VIEW)
# =========================
@router.get("/active", response_model=List[ProductResponse])
def get_active_products(db: Session = Depends(get_db)):

    products = db.query(Product).filter(Product.is_active == True).all()
    result = []

    for p in products:
        stock_count = count_available_stock(db, p.id)

        result.append({
            **p.__dict__,
            "stock_count": stock_count
        })

    return result


# =========================
# CREATE PRODUCT
# =========================
@router.post("/", response_model=ProductResponse)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):

    if payload.price_base is None:
        raise HTTPException(status_code=400, detail="price_base required")

    margin_value = payload.margin_value or 0

    if payload.margin_type == "percent":
        price_sell = payload.price_base + (payload.price_base * margin_value / 100)
    else:
        price_sell = payload.price_base + margin_value

    product = Product(
        name=payload.name,
        category_id=payload.category_id,
        product_type=payload.product_type,
        price_base=payload.price_base,
        margin_type=payload.margin_type,
        margin_value=payload.margin_value,
        price_sell=price_sell,
        vendor=payload.vendor,
        vendor_code=payload.vendor_code,
        required_fields=payload.required_fields,
        is_active=payload.is_active,
        is_featured=payload.is_featured
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        **product.__dict__,
        "stock_count": 0
    }


# =========================
# UPDATE PRODUCT
# =========================
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):

    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(product, key, value)

    # Recalculate price
    if product.price_base:
        margin_value = product.margin_value or 0
        if product.margin_type == "percent":
            product.price_sell = product.price_base + (product.price_base * margin_value / 100)
        else:
            product.price_sell = product.price_base + margin_value

    db.commit()
    db.refresh(product)

    stock_count = count_available_stock(db, product.id)

    return {
        **product.__dict__,
        "stock_count": stock_count
    }


# =========================
# TOGGLE ACTIVE
# =========================
@router.patch("/{product_id}/toggle")
def toggle_product(product_id: int, db: Session = Depends(get_db)):

    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    product.is_active = not product.is_active
    db.commit()

    return {"message": "Status updated"}


# =========================
# UPLOAD STOCK
# =========================
@router.post("/{product_id}/upload-stock")
async def upload_stock(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    add_stock_bulk(db, product_id, lines)

    return {"message": "Stock uploaded successfully"}

# =========================
# DELETE PRODUCT
# =========================
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):

    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}