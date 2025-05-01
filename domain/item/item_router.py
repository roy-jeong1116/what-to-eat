from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.item.item_schema import ItemCreate, ItemResponse
from domain.item.item_crud import create_item
from database import get_db

router = APIRouter(
    prefix="/item",
)

@router.post("/create", response_model=ItemResponse)
def create_new_item(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_item(db, item)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Item creation failed: {str(e)}"
        )
