from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from domain.item.item_schema import ItemCreate
from domain.ocr.ocr_service import parse_expiry
from models import Item, Category
from typing import List

def get_or_create_category(
    db: Session,
    major: str,
    sub: str
) -> Category:
    cat = (
        db.query(Category)
          .filter(
             Category.category_major_name == major,
             Category.category_sub_name  == sub
          )
          .first()
    )
    if not cat:
        cat = Category(
            category_major_name=major,
            category_sub_name = sub
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
    return cat

def create_item(db: Session, item_create: ItemCreate):
    # 1) 아이템 생성 전, category 레코드 확보
    cat = get_or_create_category(
        db,
        item_create.category_major_name,
        item_create.category_sub_name
    )
    # 2) 이제 DB에 FK로 넣을 수 있는 category_id 가 준비됨
    payload = item_create.model_dump()
    payload.pop("category_major_name")
    payload.pop("category_sub_name")
    payload["category_id"] = cat.category_id
    db_item = Item(**payload)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items_by_user(db: Session, user_id: int) -> List[Item]:
    return (
        db.query(Item)
          .filter(Item.user_id == user_id)
          .order_by(Item.created_at.desc())
          .all()
    )

def delete_items_by_user(db: Session, user_id: int, item_ids: List[int]) -> List[Item]:
    """
    주어진 user_id와 item_ids에 해당하는 Item 객체들을 먼저 조회한 뒤,
    일괄 삭제하고, 삭제된 Item 리스트를 반환합니다.
    """
    # 1) 삭제 대상 조회
    # category 관계를 미리 불러와(detached 후에도 메모리에 유지)
    to_delete = (
        db.query(Item)
          .options(joinedload(Item.category))
          .filter(Item.user_id == user_id, Item.item_id.in_(item_ids))
          .all()
    )
    if not to_delete:
        return []

    # 2) 객체 단위 삭제
    for item in to_delete:
        db.delete(item)

# ocr 재고 추가
def upsert_items(db: Session, items: List[ItemCreate], user_id: int):
    """
    items: List[ItemCreate] (각각 category_major_name, category_sub_name 포함)
    user_id: 현재 사용자
    - 이미 있는 item_name+category → expiry_date, created_at 업데이트
    - 없으면 새 Item 생성
    """
    updated_items: List[Item] = []

    for item in items:
        # 1) 카테고리 확보
        cat = get_or_create_category(db, item.category_major_name, item.category_sub_name)

        

        # 2) 기존 아이템 검색 (user_id+item_name+category_id)
        db_item = (
            db.query(Item)
                .filter_by(
                    user_id=user_id,
                    item_name=item.item_name,
                    category_id=cat.category_id
                )
                .first()
        )

        if db_item:
            # 기존 재고: 유통기한만 갱신, 생성일 갱신
            db_item.expiry_date = item.expiry_date
            db_item.created_at = datetime.now(timezone.utc)
        else:
            # 신규 재고 생성
            payload = item.model_dump()
            # Pydantic 입력에서 제거
            payload.pop("category_major_name")
            payload.pop("category_sub_name")
            payload["category_id"] = cat.category_id
            payload["user_id"] = user_id

            db_item = Item(**payload)
            db.add(db_item)
        # 기존이든 신규이든 updated_items에 추가
        updated_items.append(db_item)   

    db.commit()
    for item in updated_items:
        db.refresh(item)

    return updated_items  # 최종 반영된 아이템 리스트 반환