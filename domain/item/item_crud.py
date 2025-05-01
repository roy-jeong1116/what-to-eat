from datetime import datetime, timezone
from sqlalchemy.orm import Session
from domain.item.item_schema import ItemCreate
from models import Item

def create_item(db: Session, item_create: ItemCreate):
    db_item = Item(
        **item_create.model_dump(),
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item