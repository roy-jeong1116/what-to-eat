from sqlalchemy.orm import Session
from models import Category

def get_all_categories(db: Session):
    return db.query(Category).all()