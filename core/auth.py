from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.database import get_db
from core.config import settings
from core.security import decode_access_token
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def _credentials_exception() -> HTTPException:
    """Return a 401 Unauthorized exception for invalid or missing credentials."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency – decode the bearer token and return the matching User.

    Args:
        token: JWT bearer token extracted from the ``Authorization`` header.
        db: Database session injected by FastAPI.

    Returns:
        The authenticated :class:`~models.user.User` instance.

    Raises:
        HTTPException: 401 if the token is invalid, expired, or the user does not exist.
    """
    credentials_exception = _credentials_exception()

    try:
        payload = decode_access_token(
            token=token,
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    except ValueError:
        raise credentials_exception

    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency – ensure the authenticated user is active.

    Wraps :func:`get_current_user` and additionally checks ``User.is_active``.

    Raises:
        HTTPException: 403 if the user account has been deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
