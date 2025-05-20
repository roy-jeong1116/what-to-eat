from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import List, Optional
from domain.ocr.ocr_schema import OCRClassifyItem

# Item 입력 스키마
class ItemCreate(BaseModel):
    item_name: str
    category_major_name: str
    category_sub_name: str
    expiry_date: Optional[date] = None  # Optional; 무기한 식품은 None

    @field_validator("item_name")
    @staticmethod
    def not_empty(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    class Config:
        orm_mode = True


class CategoryResponse(BaseModel):
    category_id: int
    category_major_name: str
    category_sub_name: str

    class Config:
        orm_mode = True


# 아이템 조회용 응답 스키마
class ItemResponse(BaseModel):
    item_id: int
    user_id: int
    item_name: str
    expiry_date: Optional[date]  # None이면 무기한 식품
    created_at: datetime
    category: CategoryResponse

    class Config:
        orm_mode = True


# 삭제 요청 바디 스키마
class ItemDeleteRequest(BaseModel):
    item_ids: List[int]

    class Config:
        orm_mode = True


# 삭제 응답 스키마: 실제 삭제된 아이템 목록 반환
class ItemDeleteResponse(BaseModel):
    deleted_items: List[ItemResponse]

    class Config:
        orm_mode = True


class ItemUpsertRequest(BaseModel):
    user_id: int
    items: List[OCRClassifyItem]

    class Config:
        orm_mode = True
