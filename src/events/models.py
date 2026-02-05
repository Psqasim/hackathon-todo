"""Event models for TaskFlow event-driven architecture."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskEvent(BaseModel):
    """Event published when a task is created, updated, completed, or deleted.

    This event is published to the 'task-events' Kafka topic via Dapr pub/sub.
    Used for event-driven workflows like recurring task automation.
    """

    event_type: str = Field(
        ...,
        description="Type of event: created, updated, completed, deleted",
    )
    task_id: int = Field(..., description="ID of the task that triggered this event")
    user_id: str = Field(..., description="ID of the user who owns this task")
    task_data: dict[str, Any] = Field(
        ...,
        description="Complete task data snapshot at time of event",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when event was created",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "created",
                "task_id": 123,
                "user_id": "user_abc123",
                "task_data": {
                    "id": 123,
                    "title": "Review PR",
                    "is_recurring": True,
                    "recurrence": "weekly",
                    "due_date": "2026-02-12T10:00:00Z",
                },
                "timestamp": "2026-02-05T12:00:00Z",
            }
        }
    )


class ReminderEvent(BaseModel):
    """Event published when a task reminder should be sent.

    This event is published to the 'reminders' Kafka topic via Dapr pub/sub.
    Consumed by the notification service to deliver reminders to users.
    """

    task_id: int = Field(..., description="ID of the task this reminder is for")
    user_id: str = Field(..., description="ID of the user to remind")
    title: str = Field(..., description="Task title to display in reminder")
    due_at: datetime = Field(..., description="When the task is actually due")
    remind_at: datetime = Field(
        ...,
        description="When to deliver this reminder (typically 1 hour before due_at)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when reminder event was created",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": 123,
                "user_id": "user_abc123",
                "title": "Review PR",
                "due_at": "2026-02-05T10:00:00Z",
                "remind_at": "2026-02-05T09:00:00Z",
                "timestamp": "2026-02-05T08:00:00Z",
            }
        }
    )
