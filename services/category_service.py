from models.category_model import Category

def create_category(db, name):
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def get_categories(db):
    return db.query(Category).filter(Category.is_active == True).all()