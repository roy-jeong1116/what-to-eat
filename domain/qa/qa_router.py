from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from domain.qa.qa_service import recommend_recipes_from_fridge
from database import get_db
from auth import get_current_user
from domain.user.user_schema import UserResponse  # 현재 로그인한 사용자 스키마

router = APIRouter(
    prefix="/qa",
    tags=["QA / Recipe"]
)

@router.get("/recommend-recipes")
def recommend_recipes(
    user_request: str = Query(..., description="예: 맵지 않은 요리, 간단한 도시락, 아이가 좋아할만한 반찬 등"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    사용자의 냉장고 재료와 요청에 기반해 레시피 추천
    """
    result = recommend_recipes_from_fridge(db, current_user.id, user_request)
    return {"result": result}
