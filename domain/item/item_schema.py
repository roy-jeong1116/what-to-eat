# domain/item/item_schema.py

from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import List, Optional
from domain.ocr.ocr_schema import OCRClassifyItem

# ----------------------------
# 1) 새로 추가된 모델: CategoryResponse
# ----------------------------
class CategoryResponse(BaseModel):
    category_id: int
    category_major_name: str
    category_sub_name: str

    class Config:
        orm_mode = True


# ----------------------------
# 2) 아이템 생성 요청 스키마
# ----------------------------
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


# ----------------------------
# 3) 아이템 조회용 응답 스키마
#    - 이제 `category: CategoryResponse` 필드를 포함합니다.
# ----------------------------
class ItemResponse(BaseModel):
    item_id: int
    user_id: int
    item_name: str
    expiry_date: Optional[date]   # None이면 무기한
    created_at: datetime

    # 여기에 CategoryResponse를 중첩해 주면
    # FastAPI/Pydantic이 ORM에서 로드된 `item.category` 관계를
    # 자동으로 직렬화해 줍니다.
    category: CategoryResponse

    class Config:
        orm_mode = True


# ----------------------------
# 4) 아이템 삭제 요청/응답 스키마
# ----------------------------
class ItemDeleteRequest(BaseModel):
    item_ids: List[int]

    class Config:
        orm_mode = True


class ItemDeleteResponse(BaseModel):
    deleted_items: List[ItemResponse]

    class Config:
        orm_mode = True

# ----------------------------
# 5) OCR 기반 업서트 스키마
# ----------------------------

class OCRUpsertItem(BaseModel):
    item_name: str
    category_major_name: str
    category_sub_name: str
    expiry_text: str
    expiry_date: Optional[date] = None   # <— allow explicit override

# ----------------------------
# 6) OCR 기반 업서트 요청 스키마
# ----------------------------
class ItemUpsertRequest(BaseModel):
    user_id: int
    items: list[OCRUpsertItem]

    class Config:
        orm_mode = True
