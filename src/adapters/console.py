"""
Console Adapter for Rich library UI.

Provides beautiful terminal output for the todo application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from src.models import Task


class ConsoleAdapter:
    """
    Adapter for console UI using Rich library.

    Provides methods for:
        - Displaying menus
        - Showing task lists
        - Getting user input
        - Displaying messages
    """

    def __init__(self) -> None:
        """Initialize the console adapter."""
        self._console = Console()

    def display_menu(self, title: str, options: list[tuple[str, str]]) -> None:
        """
        Display a menu with numbered options.

        Args:
            title: Menu title.
            options: List of (key, description) tuples.
        """
        self._console.print()
        self._console.print(Panel(title, style="bold blue"))
        self._console.print()

        for key, description in options:
            self._console.print(f"  [{key}] {description}")

        self._console.print()

    def get_choice(self, prompt: str = "Choose an option") -> str:
        """
        Get user's menu choice.

        Args:
            prompt: Prompt text.

        Returns:
            User's input (stripped).
        """
        return Prompt.ask(f"[bold cyan]{prompt}[/]").strip()

    def get_text(
        self,
        prompt: str,
        default: str = "",
        required: bool = True,
    ) -> str:
        """
        Get text input from user.

        Args:
            prompt: Prompt text.
            default: Default value.
            required: Whether input is required.

        Returns:
            User's input.
        """
        while True:
            value = Prompt.ask(
                f"[bold]{prompt}[/]",
                default=default if default else None,
            )
            if value or not required:
                return value
            self.display_error("This field is required")

    def confirm(self, prompt: str, default: bool = False) -> bool:
        """
        Get yes/no confirmation from user.

        Args:
            prompt: Confirmation prompt.
            default: Default answer.

        Returns:
            True if confirmed, False otherwise.
        """
        return Confirm.ask(f"[bold]{prompt}[/]", default=default)

    def display_tasks(self, tasks: list[Task], title: str = "Tasks") -> None:
        """
        Display a table of tasks.

        Args:
            tasks: List of tasks to display.
            title: Table title.
        """
        if not tasks:
            self._console.print()
            self._console.print("[dim]No tasks found[/]")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("ID", style="dim", width=8)
        table.add_column("Title", style="bold")
        table.add_column("Description", style="dim")
        table.add_column("Status", justify="center")
        table.add_column("Created", style="dim")

        for idx, task in enumerate(tasks, 1):
            status_style = "green" if task.status == "completed" else "yellow"
            status_icon = "✓" if task.status == "completed" else "○"
            status_text = Text(f"{status_icon} {task.status}", style=status_style)

            created_str = task.created_at.strftime("%Y-%m-%d %H:%M")

            table.add_row(
                str(idx),
                task.id[:8],
                task.title,
                task.description or "-",
                status_text,
                created_str,
            )

        self._console.print()
        self._console.print(table)
        self._console.print()

    def display_task(self, task: Task) -> None:
        """
        Display a single task in detail.

        Args:
            task: Task to display.
        """
        status_style = "green" if task.status == "completed" else "yellow"
        status_icon = "✓" if task.status == "completed" else "○"

        content = f"""
[bold]Title:[/] {task.title}
[bold]Description:[/] {task.description or "No description"}
[bold]Status:[/] [{status_style}]{status_icon} {task.status}[/]
[bold]ID:[/] {task.id}
[bold]Created:[/] {task.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
[bold]Updated:[/] {task.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
"""
        if task.completed_at:
            content += (
                f"[bold]Completed:[/] {task.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            )

        self._console.print(Panel(content.strip(), title="Task Details"))

    def display_success(self, message: str) -> None:
        """
        Display a success message.

        Args:
            message: Success message.
        """
        self._console.print()
        self._console.print(f"[bold green]✓[/] {message}")

    def display_error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message: Error message.
        """
        self._console.print()
        self._console.print(f"[bold red]✗[/] {message}")

    def display_info(self, message: str) -> None:
        """
        Display an info message.

        Args:
            message: Info message.
        """
        self._console.print()
        self._console.print(f"[bold blue]ℹ[/] {message}")

    def display_warning(self, message: str) -> None:
        """
        Display a warning message.

        Args:
            message: Warning message.
        """
        self._console.print()
        self._console.print(f"[bold yellow]⚠[/] {message}")

    def clear(self) -> None:
        """Clear the console screen."""
        self._console.clear()

    def display_welcome(self, app_name: str, version: str) -> None:
        """
        Display welcome banner.

        Args:
            app_name: Application name.
            version: Application version.
        """
        banner = f"""
╔════════════════════════════════════════╗
║     {app_name:^32} ║
║         Version {version:^18}   ║
╚════════════════════════════════════════╝
"""
        self._console.print(Text(banner, style="bold blue"))

    def display_goodbye(self) -> None:
        """Display goodbye message."""
        self._console.print()
        self._console.print("[bold blue]Goodbye! 👋[/]")
        self._console.print()
