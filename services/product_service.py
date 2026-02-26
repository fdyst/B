from sqlalchemy.orm import Session
from models.product_model import Product
from schemas.product_schema import ProductCreate, ProductUpdate
from datetime import datetime


# =============================
# PRICE CALCULATION ENGINE
# =============================

def calculate_price(price_base: float, margin_type: str, margin_value: float):
    if not price_base:
        return 0

    if margin_type == "percent":
        return price_base + (price_base * margin_value / 100)

    elif margin_type == "fixed":
        return price_base + margin_value

    return price_base


# =============================
# CREATE PRODUCT
# =============================

def create_product(db: Session, data: ProductCreate):
    data_dict = data.model_dump()

    price_base = data_dict.get("price_base")
    margin_type = data_dict.get("margin_type")
    margin_value = data_dict.get("margin_value")

    # Auto calculate sell price
    price_sell = calculate_price(price_base, margin_type, margin_value)

    product = Product(
        **data_dict,
        price_sell=price_sell,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# =============================
# GET PRODUCTS
# =============================

def get_all_active_products(db: Session):
    return db.query(Product).filter(Product.is_active == True).all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


# =============================
# UPDATE PRODUCT
# =============================

def update_product(db: Session, product: Product, data: ProductUpdate):
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    # Recalculate price if pricing fields changed
    if any(k in update_data for k in ["price_base", "margin_type", "margin_value"]):
        product.price_sell = calculate_price(
            product.price_base,
            product.margin_type,
            product.margin_value
        )

    product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(product)

    return product


# =============================
# DELETE PRODUCT
# =============================

def delete_product(db: Session, product: Product):
    db.delete(product)
    db.commit()