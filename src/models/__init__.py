"""
Models package for the Multi-Agent Todo Application.

Contains Pydantic models for messages, tasks, and exceptions.
Phase II: Added User, TaskDB, and API request/response models.
"""

from src.models.exceptions import (
    AgentError,
    AgentInitError,
    NotFoundError,
    RoutingError,
    StorageError,
    ValidationError,
)
from src.models.messages import AgentInfo, AgentMessage, AgentResponse
from src.models.tasks import Task, TaskDB, db_to_task, task_to_db
from src.models.user import User, UserCreate, UserDB, UserLogin

__all__ = [
    # Messages
    "AgentMessage",
    "AgentResponse",
    "AgentInfo",
    # Tasks
    "Task",
    "TaskDB",
    "task_to_db",
    "db_to_task",
    # Users
    "User",
    "UserDB",
    "UserCreate",
    "UserLogin",
    # Exceptions
    "AgentError",
    "ValidationError",
    "NotFoundError",
    "StorageError",
    "RoutingError",
    "AgentInitError",
]
