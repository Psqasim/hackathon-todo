"""
JWT token validation for MCP server.

This module provides authentication utilities to validate JWT tokens
passed from the frontend and extract user information.

FR-009: MCP server MUST validate JWT token and pass user_id to all backend API calls
FR-028: MCP server MUST reject requests without valid JWT token
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from starlette.requests import Request

# Reuse existing JWT utilities from Phase II
from src.auth.jwt import TokenError, get_user_id_from_token, verify_token

logger = structlog.get_logger()


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def extract_token_from_header(authorization: str | None) -> str:
    """Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")

    Returns:
        JWT token string

    Raises:
        AuthenticationError: If header is missing or malformed
    """
    if not authorization:
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization header format. Expected 'Bearer <token>'")

    return parts[1]


def validate_token(token: str) -> dict:
    """Validate a JWT token and return the payload.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = verify_token(token)
        logger.debug("mcp_token_validated", user_id=payload.get("sub"))
        return payload
    except TokenError as e:
        logger.warning("mcp_token_validation_failed", error=str(e))
        raise AuthenticationError(f"Invalid token: {e}") from e


def get_user_id(token: str) -> str:
    """Extract user ID from a JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID from the token

    Raises:
        AuthenticationError: If token is invalid or missing user ID
    """
    try:
        user_id = get_user_id_from_token(token)
        logger.debug("mcp_user_id_extracted", user_id=user_id)
        return user_id
    except TokenError as e:
        raise AuthenticationError(f"Failed to extract user ID: {e}") from e


async def authenticate_request(request: Request) -> str:
    """Authenticate an incoming request and return user ID.

    This is the main authentication function for MCP endpoints.
    It extracts the JWT token from the Authorization header,
    validates it, and returns the user ID.

    Args:
        request: Starlette request object

    Returns:
        User ID from the authenticated token

    Raises:
        AuthenticationError: If authentication fails
    """
    authorization = request.headers.get("Authorization")
    token = extract_token_from_header(authorization)
    return get_user_id(token)


def get_token_from_request(request: Request) -> str:
    """Get the raw JWT token from a request.

    Useful when we need to pass the token to the backend client.

    Args:
        request: Starlette request object

    Returns:
        JWT token string

    Raises:
        AuthenticationError: If token is missing
    """
    authorization = request.headers.get("Authorization")
    return extract_token_from_header(authorization)


# Export commonly used items
__all__ = [
    "AuthenticationError",
    "authenticate_request",
    "extract_token_from_header",
    "get_token_from_request",
    "get_user_id",
    "validate_token",
]
