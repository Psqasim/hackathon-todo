"""
FastAPI dependencies for authentication.

Phase II: Dependency injection for protected endpoints.
"""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.jwt import TokenError, get_user_id_from_token

logger = structlog.get_logger()

# HTTP Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
) -> str:
    """
    FastAPI dependency to get the current authenticated user.

    Extracts and validates the JWT token from the Authorization header.

    Args:
        credentials: HTTP Bearer credentials from the request.

    Returns:
        User ID from the validated token.

    Raises:
        HTTPException: If authentication fails (401 Unauthorized).
    """
    if credentials is None:
        logger.warning("auth_missing_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = get_user_id_from_token(credentials.credentials)
        logger.debug("auth_user_authenticated", user_id=user_id)
        return user_id
    except TokenError as e:
        logger.warning("auth_token_invalid", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Type alias for dependency injection
CurrentUser = Annotated[str, Depends(get_current_user)]


def verify_user_access(current_user: str, user_id: str) -> None:
    """
    Verify that the current user can access the requested user's resources.

    Args:
        current_user: The authenticated user's ID.
        user_id: The user ID being accessed.

    Raises:
        HTTPException: If access is denied (403 Forbidden).
    """
    if current_user != user_id:
        logger.warning(
            "auth_access_denied",
            current_user=current_user,
            requested_user=user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
