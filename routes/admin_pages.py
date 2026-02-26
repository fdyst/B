from fastapi import APIRouter, Request, Depends, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.user_model import User
from core.security import verify_password, create_access_token, decode_token
from core.logger import setup_logger

logger = setup_logger("admin_pages")
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
    admin_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    """Validasi admin token dari cookie"""
    
    endpoint = request.url.path
    logger.info(f"🔐 [ADMIN ACCESS] Endpoint: {endpoint}")
    
    # Debug: tampilkan semua cookies
    if request.cookies:
        logger.debug(f"   Cookies received: {list(request.cookies.keys())}")
    else:
        logger.debug(f"   No cookies received")
    
    # Check token
    if not admin_token:
        logger.warning(f"❌ [ADMIN ACCESS DENIED] No token - Endpoint: {endpoint}")
    db: Session = Depends(get_db)
):
    # PENTING: Cek cookie dari request.cookies bukan Cookie parameter
    admin_token = request.cookies.get("admin_token")
    
    logger.info(f"🔍 Checking admin token...")
    logger.info(f"   Token: {admin_token[:20] if admin_token else 'NONE'}...")
    
    if not admin_token:
        logger.warning("❌ No admin token found in cookies")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    logger.debug(f"   Token found: {admin_token[:30]}...")
    
    try:
        # Decode token
        logger.debug(f"   Decoding token...")
        payload = decode_token(admin_token)
        
        if not payload:
            logger.warning(f"❌ [ADMIN ACCESS DENIED] Invalid/expired token - Endpoint: {endpoint}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        logger.debug(f"   Payload: {payload}")
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning(f"❌ [ADMIN ACCESS DENIED] No user_id in token - Endpoint: {endpoint}")
            raise HTTPException(status_code=401, detail="Invalid token - no user_id")
        
        logger.debug(f"   User ID from token: {user_id}")
        
        # Query database
        logger.debug(f"   Querying user ID: {user_id}")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            logger.warning(f"❌ [ADMIN ACCESS DENIED] User not found (ID: {user_id}) - Endpoint: {endpoint}")
            raise HTTPException(status_code=401, detail="User not found")
        
        logger.debug(f"   User found: {user.email}, Role: {user.role}")
        
        # Check admin role
        if user.role != "admin":
            logger.warning(f"❌ [ADMIN ACCESS DENIED] Not an admin - User: {user.email} - Endpoint: {endpoint}")
            raise HTTPException(status_code=403, detail="Not authorized - not an admin")
        
        logger.info(f"✅ [ADMIN ACCESS GRANTED] User: {user.email} - Endpoint: {endpoint}")
        return user
        
    except HTTPException as e:
        logger.warning(f"❌ [ADMIN ACCESS DENIED] HTTPException: {e.detail} - Endpoint: {endpoint}")
        raise
    except Exception as e:
        logger.error(f"❌ [ADMIN ACCESS ERROR] Unexpected error: {type(e).__name__}: {str(e)} - Endpoint: {endpoint}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=401, detail="Authentication error")
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
    logger.info(f"📄 [GET] /admin/login - Rendering login page")
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
    logger.info(f"🔐 [LOGIN ATTEMPT] Email: {email}")
    
    try:
        # Query user
        logger.debug(f"   Querying user: {email}")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"❌ [LOGIN FAILED] User not found: {email}")
            return templates.TemplateResponse(
                "admin/login.html",
                {"request": request, "error": "Email atau password salah"}
            )
        
        logger.debug(f"   User found: {user.email}")
        
        # Verify password
        if not verify_password(password, user.password):
            logger.warning(f"❌ [LOGIN FAILED] Wrong password for: {email}")
            return templates.TemplateResponse(
                "admin/login.html",
                {"request": request, "error": "Email atau password salah"}
            )
        
        logger.debug(f"   Password verified ✅")
        
        # Check role
        if user.role != "admin":
            logger.warning(f"❌ [LOGIN FAILED] Not an admin account: {email}")
            return templates.TemplateResponse(
                "admin/login.html",
                {"request": request, "error": "Bukan akun admin"}
            )
        
        logger.debug(f"   User is admin ✅")
        
        # Create token
        logger.debug(f"   Creating token for user ID: {user.id}")
        token = create_access_token({"sub": str(user.id)})
        
        # Prepare response
        response = RedirectResponse("/admin/dashboard", status_code=302)
        response.set_cookie(
            key="admin_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600
        )
        
        logger.info(f"✅ [LOGIN SUCCESS] User: {email} - Token created and cookie set")
        return response
        
    except Exception as e:
        logger.error(f"❌ [LOGIN ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Terjadi error saat login"}
        )


# =========================
# ADMIN LOGOUT
# =========================
@router.get("/logout")
def admin_logout(request: Request):
    logger.info(f"🚪 [LOGOUT] User logging out")
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
    logger.info(f"📊 [DASHBOARD] Rendering for user: {admin.email}")
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/users", response_class=HTMLResponse)
def admin_users(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    logger.info(f"👥 [USERS PAGE] Rendering for user: {admin.email}")
    return templates.TemplateResponse("admin/users.html", {"request": request})


@router.get("/products", response_class=HTMLResponse)
def admin_products(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    logger.info(f"📦 [PRODUCTS PAGE] Rendering for user: {admin.email}")
    return templates.TemplateResponse("admin/products.html", {"request": request})


@router.get("/transactions", response_class=HTMLResponse)
def admin_transactions(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    logger.info(f"💳 [TRANSACTIONS PAGE] Rendering for user: {admin.email}")
    return templates.TemplateResponse("admin/transactions.html", {"request": request})
    return templates.TemplateResponse("admin/transactions.html", {"request": request})
