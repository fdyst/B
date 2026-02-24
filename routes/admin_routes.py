from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.security import get_db, verify_password
from models.user_model import User
from core.security import require_admin
router = APIRouter()
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/admin", tags=["Admin"])


# =========================
# ADMIN LOGIN PAGE
# =========================

@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    total_users = db.query(User).count()
    total_admin = db.query(User).filter(User.role == "admin").count()
    total_seller = db.query(User).filter(User.role == "seller").count()
    total_orders = db.query(Order).count()

    return {
        "total_users": total_users,
        "total_admin": total_admin,
        "total_seller": total_seller,
        "total_orders": total_orders
    }
    
@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email, User.role == "admin").first()
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Email atau password salah"})
    
    response = RedirectResponse("/admin/dashboard", status_code=302)
    response.set_cookie("admin_email", user.email)
    return response

# =========================
# DASHBOARD PAGE
# =========================
@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_email = request.cookies.get("admin_email")
    if not admin_email:
        return RedirectResponse("/admin/login")
    
    users = db.query(User).all()
    from models.order_model import Order
    orders = db.query(Order).all()
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "admin_email": admin_email,
        "users": users,
        "orders": orders
    })

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return db.query(User).all()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"message": "User not found"}

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}

@router.get("/orders")
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return db.query(Order).all()


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return {"message": "Order not found"}

    order.status = status
    db.commit()

    return {"message": "Order updated"}



# =========================
# LOGOUT
# =========================
@router.get("/admin/logout")
def admin_logout():
    response = RedirectResponse("/admin/login")
    response.delete_cookie("admin_email")
    return response