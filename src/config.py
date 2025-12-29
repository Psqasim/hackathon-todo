"""
Application configuration for Phase II.

Loads environment variables with sensible defaults.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(
        default="sqlite:///./todo.db",
        alias="DATABASE_URL",
        description="Database connection string",
    )

    # JWT Authentication
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        alias="JWT_SECRET_KEY",
        description="Secret key for JWT token signing",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
        description="Algorithm for JWT token signing",
    )
    jwt_expiration_days: int = Field(
        default=7,
        alias="JWT_EXPIRATION_DAYS",
        description="JWT token expiration in days",
    )

    # Better Auth (shared secret with frontend)
    better_auth_secret: str = Field(
        default="dev-better-auth-secret-change-in-production",
        alias="BETTER_AUTH_SECRET",
        description="Shared secret for Better Auth",
    )

    # CORS
    frontend_url: str = Field(
        default="http://localhost:3000",
        alias="FRONTEND_URL",
        description="Frontend URL for CORS",
    )

    # Backend URL (for OAuth callbacks)
    backend_url: str = Field(
        default="http://localhost:8000",
        alias="BACKEND_URL",
        description="Backend URL for OAuth callbacks",
    )

    # OAuth - Google
    google_client_id: str = Field(
        default="",
        alias="GOOGLE_CLIENT_ID",
        description="Google OAuth Client ID",
    )
    google_client_secret: str = Field(
        default="",
        alias="GOOGLE_CLIENT_SECRET",
        description="Google OAuth Client Secret",
    )

    # OAuth - GitHub
    github_client_id: str = Field(
        default="",
        alias="GITHUB_CLIENT_ID",
        description="GitHub OAuth Client ID",
    )
    github_client_secret: str = Field(
        default="",
        alias="GITHUB_CLIENT_SECRET",
        description="GitHub OAuth Client Secret",
    )

    # Environment
    environment: Literal["development", "production", "test"] = Field(
        default="development",
        alias="ENVIRONMENT",
        description="Application environment",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience accessors
settings = get_settings()
