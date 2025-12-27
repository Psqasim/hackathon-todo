"""
Task Manager Agent.

Handles business logic for task operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.agents.base import BaseAgent
from src.models import (
    AgentMessage,
    AgentResponse,
    NotFoundError,
    Task,
    ValidationError,
)

if TYPE_CHECKING:
    from src.agents.storage_handler import StorageHandlerAgent


class TaskManagerAgent(BaseAgent):
    """
    Agent responsible for task business logic.

    Handles actions:
        - task_add: Add a new task
        - task_list: List tasks with optional filters
        - task_complete: Mark a task as complete
        - task_delete: Delete a task
        - task_get: Get a task by ID
        - task_update: Update task details

    Delegates storage operations to StorageHandlerAgent.
    """

    def __init__(
        self,
        storage_agent: StorageHandlerAgent,
        name: str = "task_manager",
        version: str = "1.0.0",
    ) -> None:
        """
        Initialize the task manager agent.

        Args:
            storage_agent: Storage agent for persistence.
            name: Agent name.
            version: Agent version.
        """
        super().__init__(name, version)
        self._storage = storage_agent

        # Register action handlers
        self.register_action("task_add", self._handle_add)
        self.register_action("task_list", self._handle_list)
        self.register_action("task_complete", self._handle_complete)
        self.register_action("task_delete", self._handle_delete)
        self.register_action("task_get", self._handle_get)
        self.register_action("task_update", self._handle_update)

    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Handle incoming task operation messages.

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
                f"Unknown task action: {message.action}",
            )

        try:
            return await handler(message)
        except ValidationError as e:
            return self._create_error_response(message.request_id, str(e))
        except NotFoundError as e:
            return self._create_error_response(message.request_id, str(e))
        except Exception as e:
            self._log.error("unexpected_error", error=str(e))
            return self._create_error_response(
                message.request_id,
                f"Internal error: {e}",
            )

    async def _send_to_storage(
        self,
        action: str,
        payload: dict[str, Any],
        correlation_id: str,
    ) -> AgentResponse:
        """
        Send a message to the storage agent.

        Args:
            action: Storage action to perform.
            payload: Action payload.
            correlation_id: Correlation ID for tracing.

        Returns:
            Storage agent response.
        """
        message = AgentMessage(
            sender=self._name,
            recipient=self._storage.name,
            action=action,
            payload=payload,
            correlation_id=correlation_id,
        )
        return await self._storage.handle_message(message)

    async def _handle_add(self, message: AgentMessage) -> AgentResponse:
        """Handle task_add action."""
        title = message.payload.get("title")
        if not title:
            return self._create_error_response(
                message.request_id,
                "Missing 'title' in payload",
            )

        description = message.payload.get("description")

        # Create task
        task = Task(title=title, description=description)

        # Save to storage
        response = await self._send_to_storage(
            "storage_save",
            {"task": task.model_dump()},
            message.correlation_id,
        )

        if response.status == "error":
            return self._create_error_response(
                message.request_id,
                response.error or "Failed to save task",
            )

        self._log.info("task_added", task_id=task.id)
        return self._create_success_response(
            message.request_id,
            response.result,
        )

    async def _handle_list(self, message: AgentMessage) -> AgentResponse:
        """Handle task_list action."""
        status = message.payload.get("status")

        # Query storage
        response = await self._send_to_storage(
            "storage_query",
            {"status": status},
            message.correlation_id,
        )

        if response.status == "error":
            return self._create_error_response(
                message.request_id,
                response.error or "Failed to list tasks",
            )

        return self._create_success_response(
            message.request_id,
            response.result,
        )

    async def _handle_complete(self, message: AgentMessage) -> AgentResponse:
        """Handle task_complete action."""
        task_id = message.payload.get("task_id")
        if not task_id:
            return self._create_error_response(
                message.request_id,
                "Missing 'task_id' in payload",
            )

        # Get the task first
        get_response = await self._send_to_storage(
            "storage_get",
            {"task_id": task_id},
            message.correlation_id,
        )

        if get_response.status == "error":
            return self._create_error_response(
                message.request_id,
                get_response.error or f"Task not found: {task_id}",
            )

        # Mark as complete
        task_data = get_response.result["task"]
        task = Task(**task_data)
        completed_task = task.mark_complete()

        # Update in storage
        update_response = await self._send_to_storage(
            "storage_update",
            {"task": completed_task.model_dump()},
            message.correlation_id,
        )

        if update_response.status == "error":
            return self._create_error_response(
                message.request_id,
                update_response.error or "Failed to complete task",
            )

        self._log.info("task_completed", task_id=task_id)
        return self._create_success_response(
            message.request_id,
            update_response.result,
        )

    async def _handle_delete(self, message: AgentMessage) -> AgentResponse:
        """Handle task_delete action."""
        task_id = message.payload.get("task_id")
        if not task_id:
            return self._create_error_response(
                message.request_id,
                "Missing 'task_id' in payload",
            )

        # Delete from storage
        response = await self._send_to_storage(
            "storage_delete",
            {"task_id": task_id},
            message.correlation_id,
        )

        if response.status == "error":
            return self._create_error_response(
                message.request_id,
                response.error or "Failed to delete task",
            )

        deleted = response.result.get("deleted", False)
        if not deleted:
            return self._create_error_response(
                message.request_id,
                f"Task not found: {task_id}",
            )

        self._log.info("task_deleted", task_id=task_id)
        return self._create_success_response(
            message.request_id,
            {"deleted": True, "task_id": task_id},
        )

    async def _handle_get(self, message: AgentMessage) -> AgentResponse:
        """Handle task_get action."""
        task_id = message.payload.get("task_id")
        if not task_id:
            return self._create_error_response(
                message.request_id,
                "Missing 'task_id' in payload",
            )

        # Get from storage
        response = await self._send_to_storage(
            "storage_get",
            {"task_id": task_id},
            message.correlation_id,
        )

        if response.status == "error":
            return self._create_error_response(
                message.request_id,
                response.error or f"Task not found: {task_id}",
            )

        return self._create_success_response(
            message.request_id,
            response.result,
        )

    async def _handle_update(self, message: AgentMessage) -> AgentResponse:
        """Handle task_update action."""
        task_id = message.payload.get("task_id")
        if not task_id:
            return self._create_error_response(
                message.request_id,
                "Missing 'task_id' in payload",
            )

        title = message.payload.get("title")
        description = message.payload.get("description")

        if title is None and description is None:
            return self._create_error_response(
                message.request_id,
                "No update fields provided",
            )

        # Get the task first
        get_response = await self._send_to_storage(
            "storage_get",
            {"task_id": task_id},
            message.correlation_id,
        )

        if get_response.status == "error":
            return self._create_error_response(
                message.request_id,
                get_response.error or f"Task not found: {task_id}",
            )

        # Update fields
        task_data = get_response.result["task"]
        task = Task(**task_data)
        updated_task = task.update(title=title, description=description)

        # Save update
        update_response = await self._send_to_storage(
            "storage_update",
            {"task": updated_task.model_dump()},
            message.correlation_id,
        )

        if update_response.status == "error":
            return self._create_error_response(
                message.request_id,
                update_response.error or "Failed to update task",
            )

        self._log.info("task_updated", task_id=task_id)
        return self._create_success_response(
            message.request_id,
            update_response.result,
        )
