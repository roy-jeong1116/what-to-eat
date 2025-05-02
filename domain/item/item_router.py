from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.item.item_schema import ItemCreate, ItemResponse
from domain.item.item_crud import upsert_items, create_item
from database import get_db

router = APIRouter(
    prefix="/item",
)

# 재고 하나씩 추가
@router.post("/create", response_model=ItemResponse)
def create_new_item(
    item: ItemCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        return create_item(db, item,user_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Item creation failed: {str(e)}"
        )

# 재고 항목 추가 (OCR 기반)
@router.post("/upsert")
def upsert_items_api(
    items: list[ItemCreate], 
    user_id: int,  # 프론트에서 user_id를 직접 넘기도록 설계
    db: Session = Depends(get_db)
):
    return upsert_items(db, items, user_id)