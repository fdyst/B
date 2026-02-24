from database.connection import SessionLocal
from models.user_model import User
from core.security import get_password_hash

def create_admin():
    db = SessionLocal()

    email = input("Masukkan email admin: ")
    password = input("Masukkan password admin: ")

    # cek apakah sudah ada
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print("❌ Email sudah terdaftar!")
        return

    hashed_password = get_password_hash(password)

    admin = User(
        email=email,
        password=hashed_password,
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("✅ Admin berhasil dibuat!")

if __name__ == "__main__":
    create_admin()