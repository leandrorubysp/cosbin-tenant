from typing import List, Optional

from sqlalchemy.orm import Session

from .database import current_tenant_id
from .models import Item


def get_current_tenant_or_fail() -> int:
    tenant_id = current_tenant_id.get()
    if tenant_id is None:
        raise RuntimeError("Tenant not set in context")
    return tenant_id


def create_item(db: Session, name: str) -> Item:
    tenant_id = get_current_tenant_or_fail()
    item = Item(name=name, tenant_id=tenant_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, item_id: int) -> Optional[Item]:
    tenant_id = get_current_tenant_or_fail()
    return (
        db.query(Item)
        .filter(Item.id == item_id, Item.tenant_id == tenant_id)
        .first()
    )


def list_items(db: Session) -> List[Item]:
    tenant_id = get_current_tenant_or_fail()
    return db.query(Item).filter(Item.tenant_id == tenant_id).all()