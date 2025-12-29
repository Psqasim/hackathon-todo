"""
Task model for the Multi-Agent Todo Application.

Defines the core Task entity with validation.
Phase II: Added TaskDB SQLModel with user_id for multi-user support.
Phase II Enhancement: Added priority, due_date, tags, and recurring support.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field, field_validator
from sqlmodel import JSON, Column
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel

if TYPE_CHECKING:
    pass


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


def generate_task_id() -> str:
    """Generate a unique task ID."""
    from uuid import uuid4

    return str(uuid4())


class Task(BaseModel):
    """
    Represents a todo task.

    Attributes:
        id: Unique identifier for the task (UUID4).
        title: Task title (1-200 characters).
        description: Optional task description (max 1000 characters).
        status: Task completion status ('pending' or 'completed').
        priority: Task priority level (low, medium, high, urgent).
        due_date: Optional due date for the task.
        tags: List of tags for categorization.
        is_recurring: Whether the task repeats.
        recurrence_pattern: How often the task repeats.
        created_at: When the task was created.
        updated_at: When the task was last modified.
        completed_at: When the task was marked complete (None if pending).
    """

    id: str = Field(default_factory=generate_task_id)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: Literal["pending", "completed"] = "pending"
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    is_recurring: bool = False
    recurrence_pattern: RecurrencePattern | None = None
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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags."""
        # Strip whitespace and remove empty tags
        normalized = [tag.strip().lower() for tag in v if tag.strip()]
        # Remove duplicates while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for tag in normalized:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
        return unique[:10]  # Limit to 10 tags

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

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
        is_recurring: bool | None = None,
        recurrence_pattern: RecurrencePattern | None = None,
    ) -> Task:
        """Return a new Task with updated fields."""
        updates: dict[str, str | datetime | list[str] | bool | TaskPriority | RecurrencePattern | None] = {
            "updated_at": datetime.now(UTC)
        }
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if priority is not None:
            updates["priority"] = priority
        if due_date is not None:
            updates["due_date"] = due_date
        if tags is not None:
            updates["tags"] = tags
        if is_recurring is not None:
            updates["is_recurring"] = is_recurring
        if recurrence_pattern is not None:
            updates["recurrence_pattern"] = recurrence_pattern
        return self.model_copy(update=updates)

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None or self.status == "completed":
            return False
        return datetime.now(UTC) > self.due_date

    model_config = {"frozen": False, "extra": "forbid"}


class TaskDB(SQLModel, table=True):
    """
    Database model for tasks with user ownership.

    SQLModel table for PostgreSQL persistence.
    Phase II: Added user_id for multi-user task isolation.
    Phase II Enhancement: Added priority, due_date, tags, recurring fields.
    """

    __tablename__ = "tasks"  # type: ignore[assignment]

    id: str = SQLField(default_factory=generate_task_id, primary_key=True)
    user_id: str = SQLField(foreign_key="users.id", index=True)
    title: str = SQLField(max_length=200)
    description: str | None = SQLField(default=None, max_length=1000)
    status: str = SQLField(default="pending")  # 'pending' or 'completed'
    priority: str = SQLField(default="medium")  # low, medium, high, urgent
    due_date: datetime | None = SQLField(default=None)
    tags: list[str] = SQLField(default_factory=list, sa_column=Column(JSON))
    is_recurring: bool = SQLField(default=False)
    recurrence_pattern: str | None = SQLField(default=None)  # daily, weekly, monthly, yearly
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = SQLField(default=None)

    def to_task(self) -> Task:
        """Convert to Task Pydantic model (for API responses)."""
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            status=self.status,  # type: ignore[arg-type]
            priority=TaskPriority(self.priority),
            due_date=self.due_date,
            tags=self.tags or [],
            is_recurring=self.is_recurring,
            recurrence_pattern=RecurrencePattern(self.recurrence_pattern) if self.recurrence_pattern else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
            completed_at=self.completed_at,
        )


def task_to_db(task: Task, user_id: str) -> TaskDB:
    """Convert Task Pydantic model to TaskDB SQLModel."""
    return TaskDB(
        id=task.id,
        user_id=user_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority.value,
        due_date=task.due_date,
        tags=task.tags,
        is_recurring=task.is_recurring,
        recurrence_pattern=task.recurrence_pattern.value if task.recurrence_pattern else None,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


def db_to_task(db_task: TaskDB) -> Task:
    """Convert TaskDB SQLModel to Task Pydantic model."""
    return db_task.to_task()
