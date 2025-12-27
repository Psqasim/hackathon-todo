"""
UI Controller Agent.

Handles user interface operations for the console app.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.base import BaseAgent
from src.models import AgentMessage, AgentResponse, Task

if TYPE_CHECKING:
    from src.adapters.console import ConsoleAdapter


class UIControllerAgent(BaseAgent):
    """
    Agent responsible for user interface operations.

    Handles actions:
        - ui_display_menu: Show the main menu
        - ui_get_choice: Get user menu choice
        - ui_get_task_details: Get task title and description
        - ui_display_tasks: Show task list
        - ui_display_task: Show single task details
        - ui_display_message: Show success/error/info message
        - ui_confirm: Get yes/no confirmation
        - ui_select_task: Select a task from a list
        - ui_welcome: Show welcome banner
        - ui_goodbye: Show goodbye message
    """

    MAIN_MENU_OPTIONS = [
        ("1", "Add Task"),
        ("2", "View All Tasks"),
        ("3", "Update Task"),
        ("4", "Mark Task Complete"),
        ("5", "Delete Task"),
        ("6", "View Task Details"),
        ("q", "Quit"),
    ]

    def __init__(
        self,
        adapter: ConsoleAdapter,
        name: str = "ui_controller",
        version: str = "1.0.0",
    ) -> None:
        """
        Initialize the UI controller agent.

        Args:
            adapter: Console adapter for UI operations.
            name: Agent name.
            version: Agent version.
        """
        super().__init__(name, version)
        self._adapter = adapter

        # Register action handlers
        self.register_action("ui_display_menu", self._handle_display_menu)
        self.register_action("ui_get_choice", self._handle_get_choice)
        self.register_action("ui_get_task_details", self._handle_get_task_details)
        self.register_action("ui_get_update_details", self._handle_get_update_details)
        self.register_action("ui_display_tasks", self._handle_display_tasks)
        self.register_action("ui_display_task", self._handle_display_task)
        self.register_action("ui_display_message", self._handle_display_message)
        self.register_action("ui_confirm", self._handle_confirm)
        self.register_action("ui_select_task", self._handle_select_task)
        self.register_action("ui_welcome", self._handle_welcome)
        self.register_action("ui_goodbye", self._handle_goodbye)

    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Handle incoming UI operation messages.

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
                f"Unknown UI action: {message.action}",
            )

        try:
            return await handler(message)
        except Exception as e:
            self._log.error("unexpected_error", error=str(e))
            return self._create_error_response(
                message.request_id,
                f"UI error: {e}",
            )

    async def _handle_display_menu(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_display_menu action."""
        title = message.payload.get("title", "Todo App Menu")
        options = message.payload.get("options", self.MAIN_MENU_OPTIONS)

        self._adapter.display_menu(title, options)

        return self._create_success_response(message.request_id)

    async def _handle_get_choice(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_get_choice action."""
        prompt = message.payload.get("prompt", "Choose an option")

        choice = self._adapter.get_choice(prompt)

        return self._create_success_response(
            message.request_id,
            {"choice": choice},
        )

    async def _handle_get_task_details(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_get_task_details action."""
        title = self._adapter.get_text("Task title", required=True)
        description = self._adapter.get_text(
            "Description (optional)",
            required=False,
        )

        return self._create_success_response(
            message.request_id,
            {
                "title": title,
                "description": description if description else None,
            },
        )

    async def _handle_get_update_details(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_get_update_details action."""
        current_title = message.payload.get("current_title", "")
        current_description = message.payload.get("current_description", "")

        # Show current values
        self._adapter._console.print()
        self._adapter._console.print(f"[dim]Current title:[/] {current_title}")
        self._adapter._console.print(
            f"[dim]Current description:[/] {current_description or 'No description'}"
        )
        self._adapter._console.print()
        self._adapter._console.print("[dim]Press Enter to keep current value[/]")

        # Get new values (with defaults)
        new_title = self._adapter.get_text(
            "New title",
            default=current_title,
            required=False,
        )
        new_description = self._adapter.get_text(
            "New description",
            default=current_description or "",
            required=False,
        )

        return self._create_success_response(
            message.request_id,
            {
                "title": new_title if new_title else None,
                "description": new_description if new_description else None,
            },
        )

    async def _handle_display_tasks(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_display_tasks action."""
        tasks_data = message.payload.get("tasks", [])
        title = message.payload.get("title", "Tasks")

        # Convert dicts to Task objects if needed
        tasks = []
        for t in tasks_data:
            if isinstance(t, dict):
                tasks.append(Task(**t))
            elif isinstance(t, Task):
                tasks.append(t)

        self._adapter.display_tasks(tasks, title)

        return self._create_success_response(
            message.request_id,
            {"displayed": len(tasks)},
        )

    async def _handle_display_task(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_display_task action."""
        task_data = message.payload.get("task")
        if not task_data:
            return self._create_error_response(
                message.request_id,
                "Missing 'task' in payload",
            )

        # Convert dict to Task if needed
        task = Task(**task_data) if isinstance(task_data, dict) else task_data

        self._adapter.display_task(task)

        return self._create_success_response(message.request_id)

    async def _handle_display_message(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_display_message action."""
        text = message.payload.get("message", "")
        msg_type = message.payload.get("type", "info")

        if msg_type == "success":
            self._adapter.display_success(text)
        elif msg_type == "error":
            self._adapter.display_error(text)
        elif msg_type == "warning":
            self._adapter.display_warning(text)
        else:
            self._adapter.display_info(text)

        return self._create_success_response(message.request_id)

    async def _handle_confirm(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_confirm action."""
        prompt = message.payload.get("prompt", "Are you sure?")
        default = message.payload.get("default", False)

        confirmed = self._adapter.confirm(prompt, default)

        return self._create_success_response(
            message.request_id,
            {"confirmed": confirmed},
        )

    async def _handle_select_task(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_select_task action."""
        tasks_data = message.payload.get("tasks", [])
        prompt = message.payload.get("prompt", "Select task number")

        if not tasks_data:
            return self._create_error_response(
                message.request_id,
                "No tasks available to select",
            )

        # Convert and display tasks
        tasks = []
        for t in tasks_data:
            if isinstance(t, dict):
                tasks.append(Task(**t))
            elif isinstance(t, Task):
                tasks.append(t)

        self._adapter.display_tasks(tasks, "Select a Task")

        # Get selection
        choice = self._adapter.get_text(prompt, required=True)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tasks):
                selected = tasks[idx]
                return self._create_success_response(
                    message.request_id,
                    {"task_id": selected.id, "index": idx},
                )
            else:
                return self._create_error_response(
                    message.request_id,
                    f"Invalid selection: {choice}",
                )
        except ValueError:
            return self._create_error_response(
                message.request_id,
                f"Invalid number: {choice}",
            )

    async def _handle_welcome(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_welcome action."""
        app_name = message.payload.get("app_name", "Todo App")
        version = message.payload.get("version", "1.0.0")

        self._adapter.display_welcome(app_name, version)

        return self._create_success_response(message.request_id)

    async def _handle_goodbye(self, message: AgentMessage) -> AgentResponse:
        """Handle ui_goodbye action."""
        self._adapter.display_goodbye()

        return self._create_success_response(message.request_id)
