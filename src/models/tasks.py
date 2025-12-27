"""
Task model for the Multi-Agent Todo Application.

Defines the core Task entity with validation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    """
    Represents a todo task.

    Attributes:
        id: Unique identifier for the task (UUID4).
        title: Task title (1-200 characters).
        description: Optional task description (max 1000 characters).
        status: Task completion status ('pending' or 'completed').
        created_at: When the task was created.
        updated_at: When the task was last modified.
        completed_at: When the task was marked complete (None if pending).
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: Literal["pending", "completed"] = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace-only."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace-only")
        return stripped

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Strip whitespace from description if provided."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return v

    def mark_complete(self) -> Task:
        """Return a new Task marked as completed."""
        now = datetime.now(UTC)
        return self.model_copy(
            update={
                "status": "completed",
                "completed_at": now,
                "updated_at": now,
            }
        )

    def mark_pending(self) -> Task:
        """Return a new Task marked as pending."""
        return self.model_copy(
            update={
                "status": "pending",
                "completed_at": None,
                "updated_at": datetime.now(UTC),
            }
        )

    def update(self, title: str | None = None, description: str | None = None) -> Task:
        """Return a new Task with updated fields."""
        updates: dict[str, str | datetime | None] = {"updated_at": datetime.now(UTC)}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        return self.model_copy(update=updates)

    model_config = {"frozen": False, "extra": "forbid"}
