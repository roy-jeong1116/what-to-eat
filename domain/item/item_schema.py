from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime

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

class ItemResponse(ItemCreate):
    item_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }