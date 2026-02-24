from fastapi import APIRouter, Request, Depends, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.user_model import User
from core.security import verify_password, create_access_token, decode_token
from core.logger import setup_logger

logger = setup_logger()

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
    request: Request,
    db: Session = Depends(get_db)
):
    # PENTING: Cek cookie dari request.cookies bukan Cookie parameter
    admin_token = request.cookies.get("admin_token")
    
    logger.info(f"🔍 Checking admin token...")
    logger.info(f"   Token: {admin_token[:20] if admin_token else 'NONE'}...")
    
    if not admin_token:
        logger.warning("❌ No admin token found in cookies")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Decode token
        payload = decode_token(admin_token)
        logger.info(f"   Payload: {payload}")
        
        if not payload:
            logger.warning("❌ Token payload invalid or expired")
            raise HTTPException(status_code=401, detail="Invalid token - token expired or malformed")
        
        user_id = payload.get("sub")
        
        if not user_id:
            logger.warning("❌ No user_id in token")
            raise HTTPException(status_code=401, detail="Invalid token - no user_id")
        
        # Query user dari database
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            logger.warning(f"❌ User not found: {user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        if user.role != "admin":
            logger.warning(f"❌ User is not admin: {user.email}")
            raise HTTPException(status_code=403, detail="Not authorized - not an admin")

        logger.info(f"✅ Admin authenticated: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_current_admin: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token - server error")


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
    logger.info(f"🔐 Login attempt: {email}")
    
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        logger.warning(f"❌ Login failed: Invalid credentials for {email}")
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Email atau password salah"}
        )

    if user.role != "admin":
        logger.warning(f"❌ Login failed: {email} is not admin")
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Bukan akun admin"}
        )

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"✅ Login successful: {email}")

    response = RedirectResponse("/admin/dashboard", status_code=302)

    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        secure=False,  # Set True jika pakai HTTPS
        samesite="lax",
        max_age=3600  # 1 hour
    )

    logger.info(f"🍪 Cookie set for: {email}")
    return response


# =========================
# ADMIN LOGOUT
# =========================
@router.get("/logout")
def admin_logout():
    logger.info("🚪 Logout")
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
