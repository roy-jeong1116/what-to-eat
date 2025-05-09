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
    saved_ids: list[int] = []
    item_list = []
    for it in req.items:
        # 1) expiry_text → expiry_date 계산
        expiry_date = parse_expiry(it.expiry_text)
        # 2) ItemCreate 객체 준비
        item_in = ItemCreate(
            user_id=req.user_id, # Path로 받은 값 사용
            item_name=it.item_name,
            category_major_name=it.category_major_name,
            category_sub_name=it.category_sub_name,
            expiry_date=expiry_date
        )
        item_list.append(item_in)
        
    # 3) DB 저장
    try:
        update_items = upsert_items(db, item_list, req.user_id)
    except Exception as e:
        raise HTTPException(500, f"Item 저장 실패: {e}")
    saved_ids = [itm.item_id for itm in update_items]

    return {"saved_items": saved_ids}
