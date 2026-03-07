from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: The raw password string to hash.

    Returns:
        A bcrypt-hashed password string safe to store in the database.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password: The password supplied by the user.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        ``True`` if the passwords match, ``False`` otherwise.
        Never raises – invalid inputs return ``False``.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (AttributeError, TypeError, ValueError):
        return False


def create_access_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: timedelta = timedelta(minutes=30),
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: Unique identifier embedded in the ``sub`` claim (typically ``str(user.id)``).
        secret_key: HMAC signing key (read from ``JWT_SECRET_KEY`` env var).
        algorithm: JWT signing algorithm (default: ``HS256``).
        expires_delta: Token lifetime. Defaults to 30 minutes.

    Returns:
        A signed JWT string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT string to decode.
        secret_key: The signing key used when the token was created.
        algorithm: JWT algorithm (must match the one used at creation).

    Returns:
        The decoded payload dictionary.

    Raises:
        ValueError: If the token is invalid, expired, or cannot be decoded.
    """
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
