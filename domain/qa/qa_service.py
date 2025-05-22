from sqlalchemy.orm import Session
from domain.item.item_crud import get_items_by_user
from domain.qa.qa_chain import route_request

# # 체인 초기화
# recipe_chain = get_recipe_chain()

def recommend_recipes_from_fridge(db: Session, user_id: int, user_request: str) -> str:
    # 사용자 냉장고 아이템 조회
    user_items = get_items_by_user(db, user_id)
    ingredients = [item.item_name for item in user_items]

    if not ingredients:
        return "냉장고에 재료가 없습니다. 재료를 먼저 등록해주세요."

    # 재료 텍스트로 변환
    ingredient_text = ", ".join(ingredients)

    result = route_request(user_request=user_request, user_ingredients=ingredient_text)
    return result  # AIMessage 객체 → content 문자열 추출
