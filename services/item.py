from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.item import Item
from schemas.item import ItemCreate, ItemUpdate


def get_items(db: Session) -> list[Item]:
    """Return all non-deleted items."""
    return db.query(Item).filter(Item.is_deleted == False).all()  # noqa: E712


def get_item_by_id(item_id: int, db: Session) -> Item:
    """
    Return a single non-deleted item by ID.

    Raises:
        HTTPException: 404 if the item does not exist or has been soft-deleted.
    """
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.is_deleted == False)  # noqa: E712
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


def create_item(payload: ItemCreate, owner_id: int, db: Session) -> Item:
    """
    Persist a new item owned by *owner_id*.

    Args:
        payload: Validated create payload.
        owner_id: ID of the authenticated user creating the item.
        db: SQLAlchemy session.
    """
    item = Item(
        title=payload.title,
        description=payload.description,
        owner_id=owner_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(item_id: int, payload: ItemUpdate, db: Session) -> Item:
    """
    Partially update an existing item.

    Only non-None fields in *payload* are applied.

    Raises:
        HTTPException: 404 if item not found.
    """
    item = get_item_by_id(item_id, db)

    if payload.title is not None:
        item.title = payload.title
    if payload.description is not None:
        item.description = payload.description

    db.commit()
    db.refresh(item)
    return item


def delete_item(item_id: int, db: Session) -> None:
    """
    Soft-delete an item by setting ``is_deleted = True``.

    Raises:
        HTTPException: 404 if item not found.
    """
    item = get_item_by_id(item_id, db)
    item.is_deleted = True
    db.commit()
