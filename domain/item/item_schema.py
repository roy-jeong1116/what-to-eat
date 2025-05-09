from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime
from typing import List, Optional

# Item 입력 스키마
class ItemCreate(BaseModel):
    # user_id: int
    item_name: str
    category_major_name: str
    category_sub_name: str
    expiry_date: date | None = None
    

    # class Config:
    #     orm_mode = True
        
    @field_validator("item_name")
    @staticmethod
    def not_empty(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v
# 직접 입력    
class ItemCreateInput(BaseModel):
    item_name: str
    category_major_name: str
    category_sub_name: str
    expiry_text: str  # `expiry_text`를 입력받음

    @field_validator("item_name")
    @staticmethod
    def not_empty(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v
    
class CategoryResponse(BaseModel):
    category_id: int
    category_major_name: str
    category_sub_name: str

    # model_config = {
    #     "from_attributes": True
    # }
    class Config:
        orm_mode = True  # orm_mode 활성화

# 아이템 조회용 응답 스키마
class ItemResponse(BaseModel):
    item_id: int
    user_id: int
    item_name: str
    expiry_date: Optional[date]
    created_at: datetime
    category: CategoryResponse

    # model_config = {
    #     "from_attributes": True
    # }
    class Config:
        orm_mode = True  # orm_mode 활성화
# 삭제 요청 바디 스키마
class ItemDeleteRequest(BaseModel):
    item_ids: List[int]

# 삭제 응답 스키마: 실제 삭제된 아이템 목록 반환
class ItemDeleteResponse(BaseModel):
    deleted_items: List[ItemResponse]

    model_config = {
        "from_attributes": True
    }

class ItemUpsertRequest(BaseModel):
    user_id: int
    items: List[ItemCreate]