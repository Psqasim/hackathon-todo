"""
API Request and Response models.

Phase II: Pydantic schemas for API validation per OpenAPI spec.
Phase II Enhancement: Added priority, due_date, tags, recurring fields.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# =============================================================================
# Auth Request/Response Models
# =============================================================================


class SignupRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(
        ..., min_length=1, max_length=100, description="User's display name"
    )
    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)"
    )


class SigninRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """User information response."""

    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., description="User's display name")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AuthResponse(BaseModel):
    """Authentication response with user and token."""

    user: UserResponse
    token: str = Field(..., description="JWT access token")


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


# =============================================================================
# Task Request/Response Models
# =============================================================================

# Priority and recurrence types
TaskPriorityType = Literal["low", "medium", "high", "urgent"]
RecurrencePatternType = Literal["daily", "weekly", "monthly", "yearly"]


class CreateTaskRequest(BaseModel):
    """Create task request."""

    title: str = Field(
        ..., min_length=1, max_length=200, description="Task title"
    )
    description: str | None = Field(
        default=None, max_length=1000, description="Optional task description"
    )
    priority: TaskPriorityType = Field(
        default="medium", description="Task priority level"
    )
    due_date: datetime | None = Field(
        default=None, description="Optional due date for the task"
    )
    tags: list[str] = Field(
        default_factory=list, max_length=10, description="List of tags (max 10)"
    )
    is_recurring: bool = Field(
        default=False, description="Whether the task repeats"
    )
    recurrence_pattern: RecurrencePatternType | None = Field(
        default=None, description="Recurrence pattern (if recurring)"
    )


class UpdateTaskRequest(BaseModel):
    """Update task request."""

    title: str | None = Field(
        default=None, min_length=1, max_length=200, description="Task title"
    )
    description: str | None = Field(
        default=None, max_length=1000, description="Task description"
    )
    priority: TaskPriorityType | None = Field(
        default=None, description="Task priority level"
    )
    due_date: datetime | None = Field(
        default=None, description="Due date for the task"
    )
    tags: list[str] | None = Field(
        default=None, max_length=10, description="List of tags"
    )
    is_recurring: bool | None = Field(
        default=None, description="Whether the task repeats"
    )
    recurrence_pattern: RecurrencePatternType | None = Field(
        default=None, description="Recurrence pattern"
    )


class CompleteTaskRequest(BaseModel):
    """Toggle task completion request."""

    completed: bool = Field(..., description="Set completion status")


class TaskResponse(BaseModel):
    """Task response model."""

    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Optional task description")
    status: Literal["pending", "completed"] = Field(
        ..., description="Task completion status"
    )
    priority: TaskPriorityType = Field("medium", description="Task priority level")
    due_date: datetime | None = Field(None, description="Task due date")
    tags: list[str] = Field(default_factory=list, description="Task tags")
    is_recurring: bool = Field(False, description="Whether the task repeats")
    recurrence_pattern: RecurrencePatternType | None = Field(
        None, description="Recurrence pattern"
    )
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    completed_at: datetime | None = Field(
        None, description="When task was marked complete"
    )


class TaskListResponse(BaseModel):
    """Task list response."""

    tasks: list[TaskResponse]


class SingleTaskResponse(BaseModel):
    """Single task response wrapper."""

    task: TaskResponse


class DeleteTaskResponse(BaseModel):
    """Delete task response."""

    deleted: bool = True
    task_id: str


# =============================================================================
# Error Response Models
# =============================================================================


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
