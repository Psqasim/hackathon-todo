"""
Storage Handler Agent.

Handles all storage operations for tasks.

Phase II: Added optional user_id support for multi-user task isolation.
When user_id is provided in payload, it's passed to backend methods.
When user_id is None (console app), backward compatibility is maintained.
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

        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        saved = await self._backend.save(task, user_id=user_id)
        self._log.info("task_saved", task_id=saved.id, user_id=user_id)

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

        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        task = await self._backend.get(task_id, user_id=user_id)
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
        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        tasks = await self._backend.get_all(user_id=user_id)

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

        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        updated = await self._backend.update(task, user_id=user_id)
        self._log.info("task_updated", task_id=updated.id, user_id=user_id)

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

        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        deleted = await self._backend.delete(task_id, user_id=user_id)
        self._log.info("task_deleted", task_id=task_id, user_id=user_id, success=deleted)

        return self._create_success_response(
            message.request_id,
            {"deleted": deleted, "task_id": task_id},
        )

    async def _handle_query(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_query action."""
        status = message.payload.get("status")

        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        tasks = await self._backend.query(status=status, user_id=user_id)

        return self._create_success_response(
            message.request_id,
            {"tasks": [t.model_dump() for t in tasks], "count": len(tasks)},
        )

    async def _handle_clear(self, message: AgentMessage) -> AgentResponse:
        """Handle storage_clear action."""
        # Phase II: Extract optional user_id for multi-user support
        user_id = message.payload.get("user_id")

        count = await self._backend.clear(user_id=user_id)
        self._log.info("storage_cleared", user_id=user_id, count=count)

        return self._create_success_response(
            message.request_id,
            {"cleared": count},
        )
