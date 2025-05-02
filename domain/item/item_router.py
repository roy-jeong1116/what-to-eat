from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domain.item.item_schema import ItemCreate, ItemResponse, ItemDeleteRequest, ItemDeleteResponse
from domain.item.item_crud import create_item, get_items_by_user, delete_items_by_user
from database import get_db
from typing import List

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

@router.get("/users/{user_id}/items", response_model=List[ItemResponse])
def read_items_by_user(user_id: int, db: Session = Depends(get_db)) -> List[ItemResponse]:
    return get_items_by_user(db, user_id)

@router.delete(
    "/users/{user_id}/items",
    response_model=ItemDeleteResponse,
    summary="Delete Items By User"
)
def delete_items_by_user_endpoint(
    user_id: int,
    req: ItemDeleteRequest,
    db: Session = Depends(get_db)
) -> ItemDeleteResponse:
    deleted_items = delete_items_by_user(db, user_id, req.item_ids)
    if not deleted_items:
        raise HTTPException(status_code=404, detail="삭제할 항목이 없습니다.")

    # Pydantic으로 변환하여 응답
    return ItemDeleteResponse(deleted_items=deleted_items)
    

    