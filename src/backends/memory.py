"""
In-Memory Storage Backend.

Simple dictionary-based storage for Phase I development.
Phase II: Added user_id parameters (ignored for backward compatibility).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import structlog

from src.models import NotFoundError, StorageError

if TYPE_CHECKING:
    from src.models import Task

logger = structlog.get_logger()


class InMemoryBackend:
    """
    In-memory storage backend using a dictionary.

    Thread-safe implementation using asyncio locks.
    Data is lost when the application exits.

    Implements the StorageBackend protocol.

    Phase II: user_id parameters are accepted but ignored for backward compatibility.
    This allows the console app (Phase I) to continue working without changes.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._log = logger.bind(backend="in_memory")

    async def save(self, task: Task, user_id: str | None = None) -> Task:
        """
        Save a task to storage.

        Args:
            task: The task to save.

        Returns:
            The saved task.

        Raises:
            StorageError: If the save operation fails.
        """
        try:
            async with self._lock:
                self._tasks[task.id] = task
                self._log.debug("task_saved", task_id=task.id)
                return task
        except Exception as e:
            self._log.error("save_failed", task_id=task.id, error=str(e))
            raise StorageError(
                f"Failed to save task: {e}",
                operation="save",
            ) from e

    async def get(self, task_id: str, user_id: str | None = None) -> Task | None:
        """
        Retrieve a task by ID.

        Args:
            task_id: The unique identifier of the task.
            user_id: Optional user ID (ignored for backward compatibility).

        Returns:
            The task if found, None otherwise.
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                self._log.debug("task_retrieved", task_id=task_id)
            else:
                self._log.debug("task_not_found", task_id=task_id)
            return task

    async def get_all(self, user_id: str | None = None) -> list[Task]:
        """
        Retrieve all tasks.

        Args:
            user_id: Optional user ID (ignored for backward compatibility).

        Returns:
            List of all tasks in storage.
        """
        async with self._lock:
            tasks = list(self._tasks.values())
            self._log.debug("tasks_retrieved", count=len(tasks))
            return tasks

    async def update(self, task: Task, user_id: str | None = None) -> Task:
        """
        Update an existing task.

        Args:
            task: The task with updated fields.
            user_id: Optional user ID (ignored for backward compatibility).

        Returns:
            The updated task.

        Raises:
            NotFoundError: If the task doesn't exist.
        """
        async with self._lock:
            if task.id not in self._tasks:
                self._log.warning("update_not_found", task_id=task.id)
                raise NotFoundError(
                    f"Task not found: {task.id}",
                    resource_type="task",
                    resource_id=task.id,
                )
            self._tasks[task.id] = task
            self._log.debug("task_updated", task_id=task.id)
            return task

    async def delete(self, task_id: str, user_id: str | None = None) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete.
            user_id: Optional user ID (ignored for backward compatibility).

        Returns:
            True if the task was deleted, False if not found.
        """
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                self._log.debug("task_deleted", task_id=task_id)
                return True
            self._log.debug("delete_not_found", task_id=task_id)
            return False

    async def query(
        self,
        status: str | None = None,
        user_id: str | None = None,
    ) -> list[Task]:
        """
        Query tasks with optional filters.

        Args:
            status: Optional filter by status ('pending' or 'completed').
            user_id: Optional user ID (ignored for backward compatibility).

        Returns:
            List of tasks matching the filter criteria.
        """
        async with self._lock:
            tasks = list(self._tasks.values())

            if status is not None:
                tasks = [t for t in tasks if t.status == status]

            self._log.debug(
                "tasks_queried",
                status_filter=status,
                count=len(tasks),
            )
            return tasks

    async def clear(self, user_id: str | None = None) -> int:
        """
        Delete all tasks from storage.

        Args:
            user_id: Optional user ID (ignored for backward compatibility).

        Returns:
            The number of tasks deleted.
        """
        async with self._lock:
            count = len(self._tasks)
            self._tasks.clear()
            self._log.info("storage_cleared", count=count)
            return count

    @property
    def count(self) -> int:
        """Return the number of tasks in storage (synchronous)."""
        return len(self._tasks)
