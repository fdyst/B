from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.security import get_db, verify_password, require_admin
from models.user_model import User
from models.order_model import Order

router = APIRouter(prefix="/admin", tags=["Admin API"])
templates = Jinja2Templates(directory="templates")


# =========================
# API ENDPOINTS (untuk frontend call, bukan HTML)
# =========================

@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get admin statistics"""
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


@router.get("/api/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users (API endpoint)"""
    users = db.query(User).all()
    return {
        "total": len(users),
        "users": [
            {"id": u.id, "email": u.email, "role": u.role}
            for u in users
        ]
    }


@router.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"message": "User not found", "success": False}

    db.delete(user)
    db.commit()

    return {"message": "User deleted", "success": True}


@router.get("/api/orders")
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all orders (API endpoint)"""
    orders = db.query(Order).all()
    return {
        "total": len(orders),
        "orders": [
            {
                "id": o.id,
                "order_number": o.order_number,
                "status": o.status,
                "price": o.price
            }
            for o in orders
        ]
    }


@router.put("/api/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update order status"""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return {"message": "Order not found", "success": False}

    order.status = status
    db.commit()

    return {"message": "Order status updated", "success": True, "new_status": status}