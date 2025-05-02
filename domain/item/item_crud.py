from datetime import datetime, timezone
from sqlalchemy.orm import Session
from domain.item.item_schema import ItemCreate
from models import Item
from typing import List

def create_item(db: Session, item_create: ItemCreate):
    db_item = Item(
        **item_create.model_dump(),
        created_at=datetime.now(timezone.utc)
    )
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
    to_delete = (
        db.query(Item)
          .filter(Item.user_id == user_id, Item.item_id.in_(item_ids))
          .all()
    )
    if not to_delete:
        return []

    # 2) 객체 단위 삭제
    for item in to_delete:
        db.delete(item)
    db.commit()

    return to_delete
