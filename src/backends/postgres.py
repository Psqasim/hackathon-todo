"""
PostgreSQL Storage Backend.

SQLModel-based storage for Phase II production deployment.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog
from sqlmodel import Session, select

from src.models import NotFoundError, StorageError
from src.models.tasks import Task, TaskDB, db_to_task, task_to_db

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

logger = structlog.get_logger()


class PostgresBackend:
    """
    PostgreSQL storage backend using SQLModel.

    Implements the StorageBackend protocol with user-scoped operations.
    Phase II: Supports multi-user task isolation via user_id filtering.
    """

    def __init__(self, engine: Engine) -> None:
        """
        Initialize PostgreSQL backend.

        Args:
            engine: SQLAlchemy engine for database connections.
        """
        self._engine = engine
        self._log = logger.bind(backend="postgres")

    async def save(self, task: Task, user_id: str | None = None) -> Task:
        """
        Save a task to PostgreSQL.

        Args:
            task: The task to save.
            user_id: Owner user ID (required for new tasks).

        Returns:
            The saved task.

        Raises:
            StorageError: If the save operation fails.
        """
        if user_id is None:
            raise StorageError(
                "user_id is required for PostgreSQL backend",
                operation="save",
            )

        try:
            with Session(self._engine) as session:
                db_task = task_to_db(task, user_id)
                session.add(db_task)
                session.commit()
                session.refresh(db_task)
                self._log.debug("task_saved", task_id=task.id, user_id=user_id)
                return db_to_task(db_task)
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
            user_id: Optional user ID for ownership verification.

        Returns:
            The task if found, None otherwise.
        """
        try:
            with Session(self._engine) as session:
                statement = select(TaskDB).where(TaskDB.id == task_id)
                if user_id is not None:
                    statement = statement.where(TaskDB.user_id == user_id)
                
                db_task = session.exec(statement).first()
                
                if db_task:
                    self._log.debug("task_retrieved", task_id=task_id)
                    return db_to_task(db_task)
                
                self._log.debug("task_not_found", task_id=task_id)
                return None
        except Exception as e:
            self._log.error("get_failed", task_id=task_id, error=str(e))
            raise StorageError(
                f"Failed to get task: {e}",
                operation="get",
            ) from e

    async def get_all(self, user_id: str | None = None) -> list[Task]:
        """
        Retrieve all tasks, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter tasks.

        Returns:
            List of all tasks (for user if specified).
        """
        try:
            with Session(self._engine) as session:
                statement = select(TaskDB)
                if user_id is not None:
                    statement = statement.where(TaskDB.user_id == user_id)
                
                db_tasks = session.exec(statement).all()
                tasks = [db_to_task(t) for t in db_tasks]
                self._log.debug("tasks_retrieved", count=len(tasks), user_id=user_id)
                return tasks
        except Exception as e:
            self._log.error("get_all_failed", error=str(e))
            raise StorageError(
                f"Failed to get all tasks: {e}",
                operation="get_all",
            ) from e

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
        """
        try:
            with Session(self._engine) as session:
                statement = select(TaskDB).where(TaskDB.id == task.id)
                if user_id is not None:
                    statement = statement.where(TaskDB.user_id == user_id)
                
                db_task = session.exec(statement).first()
                
                if db_task is None:
                    self._log.warning("update_not_found", task_id=task.id)
                    raise NotFoundError(
                        f"Task not found: {task.id}",
                        resource_type="task",
                        resource_id=task.id,
                    )
                
                # Update fields
                db_task.title = task.title
                db_task.description = task.description
                db_task.status = task.status
                db_task.updated_at = task.updated_at
                db_task.completed_at = task.completed_at
                
                session.add(db_task)
                session.commit()
                session.refresh(db_task)
                
                self._log.debug("task_updated", task_id=task.id)
                return db_to_task(db_task)
        except NotFoundError:
            raise
        except Exception as e:
            self._log.error("update_failed", task_id=task.id, error=str(e))
            raise StorageError(
                f"Failed to update task: {e}",
                operation="update",
            ) from e

    async def delete(self, task_id: str, user_id: str | None = None) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete.
            user_id: Optional user ID for ownership verification.

        Returns:
            True if the task was deleted, False if not found.
        """
        try:
            with Session(self._engine) as session:
                statement = select(TaskDB).where(TaskDB.id == task_id)
                if user_id is not None:
                    statement = statement.where(TaskDB.user_id == user_id)
                
                db_task = session.exec(statement).first()
                
                if db_task is None:
                    self._log.debug("delete_not_found", task_id=task_id)
                    return False
                
                session.delete(db_task)
                session.commit()
                
                self._log.debug("task_deleted", task_id=task_id)
                return True
        except Exception as e:
            self._log.error("delete_failed", task_id=task_id, error=str(e))
            raise StorageError(
                f"Failed to delete task: {e}",
                operation="delete",
            ) from e

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
        """
        try:
            with Session(self._engine) as session:
                statement = select(TaskDB)
                
                if user_id is not None:
                    statement = statement.where(TaskDB.user_id == user_id)
                
                if status is not None:
                    statement = statement.where(TaskDB.status == status)
                
                db_tasks = session.exec(statement).all()
                tasks = [db_to_task(t) for t in db_tasks]
                
                self._log.debug(
                    "tasks_queried",
                    status_filter=status,
                    user_id=user_id,
                    count=len(tasks),
                )
                return tasks
        except Exception as e:
            self._log.error("query_failed", error=str(e))
            raise StorageError(
                f"Failed to query tasks: {e}",
                operation="query",
            ) from e

    async def clear(self, user_id: str | None = None) -> int:
        """
        Delete all tasks from storage.

        Args:
            user_id: Optional user ID to clear only that user's tasks.

        Returns:
            The number of tasks deleted.
        """
        try:
            with Session(self._engine) as session:
                statement = select(TaskDB)
                if user_id is not None:
                    statement = statement.where(TaskDB.user_id == user_id)
                
                db_tasks = session.exec(statement).all()
                count = len(db_tasks)
                
                for db_task in db_tasks:
                    session.delete(db_task)
                
                session.commit()
                self._log.info("storage_cleared", count=count, user_id=user_id)
                return count
        except Exception as e:
            self._log.error("clear_failed", error=str(e))
            raise StorageError(
                f"Failed to clear storage: {e}",
                operation="clear",
            ) from e
