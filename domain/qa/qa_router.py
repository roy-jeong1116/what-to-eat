from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from domain.qa.qa_service import recommend_recipes_from_fridge
from database import get_db
from auth import get_current_user
from domain.user.user_schema import UserResponse  # 현재 로그인한 사용자 스키마

router = APIRouter(
    prefix="/qa",
    tags=["QA / Recipe"]
)

@router.get("/{user_id}/recommend-recipes")
def recommend_recipes(
    user_id : int= Path(..., description="요청할 사용자의 ID"),
    user_request: str = Query(..., description="예: 맵지 않은 요리, 간단한 도시락, 아이가 좋아할만한 반찬 등"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    사용자의 냉장고 재료와 요청에 기반해 레시피 추천
    """

    # 🔐 보안 체크 (선택 사항): 경로의 user_id가 로그인 사용자와 일치하는지 확인
    if user_id != current_user.user_id:
        return {"error": "권한이 없습니다."}
    

    result = recommend_recipes_from_fridge(
        db=db,
        user_id=user_id,
        user_request=user_request
    )
    # result = recommend_recipes_from_fridge(db, current_user.user_id, user_request)
    return {"result": result}
