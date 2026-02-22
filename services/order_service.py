from sqlalchemy.orm import Session
from models.order_model import Order
from models.product_model import Product


def create_order(db: Session, user_id: int, product_id: int, target_data: dict):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        return None

    order = Order(
        user_id=user_id,
        product_id=product.id,
        price=product.price,  # snapshot harga saat transaksi
        target_data=target_data,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_all_orders(db: Session):
    return db.query(Order).all()