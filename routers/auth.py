from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from core.auth import get_current_active_user
from models.user import User
from schemas.auth import AuthUserResponse, LoginRequest, TokenResponse
from services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description=(
        "Authenticate with email and password. Returns a JWT access token on success. "
        "The token must be passed as `Authorization: Bearer <token>` on protected routes."
    ),
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.authenticate_user(payload, db)


@router.get(
    "/me",
    response_model=AuthUserResponse,
    summary="Get current user",
    description="Return the profile of the currently authenticated user. Requires a valid bearer token.",
)
def current_user(current_user: User = Depends(get_current_active_user)):
    return current_user
