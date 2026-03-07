from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.config import settings
from core.security import create_access_token, verify_password
from db.crud import get_user_by_email
from schemas.auth import LoginRequest, TokenResponse


def authenticate_user(payload: LoginRequest, db: Session) -> TokenResponse:
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = get_user_by_email(db, str(payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=str(user.id),
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=int(expires_delta.total_seconds()),
        user=user,
    )
