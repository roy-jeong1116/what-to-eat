from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from domain.category.category_schema import CategoryResponse
from domain.category.category_crud import get_all_categories

router = APIRouter(
    prefix="/category",
    tags=["category"],
)

@router.get("/", response_model=List[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    categories = get_all_categories(db)
    if not categories:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    return categories