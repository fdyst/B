from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.category_model import Category
from fastapi import Depends
from models.product_model import Product
from models.category_model import Category
from sqlalchemy.orm import Session
from database.connection import get_db
router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):

    categories = db.query(Category).filter(
        Category.is_active == True
    ).all()

    return templates.TemplateResponse(
        "user/dashboard.html",
        {
            "request": request,
            "categories": categories
        }
    )

@router.get("/transfer", response_class=HTMLResponse)
def transfer_page(request: Request):
    return templates.TemplateResponse("user/transfer.html", {
        "request": request
    })


@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse("user/history.html", {
        "request": request
    })


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse("user/profile.html", {
        "request": request
    })
    
@router.get("/topup", response_class=HTMLResponse)
def topup_page(request: Request):
    return templates.TemplateResponse("user/topup.html", {"request": request})
    
@router.get("/category/{category_id}", response_class=HTMLResponse)
def category_page(category_id: int, request: Request, db: Session = Depends(get_db)):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_active == True
    ).first()

    if not category:
        return templates.TemplateResponse(
            "user/404.html",
            {"request": request}
        )

    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).all()

    return templates.TemplateResponse(
        "user/category_products.html",
        {
            "request": request,
            "category": category,
            "products": products
        }
    )

@router.get("/product/{product_id}", response_class=HTMLResponse)
def product_detail(product_id: int, request: Request, db: Session = Depends(get_db)):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        return templates.TemplateResponse(
            "user/404.html",
            {"request": request}
        )

    return templates.TemplateResponse(
        "user/product_detail.html",
        {
            "request": request,
            "product": product
        }
    )