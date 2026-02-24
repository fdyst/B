from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from models.wallet_model import Wallet
from database.connection import SessionLocal
from models.user_model import User
from schemas.user_schema import (
    UserRegister,
    UserLogin,
    ForgotPassword,
    ResetPassword
)
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
    require_seller
)

router = APIRouter(prefix="/auth", tags=["Auth"])
templates = Jinja2Templates(directory="templates")


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# REGISTER
# =========================

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {
        "request": request
    })

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    new_user = User(
        email=user.email,
        password=get_password_hash(user.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🔥 TAMBAHAN WALLET (AMAN)
    wallet = Wallet(user_id=new_user.id)
    db.add(wallet)
    db.commit()

    return {"message": "Register berhasil"}
# =========================
# LOGIN
# =========================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {
        "request": request
    })
    
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Email atau password salah")

    token = create_access_token({"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# =========================
# FORGOT PASSWORD
# =========================

@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email tidak ditemukan")

    token = secrets.token_hex(16)

    user.reset_token = token
    user.reset_token_expire = datetime.utcnow() + timedelta(minutes=15)

    db.commit()

    # nanti seharusnya kirim email
    return {"reset_token": token}


# =========================
# RESET PASSWORD
# =========================

@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user or user.reset_token_expire < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Token tidak valid / expired"
        )

    user.password = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expire = None

    db.commit()

    return {"message": "Password berhasil direset"}


# =========================
# PROTECTED ROUTE
# =========================

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


# =========================
# ADMIN ONLY ROUTE
# =========================

@router.get("/admin-only")
def admin_only(current_user: User = Depends(require_admin)):
    return {"message": "Welcome admin!"}