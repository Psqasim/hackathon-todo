"""
User model for the Multi-Agent Todo Application.

Defines the User entity for authentication and task ownership.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel

if TYPE_CHECKING:
    pass


class UserBase(BaseModel):
    """Base user model with common fields."""

    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")


class UserCreate(UserBase):
    """User creation request model."""

    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")


class UserLogin(BaseModel):
    """User login request model."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class User(UserBase):
    """User response model (without password)."""

    id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")


class UserDB(SQLModel, table=True):
    """
    Database model for users.

    SQLModel table for PostgreSQL persistence.
    """

    __tablename__ = "users"  # type: ignore[assignment]

    id: str = SQLField(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = SQLField(unique=True, index=True, max_length=255)
    name: str = SQLField(max_length=100)
    hashed_password: str = SQLField(max_length=255)
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))

    def to_user(self) -> User:
        """Convert to User response model (without password)."""
        return User(
            id=self.id,
            email=self.email,
            name=self.name,
            created_at=self.created_at,
        )
