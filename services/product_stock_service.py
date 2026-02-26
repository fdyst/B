from models.product_stock_model import ProductStock

def add_stock_bulk(db, product_id, lines):
    for line in lines:
        clean = line.strip()
        if clean:  # 🔥 cegah baris kosong
            stock = ProductStock(
                product_id=product_id,
                credential=clean,
                is_sold=False
            )
            db.add(stock)

    db.commit()


def count_available_stock(db, product_id):
    return db.query(ProductStock).filter(
        ProductStock.product_id == product_id,
        ProductStock.is_sold == False
    ).count()