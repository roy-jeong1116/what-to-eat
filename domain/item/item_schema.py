from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime
from typing import List

# Item 입력 스키마
class ItemCreate(BaseModel):
    # user_id: int
    item_name: str
    category_name: str
    expiry_date: date | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("item_name", "category_name")
    @staticmethod
    def not_empty(v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

# 아이템 조회용 응답 스키마
class ItemResponse(ItemCreate):
    item_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# 삭제 요청 바디 스키마
class ItemDeleteRequest(BaseModel):
    item_ids: List[int]

# 삭제 응답 스키마: 실제 삭제된 아이템 목록 반환환
class ItemDeleteResponse(BaseModel):
    deleted_items: List[ItemResponse]

    class Config:
        from_attributes = True