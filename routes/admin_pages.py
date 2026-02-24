from fastapi import APIRouter, Request, Depends, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.user_model import User
from core.security import verify_password, create_access_token, decode_token

router = APIRouter(prefix="/admin", tags=["Admin Pages"])
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
# GET CURRENT ADMIN (PROTECTION)
# =========================
def get_current_admin(
    admin_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not admin_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(admin_token)
        user_id = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return user


# =========================
# ADMIN LOGIN PAGE
# =========================
@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


# =========================
# ADMIN LOGIN PROCESS
# =========================
@router.post("/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Email atau password salah"}
        )

    if user.role != "admin":
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Bukan akun admin"}
        )

    token = create_access_token({"sub": str(user.id)})

    response = RedirectResponse("/admin/dashboard", status_code=302)

    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True
    )

    return response


# =========================
# ADMIN LOGOUT
# =========================
@router.get("/logout")
def admin_logout():
    response = RedirectResponse("/admin/login", status_code=302)
    response.delete_cookie("admin_token")
    return response


# =========================
# ADMIN PAGES (PROTECTED)
# =========================
@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/users", response_class=HTMLResponse)
def admin_users(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    return templates.TemplateResponse("admin/users.html", {"request": request})


@router.get("/products", response_class=HTMLResponse)
def admin_products(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    return templates.TemplateResponse("admin/products.html", {"request": request})


@router.get("/transactions", response_class=HTMLResponse)
def admin_transactions(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    return templates.TemplateResponse("admin/transactions.html", {"request": request})