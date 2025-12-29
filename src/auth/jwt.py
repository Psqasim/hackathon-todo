"""
JWT Token handling for authentication.

Phase II: Create and verify JWT tokens using python-jose.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from jose import JWTError, jwt

from src.config import settings

logger = structlog.get_logger()


class TokenError(Exception):
    """Exception raised for token-related errors."""

    pass


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.jwt_expiration_days)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    logger.debug("jwt_token_created", sub=data.get("sub"))
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string to verify.

    Returns:
        Decoded token payload.

    Raises:
        TokenError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        logger.debug("jwt_token_verified", sub=payload.get("sub"))
        return payload
    except JWTError as e:
        logger.warning("jwt_token_invalid", error=str(e))
        raise TokenError(f"Invalid token: {e}") from e


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from a JWT token.

    Args:
        token: The JWT token string.

    Returns:
        User ID from the token's 'sub' claim.

    Raises:
        TokenError: If the token is invalid or missing user ID.
    """
    payload = verify_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise TokenError("Token missing user ID (sub claim)")

    return user_id
