from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from core.auth import get_current_active_user
from models.user import User
from schemas.user import UserCreate, UserResponse
from services import user as user_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List users",
    description="Return all registered users. Requires a valid bearer token.",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return user_service.get_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user",
    description="Fetch a single user by their integer ID. Returns 404 if not found. Requires authentication.",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return user_service.get_user(user_id, db)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description="Register a new user account. Email and username must be unique.",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(payload, db)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Permanently delete a user account. Requires authentication.",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    user_service.delete_user(user_id, db)
    return None
