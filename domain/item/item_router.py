from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from domain.item.item_schema import ItemCreate, ItemResponse, ItemDeleteRequest, ItemDeleteResponse, ItemUpsertRequest
from domain.item.item_crud import get_items_by_user, delete_items_by_user, upsert_items
from domain.ocr.ocr_service import parse_expiry

from database import get_db
from typing import List

from fastapi import Body

router = APIRouter(
    prefix="/item/{user_id}",
)


@router.get("/", response_model=List[ItemResponse])
def read_items_by_user(user_id: int, db: Session = Depends(get_db)) -> List[ItemResponse]:
    # get_items_by_user 에서 Category 관계가 이미 로드되므로
    # Pydantic이 category_major_name/sub_name까지 직렬화해 줍니다.
    return get_items_by_user(db, user_id)

@router.delete(
    "/delete",
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
@router.post("/upsert", response_model=list[ItemResponse])
def upsert_items_api(req: ItemUpsertRequest, db: Session = Depends(get_db)):
    converted: list[ItemCreate] = []
    for it in req.items:
        # if the frontend gave us expiry_date, honor it:
        expiry = it.expiry_date
        if expiry is None and it.expiry_text:
            # fallback to old parse
            from domain.ocr.ocr_service import parse_expiry
            expiry = parse_expiry(it.expiry_text)
        converted.append(ItemCreate(
            user_id             = req.user_id,
            item_name           = it.item_name,
            category_major_name = it.category_major_name,
            category_sub_name   = it.category_sub_name,
            expiry_date         = expiry
        ))
    updated = upsert_items(db, converted, req.user_id)
    return updated