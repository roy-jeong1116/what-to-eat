from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from .ocr_schema import (
    OCRExtractResponse, OCRClassifyRequest,
    OCRClassifyResponse, OCRSaveRequest, OCRSaveResponse
)
from .ocr_service import (
    extract_names_from_image, classify_names, parse_expiry
)
from domain.item.item_crud import upsert_items
from domain.item.item_schema import ItemCreate
from database import get_db

from fastapi import Path

router = APIRouter(prefix="/ocr")

@router.post("/extract-names", response_model=OCRExtractResponse)
async def extract_names_endpoint(file: UploadFile = File(...)):
    try:
        img = await file.read()
        names = extract_names_from_image(img)
        return {"extracted_names": names}
    except Exception as e:
        raise HTTPException(400, f"OCR 추출 실패: {e}")

@router.post("/classify-names", response_model=OCRClassifyResponse)
async def classify_names_endpoint(req: OCRClassifyRequest):
    try:
        items = classify_names(req.names)
        return {"items": items}
    except Exception as e:
        raise HTTPException(500, f"분류 실패: {e}")

@router.post("/save-items", response_model=OCRSaveResponse)
def save_items_endpoint(
    req: OCRSaveRequest,
    db: Session = Depends(get_db)
):
    # 1) OCR에서 받은 expiry_text → expiry_date 변환
    item_list: list[ItemCreate] = []
    for it in req.items:
        expiry_date = parse_expiry(it.expiry_text)
        item_list.append(ItemCreate(
            item_name=it.item_name,
            category_major_name=it.category_major_name,
            category_sub_name=it.category_sub_name,
            expiry_date=expiry_date
        ))

    # 2) DB에 upsert (user_id는 upsert_items 함수에 전달)
    try:
        updated_items = upsert_items(db, item_list, req.user_id)
    except Exception as e:
        raise HTTPException(500, f"Item 저장 실패: {e}")

    # 3) 저장된 아이템 ID 리스트 반환
    saved_ids = [itm.item_id for itm in updated_items]
    return {"saved_items": saved_ids}
