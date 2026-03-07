from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from core.auth import get_current_active_user
from models.user import User
from schemas.item import ItemCreate, ItemResponse, ItemUpdate
from services import item as item_service

router = APIRouter(
    prefix="/api/v1/items",
    tags=["items (example)"],
)


@router.get(
    "/",
    response_model=list[ItemResponse],
    summary="List all items",
    description="Returns every non-deleted item. Requires a valid bearer token.",
)
def list_items(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return item_service.get_items(db)


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get a single item",
    description="Fetch one item by its integer ID. Returns 404 if not found or soft-deleted.",
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return item_service.get_item_by_id(item_id, db)


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an item",
    description="Create a new item owned by the currently authenticated user.",
)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return item_service.create_item(payload, owner_id=current_user.id, db=db)


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update an item",
    description="Partially update an item's fields. Only provided fields are changed.",
)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return item_service.update_item(item_id, payload, db)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description="Soft-deletes an item by setting `is_deleted = true`. The record is kept in the database.",
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    item_service.delete_item(item_id, db)
    return None
