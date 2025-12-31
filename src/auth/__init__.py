"""
Authentication module for the Multi-Agent Todo Application.

Phase II: JWT-based authentication for web API.
"""

from __future__ import annotations

from src.auth.dependencies import (
    CurrentUser,
    CurrentUserWithToken,
    get_current_user,
    get_current_user_with_token,
)
from src.auth.jwt import create_access_token, get_user_id_from_token, verify_token
from src.auth.password import hash_password, verify_password

__all__ = [
    # JWT
    "create_access_token",
    "verify_token",
    "get_user_id_from_token",
    # Password
    "hash_password",
    "verify_password",
    # Dependencies
    "get_current_user",
    "CurrentUser",
    "get_current_user_with_token",
    "CurrentUserWithToken",
]
