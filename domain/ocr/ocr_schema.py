from pydantic import BaseModel
from typing import List
from datetime import date

# 1) OCR로 뽑아낸 원본 이름 목록
class OCRExtractResponse(BaseModel):
    extracted_names: List[str]

# 2) 프론트에서 교정된 이름 리스트를 보낼 때
class OCRClassifyRequest(BaseModel):
    names: List[str]

# 3) 분류 + 유통기한 텍스트를 담을 모델
class OCRClassifyItem(BaseModel):
    item_name: str
    major_category: str
    sub_category: str
    expiry_text: str

# 4) 분류 응답
class OCRClassifyResponse(BaseModel):
    items: List[OCRClassifyItem]

# 5) 최종 저장 요청: user_id + 분류된 아이템들
class OCRSaveRequest(BaseModel):
    user_id: int
    items: List[OCRClassifyItem]

# 6) 저장 응답: 생성된 item_id 리스트
class OCRSaveResponse(BaseModel):
    saved_items: List[int]
