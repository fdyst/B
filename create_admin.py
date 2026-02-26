from database.connection import SessionLocal, engine
from models.user_model import User
from models.wallet_model import Wallet  # IMPORT INI PENTING!
from models.order_model import Order
from models.transaction_model import Transaction
from core.security import get_password_hash
from database.connection import Base
# WAJIB IMPORT SEMUA MODEL RELASI
from models.product_model import Product
from models.category_model import Category
from models.product_stock_model import ProductStock

def create_admin():
    # Buat semua tabel jika belum ada
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    try:
        email = input("Masukkan email admin: ")
        password = input("Masukkan password admin: ")

        # Cek apakah sudah ada
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("❌ Email sudah terdaftar!")
            return

        hashed_password = get_password_hash(password)

        # Buat user admin
        admin = User(
            email=email,
            password=hashed_password,
            role="admin"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        # Buat wallet untuk admin
        wallet = Wallet(
            user_id=admin.id,
            balance=0.0
        )
        db.add(wallet)
        db.commit()

        print("✅ Admin berhasil dibuat!")
        print(f"   Email: {email}")
        print(f"   ID: {admin.id}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()