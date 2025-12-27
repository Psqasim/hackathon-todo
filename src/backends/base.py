"""
Storage Backend Protocol.

Defines the interface for all storage implementations.
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
    """

    async def save(self, task: Task) -> Task:
        """
        Save a task to storage.

        Args:
            task: The task to save.

        Returns:
            The saved task (may have updated fields like ID).

        Raises:
            StorageError: If the save operation fails.
        """
        ...

    async def get(self, task_id: str) -> Task | None:
        """
        Retrieve a task by ID.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The task if found, None otherwise.

        Raises:
            StorageError: If the get operation fails.
        """
        ...

    async def get_all(self) -> list[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks in storage.

        Raises:
            StorageError: If the get operation fails.
        """
        ...

    async def update(self, task: Task) -> Task:
        """
        Update an existing task.

        Args:
            task: The task with updated fields.

        Returns:
            The updated task.

        Raises:
            NotFoundError: If the task doesn't exist.
            StorageError: If the update operation fails.
        """
        ...

    async def delete(self, task_id: str) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete.

        Returns:
            True if the task was deleted, False if not found.

        Raises:
            StorageError: If the delete operation fails.
        """
        ...

    async def query(
        self,
        status: str | None = None,
    ) -> list[Task]:
        """
        Query tasks with optional filters.

        Args:
            status: Optional filter by status ('pending' or 'completed').

        Returns:
            List of tasks matching the filter criteria.

        Raises:
            StorageError: If the query operation fails.
        """
        ...

    async def clear(self) -> int:
        """
        Delete all tasks from storage.

        Returns:
            The number of tasks deleted.

        Raises:
            StorageError: If the clear operation fails.
        """
        ...
