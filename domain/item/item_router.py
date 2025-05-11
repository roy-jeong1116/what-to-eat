from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from domain.item.item_schema import ItemCreate, ItemResponse, ItemDeleteRequest, ItemDeleteResponse, ItemUpsertRequest
from domain.item.item_crud import get_items_by_user, delete_items_by_user, upsert_items
from domain.ocr.ocr_service import parse_expiry

from database import get_db
from typing import List

from fastapi import Body

router = APIRouter(
    prefix="/users/{user_id}/item",
)


@router.get("/items", response_model=List[ItemResponse])
def read_items_by_user(user_id: int, db: Session = Depends(get_db)) -> List[ItemResponse]:
    return get_items_by_user(db, user_id)

@router.delete(
    "/items",
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
    
# 재고 항목 업서트 (OCR 기반)
@router.post(
    "/upsert",
    response_model=List[ItemResponse],
    # summary="Upsert multiple items: update expiry if exists, else create"
)
def upsert_items_api(request: ItemUpsertRequest, db: Session = Depends(get_db)) -> List[ItemResponse]:
    converted_items = []
    for item in request.items:
        expiry_date = parse_expiry(item.expiry_text)
        converted_items.append(ItemCreate(
            user_id=request.user_id,
            item_name=item.item_name,
            category_major_name=item.category_major_name,
            category_sub_name=item.category_sub_name,
            expiry_date=expiry_date
        ))

    updated = upsert_items(db, converted_items, request.user_id)
    return updated
