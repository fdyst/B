from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.category_model import Category

router = APIRouter(prefix="/categories", tags=["Categories"])


# ✅ GET ALL (untuk admin → tampilkan semua, bukan cuma aktif)
@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# ✅ CREATE
@router.post("/")
def create_category(name: str, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ✅ EDIT / RENAME
@router.put("/{category_id}")
def update_category(category_id: int, name: str, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Not found")

    category.name = name
    db.commit()
    db.refresh(category)

    return category


# ✅ DELETE
@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted"}


# ✅ TOGGLE ACTIVE
@router.patch("/{category_id}/toggle")
def toggle_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Not found")

    category.is_active = not category.is_active
    db.commit()

    return {"is_active": category.is_active}

