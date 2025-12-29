"""
Application configuration for Phase II.

Loads environment variables with sensible defaults.
Supports Railway deployment detection.
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

# Detect if running on Railway
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")


def get_frontend_url() -> str:
    """Get frontend URL based on environment."""
    env_url = os.getenv("FRONTEND_URL")
    if env_url:
        return env_url
    if IS_RAILWAY:
        return "https://hackathon-todo.vercel.app"
    return "http://localhost:3000"


def get_backend_url() -> str:
    """Get backend URL based on environment."""
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url
    if IS_RAILWAY and RAILWAY_PUBLIC_DOMAIN:
        return f"https://{RAILWAY_PUBLIC_DOMAIN}"
    return "http://localhost:8000"


def get_allowed_origins() -> list[str]:
    """Get CORS allowed origins."""
    origins = [
        get_frontend_url(),
        "http://localhost:3000",  # Local development
    ]
    # Add Vercel preview deployments pattern
    if IS_RAILWAY:
        origins.extend([
            "https://hackathon-todo.vercel.app",
            "https://hackathon-todo-*.vercel.app",
        ])
    return origins


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
        default_factory=get_frontend_url,
        alias="FRONTEND_URL",
        description="Frontend URL for CORS",
    )

    # Backend URL (for OAuth callbacks)
    backend_url: str = Field(
        default_factory=get_backend_url,
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

# CORS allowed origins (computed at module load)
ALLOWED_ORIGINS = get_allowed_origins()
