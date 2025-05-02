from datetime import datetime, timezone
from sqlalchemy.orm import Session
from domain.item.item_schema import ItemCreate
from models import Item

def create_item(db: Session, item_create: ItemCreate, user_id: int):
    db_item = Item(
        **item_create.model_dump(),
        user_id=user_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# ocr 재고 추가
def upsert_items(db: Session, items: list[ItemCreate], user_id: int):
    updated_items = []

    for item in items:
        # 이미 등록된 item_name이 있는지 확인 (사용자별로)
        db_item = db.query(Item).filter(
            Item.user_id == user_id,
            Item.item_name == item.item_name
        ).first()

        if db_item:
            # 업데이트
            db_item.expiry_date = item.expiry_date
            db_item.created_at = item.created_at
        else:
            # 생성
            db_item = Item(
                **item.model_dump(),
                user_id=user_id,
                # created_at=datetime.now(timezone.utc)
            )
            db.add(db_item)

        updated_items.append(db_item)

    db.commit()
    for item in updated_items:
        db.refresh(item)

    return updated_items  # 최종 반영된 아이템 리스트 반환