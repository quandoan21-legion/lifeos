from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def _create_token(
    user_id: UUID,
    expires_delta: timedelta,
    token_type: str,
) -> tuple[str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
        "type": token_type,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def create_access_token(user_id: UUID) -> tuple[str, datetime]:
    return _create_token(
        user_id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(user_id: UUID) -> tuple[str, datetime]:
    return _create_token(
        user_id,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
