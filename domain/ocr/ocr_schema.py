from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class BoundingBox(BaseModel):
    """텍스트 영역의 좌표 정보"""
    x: int
    y: int
    width: int
    height: int

class ReceiptItem(BaseModel):
    """영수증 항목 모델"""
    original_text: str
    item_name: str
    category_name: str
    receipt_date: date
    expiry_date: date
    bounding_box: Optional[BoundingBox] = None

class OCRExtractResponse(BaseModel):
    """OCR 추출 응답"""
    extracted_text: str
    ocr_id: str
    items: List[ReceiptItem]
    receipt_date: date
    detected_items_count: int  # 감지된 항목 수
    missing_items_likely: bool  # 누락 항목 가능성

class NewItemRequest(BaseModel):
    """누락된 항목 추가 요청 - 식재료명만 입력해도 LLM이 자동 추론"""
    item_name: str
    category_name: Optional[str] = None  # 선택적 입력, 없으면 LLM이 추론
    expiry_date: Optional[date] = None  # 선택적 입력, 없으면 LLM이 권장소비기한 계산

class FoodInfo(BaseModel):
    """LLM이 반환하는 식품 정보"""
    category: str
    shelf_life_days: int
    description: Optional[str] = None

class OCREditRequest(BaseModel):
    """OCR 편집 요청"""
    ocr_id: str
    user_id: str
    items: List[ReceiptItem]

class OCREditResponse(BaseModel):
    """OCR 편집 응답"""
    success: bool
    item_ids: List[int]