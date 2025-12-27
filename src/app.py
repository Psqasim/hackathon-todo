"""
Main application entry point.

Runs the interactive console todo application.
"""

from __future__ import annotations

import asyncio
import sys

import structlog

from src import __version__
from src.agents import create_orchestrator
from src.backends import InMemoryBackend
from src.models import AgentMessage

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class TodoApp:
    """
    Main todo application class.

    Coordinates the orchestrator and handles the main application loop.
    """

    def __init__(self) -> None:
        """Initialize the application."""
        self._orchestrator = None
        self._running = False

    async def _send_message(
        self,
        action: str,
        payload: dict | None = None,
    ) -> dict | None:
        """
        Send a message through the orchestrator.

        Args:
            action: Action to perform.
            payload: Optional payload data.

        Returns:
            Result data if successful, None if error.
        """
        message = AgentMessage(
            sender="app",
            recipient="orchestrator",
            action=action,
            payload=payload or {},
        )
        response = await self._orchestrator.handle_message(message)

        if response.status == "error":
            await self._send_message(
                "ui_display_message",
                {"message": response.error, "type": "error"},
            )
            return None

        return response.result

    async def _handle_add_task(self) -> None:
        """Handle the add task workflow."""
        # Get task details from user
        result = await self._send_message("ui_get_task_details")
        if result is None:
            return

        title = result.get("title")
        description = result.get("description")

        if not title:
            await self._send_message(
                "ui_display_message",
                {"message": "Task title is required", "type": "error"},
            )
            return

        # Add the task
        result = await self._send_message(
            "task_add",
            {"title": title, "description": description},
        )

        if result:
            await self._send_message(
                "ui_display_message",
                {"message": "Task added successfully!", "type": "success"},
            )

    async def _handle_list_tasks(self) -> None:
        """Handle the list tasks workflow."""
        result = await self._send_message("task_list")
        if result is None:
            return

        tasks = result.get("tasks", [])
        await self._send_message(
            "ui_display_tasks",
            {"tasks": tasks, "title": "All Tasks"},
        )

    async def _handle_complete_task(self) -> None:
        """Handle the complete task workflow."""
        # Get all pending tasks
        result = await self._send_message("task_list", {"status": "pending"})
        if result is None:
            return

        tasks = result.get("tasks", [])
        if not tasks:
            await self._send_message(
                "ui_display_message",
                {"message": "No pending tasks to complete", "type": "info"},
            )
            return

        # Let user select a task
        result = await self._send_message(
            "ui_select_task",
            {"tasks": tasks, "prompt": "Select task to complete"},
        )
        if result is None:
            return

        task_id = result.get("task_id")
        if not task_id:
            return

        # Confirm completion
        result = await self._send_message(
            "ui_confirm",
            {"prompt": "Mark this task as complete?", "default": True},
        )
        if result is None or not result.get("confirmed"):
            await self._send_message(
                "ui_display_message",
                {"message": "Cancelled", "type": "info"},
            )
            return

        # Complete the task
        result = await self._send_message("task_complete", {"task_id": task_id})
        if result:
            await self._send_message(
                "ui_display_message",
                {"message": "Task completed!", "type": "success"},
            )

    async def _handle_delete_task(self) -> None:
        """Handle the delete task workflow."""
        # Get all tasks
        result = await self._send_message("task_list")
        if result is None:
            return

        tasks = result.get("tasks", [])
        if not tasks:
            await self._send_message(
                "ui_display_message",
                {"message": "No tasks to delete", "type": "info"},
            )
            return

        # Let user select a task
        result = await self._send_message(
            "ui_select_task",
            {"tasks": tasks, "prompt": "Select task to delete"},
        )
        if result is None:
            return

        task_id = result.get("task_id")
        if not task_id:
            return

        # Confirm deletion
        result = await self._send_message(
            "ui_confirm",
            {"prompt": "Are you sure you want to delete this task?", "default": False},
        )
        if result is None or not result.get("confirmed"):
            await self._send_message(
                "ui_display_message",
                {"message": "Cancelled", "type": "info"},
            )
            return

        # Delete the task
        result = await self._send_message("task_delete", {"task_id": task_id})
        if result:
            await self._send_message(
                "ui_display_message",
                {"message": "Task deleted!", "type": "success"},
            )

    async def _handle_update_task(self) -> None:
        """Handle the update task workflow."""
        # Get all tasks
        result = await self._send_message("task_list")
        if result is None:
            return

        tasks = result.get("tasks", [])
        if not tasks:
            await self._send_message(
                "ui_display_message",
                {"message": "No tasks to update", "type": "info"},
            )
            return

        # Let user select a task
        result = await self._send_message(
            "ui_select_task",
            {"tasks": tasks, "prompt": "Select task to update"},
        )
        if result is None:
            return

        task_id = result.get("task_id")
        if not task_id:
            return

        # Get current task details
        result = await self._send_message("task_get", {"task_id": task_id})
        if result is None:
            return

        current_task = result.get("task", {})
        current_title = current_task.get("title", "")
        current_description = current_task.get("description", "")

        # Get new values from user
        result = await self._send_message(
            "ui_get_update_details",
            {
                "current_title": current_title,
                "current_description": current_description,
            },
        )
        if result is None:
            return

        new_title = result.get("title")
        new_description = result.get("description")

        # Check if anything changed
        if new_title is None and new_description is None:
            await self._send_message(
                "ui_display_message",
                {"message": "No changes made", "type": "info"},
            )
            return

        # Update the task
        update_payload = {"task_id": task_id}
        if new_title:
            update_payload["title"] = new_title
        if new_description:
            update_payload["description"] = new_description

        result = await self._send_message("task_update", update_payload)
        if result:
            await self._send_message(
                "ui_display_message",
                {"message": "Task updated successfully!", "type": "success"},
            )

    async def _handle_view_task(self) -> None:
        """Handle the view task workflow."""
        # Get all tasks
        result = await self._send_message("task_list")
        if result is None:
            return

        tasks = result.get("tasks", [])
        if not tasks:
            await self._send_message(
                "ui_display_message",
                {"message": "No tasks to view", "type": "info"},
            )
            return

        # Let user select a task
        result = await self._send_message(
            "ui_select_task",
            {"tasks": tasks, "prompt": "Select task to view"},
        )
        if result is None:
            return

        task_id = result.get("task_id")
        if not task_id:
            return

        # Get task details
        result = await self._send_message("task_get", {"task_id": task_id})
        if result:
            await self._send_message("ui_display_task", {"task": result.get("task")})

    async def run(self) -> None:
        """Run the main application loop."""
        # Create and start orchestrator
        backend = InMemoryBackend()
        self._orchestrator = await create_orchestrator(backend)
        await self._orchestrator.start()

        self._running = True

        # Show welcome
        await self._send_message(
            "ui_welcome",
            {"app_name": "Todo App", "version": __version__},
        )

        # Main loop
        while self._running:
            # Show menu
            await self._send_message("ui_display_menu", {"title": "Todo App Menu"})

            # Get choice
            result = await self._send_message("ui_get_choice")
            if result is None:
                continue

            choice = result.get("choice", "").lower()

            # Handle choice
            if choice == "1":
                await self._handle_add_task()
            elif choice == "2":
                await self._handle_list_tasks()
            elif choice == "3":
                await self._handle_update_task()
            elif choice == "4":
                await self._handle_complete_task()
            elif choice == "5":
                await self._handle_delete_task()
            elif choice == "6":
                await self._handle_view_task()
            elif choice == "q":
                # Confirm quit
                result = await self._send_message(
                    "ui_confirm",
                    {"prompt": "Are you sure you want to quit?", "default": True},
                )
                if result and result.get("confirmed"):
                    self._running = False
            else:
                await self._send_message(
                    "ui_display_message",
                    {"message": f"Unknown option: {choice}", "type": "warning"},
                )

        # Show goodbye
        await self._send_message("ui_goodbye")

        # Stop orchestrator
        await self._orchestrator.stop()


def main() -> int:
    """Main entry point."""
    try:
        app = TodoApp()
        asyncio.run(app.run())
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 130
    except Exception as e:
        logger.error("fatal_error", error=str(e))
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
