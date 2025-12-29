"""
Storage Backend Protocol.

Defines the interface for all storage implementations.
Phase II: Added optional user_id parameter for multi-user support.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.models import Task


@runtime_checkable
class StorageBackend(Protocol):
    """
    Protocol defining the storage backend interface.

    All storage implementations must provide these methods.
    This allows for pluggable storage (in-memory, SQLite, PostgreSQL, etc.).

    Phase II: Methods accept optional user_id for multi-user filtering.
    In-memory backend ignores user_id (backward compatible).
    PostgreSQL backend uses user_id for task isolation.
    """

    async def save(self, task: Task, user_id: str | None = None) -> Task:
        """
        Save a task to storage.

        Args:
            task: The task to save.
            user_id: Optional owner user ID (required for PostgreSQL).

        Returns:
            The saved task (may have updated fields like ID).

        Raises:
            StorageError: If the save operation fails.
        """
        ...

    async def get(self, task_id: str, user_id: str | None = None) -> Task | None:
        """
        Retrieve a task by ID.

        Args:
            task_id: The unique identifier of the task.
            user_id: Optional user ID for ownership verification.

        Returns:
            The task if found, None otherwise.

        Raises:
            StorageError: If the get operation fails.
        """
        ...

    async def get_all(self, user_id: str | None = None) -> list[Task]:
        """
        Retrieve all tasks.

        Args:
            user_id: Optional user ID to filter tasks.

        Returns:
            List of all tasks in storage (for user if specified).

        Raises:
            StorageError: If the get operation fails.
        """
        ...

    async def update(self, task: Task, user_id: str | None = None) -> Task:
        """
        Update an existing task.

        Args:
            task: The task with updated fields.
            user_id: Optional user ID for ownership verification.

        Returns:
            The updated task.

        Raises:
            NotFoundError: If the task doesn't exist.
            StorageError: If the update operation fails.
        """
        ...

    async def delete(self, task_id: str, user_id: str | None = None) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete.
            user_id: Optional user ID for ownership verification.

        Returns:
            True if the task was deleted, False if not found.

        Raises:
            StorageError: If the delete operation fails.
        """
        ...

    async def query(
        self,
        status: str | None = None,
        user_id: str | None = None,
    ) -> list[Task]:
        """
        Query tasks with optional filters.

        Args:
            status: Optional filter by status ('pending' or 'completed').
            user_id: Optional filter by user ID.

        Returns:
            List of tasks matching the filter criteria.

        Raises:
            StorageError: If the query operation fails.
        """
        ...

    async def clear(self, user_id: str | None = None) -> int:
        """
        Delete all tasks from storage.

        Args:
            user_id: Optional user ID to clear only that user's tasks.

        Returns:
            The number of tasks deleted.

        Raises:
            StorageError: If the clear operation fails.
        """
        ...
