"""
Storage Handler Agent.

Handles all storage operations for tasks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.base import BaseAgent
from src.models import (
    AgentMessage,
    AgentResponse,
    NotFoundError,
    StorageError,
    Task,
    ValidationError,
)

if TYPE_CHECKING:
    from src.backends.base import StorageBackend


class StorageHandlerAgent(BaseAgent):
    """
    Agent responsible for task persistence operations.

    Handles actions:
        - storage_save: Save a new task
        - storage_get: Get a task by ID
        - storage_get_all: Get all tasks
        - storage_update: Update an existing task
        - storage_delete: Delete a task
        - storage_query: Query tasks with filters
        - storage_clear: Clear all tasks
    """

    def __init__(
        self,
        backend: StorageBackend,
        name: str = "storage_handler",
        version: str = "1.0.0",
    ) -> None:
        """
        Initialize the storage handler agent.

        Args:
            backend: Storage backend implementation.
            name: Agent name.
            version: Agent version.
        """
        super().__init__(name, version)
        self._backend = backend

        # Register action handlers
        self.register_action("storage_save", self._handle_save)
        self.register_action("storage_get", self._handle_get)
        self.register_action("storage_get_all", self._handle_get_all)
        self.register_action("storage_update", self._handle_update)
        self.register_action("storage_delete", self._handle_delete)
        self.register_action("storage_query", self._handle_query)
        self.register_action("storage_clear", self._handle_clear)

    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Handle incoming storage operation messages.

        Args:
            message: The incoming message.

        Returns:
            AgentResponse with operation result or error.
        """
        self._log.info(
            "handling_message",
            action=message.action,
            request_id=message.request_id,
        )

        handler = self._actions.get(message.action)
        if handler is None:
            return self._create_error_response(
                message.request_id,
                f"Unknown storage action: {message.action}",
            )

        try:
            return await handler(message)
        except NotFoundError as e:
            return self._create_error_response(message.request_id, str(e))
        except StorageError as e:
            return self._create_error_response(message.request_id, str(e))
        except ValidationError as e:
            return self._create_error_response(message.request_id, str(e))
        except Exception as e:
            self._log.error("unexpected_error", error=str(e))
            return self._create_error_response(
                message.request_id,
                f"Internal error: {e}",
            )

    async def _handle_save(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_save action."""
        task_data = message.payload.get("task")
        if task_data is None:
            return self._create_error_response(
                message.request_id,
                "Missing 'task' in payload",
            )

        # Accept either Task object or dict
        if isinstance(task_data, dict):
            task = Task(**task_data)
        elif isinstance(task_data, Task):
            task = task_data
        else:
            return self._create_error_response(
                message.request_id,
                "Invalid task data type",
            )

        saved = await self._backend.save(task)
        self._log.info("task_saved", task_id=saved.id)

        return self._create_success_response(
            message.request_id,
            {"task": saved.model_dump()},
        )

    async def _handle_get(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_get action."""
        task_id = message.payload.get("task_id")
        if not task_id:
            return self._create_error_response(
                message.request_id,
                "Missing 'task_id' in payload",
            )

        task = await self._backend.get(task_id)
        if task is None:
            return self._create_error_response(
                message.request_id,
                f"Task not found: {task_id}",
            )

        return self._create_success_response(
            message.request_id,
            {"task": task.model_dump()},
        )

    async def _handle_get_all(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_get_all action."""
        tasks = await self._backend.get_all()

        return self._create_success_response(
            message.request_id,
            {"tasks": [t.model_dump() for t in tasks]},
        )

    async def _handle_update(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_update action."""
        task_data = message.payload.get("task")
        if task_data is None:
            return self._create_error_response(
                message.request_id,
                "Missing 'task' in payload",
            )

        # Accept either Task object or dict
        if isinstance(task_data, dict):
            task = Task(**task_data)
        elif isinstance(task_data, Task):
            task = task_data
        else:
            return self._create_error_response(
                message.request_id,
                "Invalid task data type",
            )

        updated = await self._backend.update(task)
        self._log.info("task_updated", task_id=updated.id)

        return self._create_success_response(
            message.request_id,
            {"task": updated.model_dump()},
        )

    async def _handle_delete(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_delete action."""
        task_id = message.payload.get("task_id")
        if not task_id:
            return self._create_error_response(
                message.request_id,
                "Missing 'task_id' in payload",
            )

        deleted = await self._backend.delete(task_id)
        self._log.info("task_deleted", task_id=task_id, success=deleted)

        return self._create_success_response(
            message.request_id,
            {"deleted": deleted, "task_id": task_id},
        )

    async def _handle_query(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_query action."""
        status = message.payload.get("status")

        tasks = await self._backend.query(status=status)

        return self._create_success_response(
            message.request_id,
            {"tasks": [t.model_dump() for t in tasks], "count": len(tasks)},
        )

    async def _handle_clear(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_clear action."""
        count = await self._backend.clear()
        self._log.info("storage_cleared", count=count)

        return self._create_success_response(
            message.request_id,
            {"cleared": count},
        )
