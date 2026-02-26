from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.user_model import User
from core.security import get_password_hash, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= REGISTER =================

@router.get("/user/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("user/register.html", {"request": request})


@router.post("/user/register", response_class=HTMLResponse)
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse("user/register.html",
                                          {"request": request, "error": "Email sudah terdaftar"})

    new_user = User(
        email=email,
        password=get_password_hash(password),
        role="user"
    )
    db.add(new_user)
    db.commit()

    return RedirectResponse("/user/login", status_code=302)


# ================= LOGIN =================

@router.get("/user/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("user/login.html", {"request": request})


@router.post("/user/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse("user/login.html",
                                          {"request": request, "error": "Email atau password salah"})

    response = RedirectResponse("/user/dashboard", status_code=302)
    response.set_cookie("user_email", user.email)
    return response


# ================= DASHBOARD =================

@router.get("/user/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    email = request.cookies.get("user_email")
    if not email:
        return RedirectResponse("/user/login")

    return templates.TemplateResponse("user/dashboard.html",
                                      {"request": request, "email": email})


# ================= FORGOT PASSWORD =================

@router.get("/user/forgot", response_class=HTMLResponse)
def forgot_page(request: Request):
    return templates.TemplateResponse("user_forgot.html", {"request": request})


@router.post("/user/forgot", response_class=HTMLResponse)
def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return templates.TemplateResponse("user_forgot.html",
                                          {"request": request, "message": "Email tidak ditemukan"})

    return templates.TemplateResponse("user_forgot.html",
                                      {"request": request, "message": "Fitur reset akan dikirim (dummy)"})


# ================= LOGOUT =================

@router.get("/user/logout")
def logout():
    response = RedirectResponse("/user/login")
    response.delete_cookie("user_email")
    return response