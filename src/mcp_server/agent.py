"""
OpenAI Agents SDK Task Management Agent.

This module provides a TRUE agentic system using the OpenAI Agents SDK:
- Uses Agent class with OpenAI Conversations API for memory
- Implements @function_tool for automatic tool execution
- Maintains conversation context via OpenAI's server-side storage
- NO chat history in PostgreSQL - uses SDK thread memory ONLY

Architecture:
- PostgreSQL stores ONLY: Users, Tasks
- Chat history stored in OpenAI Conversations API (OpenAIConversationsSession)
- Backend remains stateless
- conversation_id = OpenAI conversation ID for continuity

FR-011: Agent uses OpenAI model
FR-012: Agent implements function calling for all task operations
FR-014: Agent maintains conversation context via SDK sessions
FR-018: Agent provides friendly, conversational responses
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
from agents import Agent, Runner, function_tool, RunContextWrapper, OpenAIConversationsSession

from src.config import settings
from src.mcp_server.backend_client import BackendClient, BackendError
from src.mcp_server.prompts import get_full_system_prompt

logger = structlog.get_logger()

# Model configuration
MODEL_NAME = "gpt-4o-mini"


# =============================================================================
# Agent Context - Holds user_id and backend client for tools
# =============================================================================


@dataclass
class AgentContext:
    """Context passed to agent tools containing user info and API client."""

    user_id: str
    backend: BackendClient
    last_task_ids: list[str] = field(default_factory=list)
    last_operation: str = ""

    def set_task_context(self, task_ids: list[str], operation: str) -> None:
        """Update context with last mentioned tasks."""
        self.last_task_ids = task_ids
        self.last_operation = operation

    def get_last_task_id(self) -> str | None:
        """Get the most recently mentioned task ID."""
        return self.last_task_ids[0] if self.last_task_ids else None


# =============================================================================
# Tool Functions using @function_tool decorator
# =============================================================================


@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Create a new task with title, optional description, priority, due date, and tags.

    Args:
        title: The title of the task (required)
        description: Optional detailed description of the task
        priority: Task priority level - one of: low, medium, high, urgent (default: medium)
        due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        tags: List of tags/labels for the task
    """
    try:
        result = await ctx.context.backend.create_task(
            user_id=ctx.context.user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags or [],
        )

        # Extract task from response
        task = result.get("task", result)
        task_id = task.get("id", "")

        # Update context
        if task_id:
            ctx.context.set_task_context([task_id], "create")

        logger.info("task_created", task_id=task_id, title=title)

        return f"Created task: '{title}' with ID {task_id}. Priority: {priority}. Due: {due_date or 'Not set'}."

    except BackendError as e:
        logger.error("add_task_failed", error=str(e))
        return f"Failed to create task: {e.message}"


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str = "all",
    priority: str | None = None,
    limit: int = 20,
) -> str:
    """Get a list of tasks, optionally filtered by status or priority.

    Args:
        status: Filter by task status - one of: all, pending, completed (default: all)
        priority: Filter by priority level - one of: low, medium, high, urgent
        limit: Maximum number of tasks to return (default: 20)
    """
    try:
        result = await ctx.context.backend.get_tasks(
            user_id=ctx.context.user_id,
            status=status if status != "all" else None,
            priority=priority,
            limit=limit,
        )

        tasks = result.get("tasks", []) if isinstance(result, dict) else result

        if not tasks:
            return "You don't have any tasks yet. Would you like to create one?"

        # Update context with listed task IDs
        task_ids = [t.get("id") for t in tasks if t.get("id")]
        ctx.context.set_task_context(task_ids, "list")

        # Format task list
        lines = [f"Found {len(tasks)} task(s):"]
        for i, task in enumerate(tasks, 1):
            status_icon = "✓" if task.get("status") == "completed" else "○"
            priority_label = f"[{task.get('priority', 'medium').capitalize()}]"
            due = f" - Due: {task.get('due_date', 'No due date')}" if task.get("due_date") else ""
            lines.append(f"{i}. {status_icon} {priority_label} {task.get('title', 'Untitled')}{due}")
            if task.get("description"):
                lines.append(f"   Description: {task['description']}")

        return "\n".join(lines)

    except BackendError as e:
        logger.error("list_tasks_failed", error=str(e))
        return f"Failed to list tasks: {e.message}"


@function_tool
async def get_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str | None = None,
) -> str:
    """Get details of a specific task by ID.

    Args:
        task_id: The unique identifier of the task. If not provided, uses the last mentioned task.
    """
    # Use context if no task_id provided
    if not task_id:
        task_id = ctx.context.get_last_task_id()
        if not task_id:
            return "Please specify which task you want to see, or mention a task first."

    try:
        result = await ctx.context.backend.get_task(ctx.context.user_id, task_id)
        task = result.get("task", result)

        ctx.context.set_task_context([task_id], "get")

        status = "Completed" if task.get("status") == "completed" else "Pending"
        due = task.get("due_date") or "Not set"
        tags = ", ".join(task.get("tags", [])) or "None"

        return f"""Task Details:
- Title: {task.get('title', 'Untitled')}
- Description: {task.get('description') or 'No description'}
- Status: {status}
- Priority: {task.get('priority', 'medium').capitalize()}
- Due Date: {due}
- Tags: {tags}
- Created: {task.get('created_at', 'Unknown')}"""

    except BackendError as e:
        logger.error("get_task_failed", error=str(e))
        return f"Failed to get task: {e.message}"


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Update an existing task's details.

    Args:
        task_id: The unique identifier of the task to update. If not provided, uses the last mentioned task.
        title: New title for the task
        description: New description for the task
        priority: New priority level - one of: low, medium, high, urgent
        due_date: New due date in ISO format
        tags: New list of tags
    """
    # Use context if no task_id provided
    if not task_id:
        task_id = ctx.context.get_last_task_id()
        if not task_id:
            return "Please specify which task to update, or mention a task first."

    # Build updates dict
    updates: dict[str, Any] = {}
    if title is not None:
        updates["title"] = title
    if description is not None:
        updates["description"] = description
    if priority is not None:
        updates["priority"] = priority
    if due_date is not None:
        updates["due_date"] = due_date
    if tags is not None:
        updates["tags"] = tags

    if not updates:
        return "No updates specified. What would you like to change?"

    try:
        result = await ctx.context.backend.update_task(
            ctx.context.user_id, task_id, **updates
        )

        task = result.get("task", result)
        ctx.context.set_task_context([task_id], "update")

        updated_fields = ", ".join(updates.keys())
        logger.info("task_updated", task_id=task_id, fields=updated_fields)

        return f"Updated task '{task.get('title', 'Task')}': changed {updated_fields}."

    except BackendError as e:
        logger.error("update_task_failed", error=str(e))
        return f"Failed to update task: {e.message}"


@function_tool
async def complete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str | None = None,
    completed: bool = True,
) -> str:
    """Mark a task as completed or revert to pending.

    Args:
        task_id: The unique identifier of the task. If not provided, uses the last mentioned task.
        completed: True to mark complete, False to revert to pending (default: True)
    """
    # Use context if no task_id provided
    if not task_id:
        task_id = ctx.context.get_last_task_id()
        if not task_id:
            return "Please specify which task to complete, or mention a task first."

    try:
        result = await ctx.context.backend.complete_task(
            ctx.context.user_id, task_id, completed
        )

        task = result.get("task", result)
        ctx.context.set_task_context([task_id], "complete")

        if completed:
            logger.info("task_completed", task_id=task_id)
            return f"Great job! Marked '{task.get('title', 'Task')}' as complete! One less thing on your plate."
        else:
            logger.info("task_uncompleted", task_id=task_id)
            return f"Reverted '{task.get('title', 'Task')}' back to pending."

    except BackendError as e:
        logger.error("complete_task_failed", error=str(e))
        return f"Failed to complete task: {e.message}"


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str | None = None,
) -> str:
    """Delete a task permanently. Always confirm with user before calling this.

    Args:
        task_id: The unique identifier of the task to delete. If not provided, uses the last mentioned task.
    """
    # Use context if no task_id provided
    if not task_id:
        task_id = ctx.context.get_last_task_id()
        if not task_id:
            return "Please specify which task to delete, or mention a task first."

    try:
        result = await ctx.context.backend.delete_task(ctx.context.user_id, task_id)

        ctx.context.set_task_context([task_id], "delete")
        logger.info("task_deleted", task_id=task_id)

        return f"Deleted task with ID {task_id}. It's gone for good!"

    except BackendError as e:
        logger.error("delete_task_failed", error=str(e))
        return f"Failed to delete task: {e.message}"


@function_tool
async def search_tasks(
    ctx: RunContextWrapper[AgentContext],
    query: str,
) -> str:
    """Search tasks by keyword in title or description.

    Args:
        query: Search keyword to find in task titles and descriptions
    """
    try:
        tasks = await ctx.context.backend.search_tasks(ctx.context.user_id, query)

        if not tasks:
            return f"No tasks found matching '{query}'. Would you like to create one?"

        # Update context
        task_ids = [t.get("id") for t in tasks if t.get("id")]
        ctx.context.set_task_context(task_ids, "search")

        lines = [f"Found {len(tasks)} task(s) matching '{query}':"]
        for i, task in enumerate(tasks, 1):
            status_icon = "✓" if task.get("status") == "completed" else "○"
            lines.append(f"{i}. {status_icon} {task.get('title', 'Untitled')}")

        return "\n".join(lines)

    except BackendError as e:
        logger.error("search_tasks_failed", error=str(e))
        return f"Failed to search tasks: {e.message}"


@function_tool
async def filter_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str | None = None,
    priority: str | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Filter tasks by multiple criteria including date range.

    Args:
        status: Filter by status - one of: pending, completed, all
        priority: Filter by priority - one of: low, medium, high, urgent
        due_before: Filter tasks due before this date (ISO format)
        due_after: Filter tasks due after this date (ISO format)
        tags: Filter by tags (tasks must have at least one)
    """
    try:
        tasks = await ctx.context.backend.filter_tasks(
            user_id=ctx.context.user_id,
            status=status,
            priority=priority,
            due_before=due_before,
            due_after=due_after,
            tags=tags,
        )

        if not tasks:
            filters = []
            if status:
                filters.append(f"status={status}")
            if priority:
                filters.append(f"priority={priority}")
            if due_before:
                filters.append(f"due before {due_before}")
            if due_after:
                filters.append(f"due after {due_after}")
            filter_desc = ", ".join(filters) if filters else "your criteria"
            return f"No tasks found matching {filter_desc}."

        # Update context
        task_ids = [t.get("id") for t in tasks if t.get("id")]
        ctx.context.set_task_context(task_ids, "filter")

        lines = [f"Found {len(tasks)} matching task(s):"]
        for i, task in enumerate(tasks, 1):
            status_icon = "✓" if task.get("status") == "completed" else "○"
            priority_label = f"[{task.get('priority', 'medium').capitalize()}]"
            due = f" - Due: {task.get('due_date')}" if task.get("due_date") else ""
            lines.append(f"{i}. {status_icon} {priority_label} {task.get('title', 'Untitled')}{due}")

        return "\n".join(lines)

    except BackendError as e:
        logger.error("filter_tasks_failed", error=str(e))
        return f"Failed to filter tasks: {e.message}"


# =============================================================================
# Task Agent using OpenAI Agents SDK
# =============================================================================


def create_task_agent() -> Agent[AgentContext]:
    """Create the task management agent with all tools.

    Returns:
        Configured Agent instance with task management tools
    """
    return Agent[AgentContext](
        name="TaskFlow AI",
        model=MODEL_NAME,
        instructions=get_full_system_prompt(),
        tools=[
            add_task,
            list_tasks,
            get_task,
            update_task,
            complete_task,
            delete_task,
            search_tasks,
            filter_tasks,
        ],
    )


# Global agent instance
_task_agent: Agent[AgentContext] | None = None


def get_task_agent() -> Agent[AgentContext]:
    """Get or create the singleton task agent.

    Returns:
        The task management agent
    """
    global _task_agent
    if _task_agent is None:
        _task_agent = create_task_agent()
    return _task_agent


# =============================================================================
# Response Types
# =============================================================================


@dataclass
class ToolCallResult:
    """Result from executing a tool call."""

    tool_call_id: str
    tool_name: str
    success: bool
    result: dict[str, Any]


@dataclass
class AgentResponse:
    """Response from the agent after processing a message."""

    content: str
    tool_calls: list[ToolCallResult] = field(default_factory=list)
    conversation_id: str = ""


# =============================================================================
# Agent Runner - Uses OpenAI Conversations API for memory
# =============================================================================


class TaskAgentRunner:
    """Runs the task agent with OpenAI Conversations API for memory.

    Uses OpenAIConversationsSession to store conversation history
    on OpenAI's servers, NOT in PostgreSQL. This makes the backend
    completely stateless.

    Architecture:
    - Each conversation_id maps to an OpenAI conversation
    - History is stored/retrieved from OpenAI's Conversations API
    - Backend holds NO conversation state
    - PostgreSQL stores ONLY users and tasks
    """

    def __init__(self, token: str | None = None):
        """Initialize the runner.

        Args:
            token: JWT token for authenticating backend API calls
        """
        self._agent = get_task_agent()
        self._token = token

    async def run(
        self,
        user_id: str,
        message: str,
        conversation_id: str | None = None,
    ) -> AgentResponse:
        """Run the agent with a user message.

        Uses OpenAI Conversations API for automatic conversation
        memory management. No local storage needed.

        Args:
            user_id: Authenticated user ID
            message: User's natural language message
            conversation_id: OpenAI conversation ID to resume (optional)

        Returns:
            AgentResponse with content and the OpenAI conversation_id
        """
        # Create session - if conversation_id provided, resume that conversation
        # Otherwise, OpenAI creates a new conversation automatically
        session = OpenAIConversationsSession(
            conversation_id=conversation_id
        )

        # Create context for tools (user_id for backend API calls)
        context = AgentContext(
            user_id=user_id,
            backend=BackendClient(token=self._token),
        )

        logger.info(
            "agent_processing",
            user_id=user_id,
            conversation_id=conversation_id or "new",
            message_length=len(message),
        )

        try:
            # Run agent with session - OpenAI manages conversation history
            result = await Runner.run(
                self._agent,
                input=message,
                context=context,
                session=session,  # OpenAI Conversations API handles memory
            )

            # Get the conversation ID from the session (for continuity)
            # After first message, session._session_id contains the OpenAI conversation ID
            actual_conversation_id = await session._get_session_id()

            # Extract the final output
            final_output = result.final_output or ""

            logger.info(
                "agent_response_generated",
                conversation_id=actual_conversation_id,
                response_length=len(final_output),
            )

            return AgentResponse(
                content=final_output,
                tool_calls=[],  # SDK handles tools internally
                conversation_id=actual_conversation_id,
            )

        except Exception as e:
            logger.exception("agent_run_failed", error=str(e))
            # Try to get conversation ID even on error
            try:
                actual_conversation_id = await session._get_session_id()
            except Exception:
                actual_conversation_id = conversation_id or ""

            return AgentResponse(
                content=f"I encountered an error: {e!s}. Please try again.",
                tool_calls=[],
                conversation_id=actual_conversation_id,
            )


# =============================================================================
# Legacy Compatibility - TaskAgent wrapper
# =============================================================================


class TaskAgent:
    """Legacy wrapper for backward compatibility.

    Wraps the new TaskAgentRunner to maintain the same interface
    as the previous Chat Completions API implementation.
    """

    def __init__(
        self,
        backend_client: BackendClient | None = None,
        memory: Any = None,  # Ignored - OpenAI Conversations API handles memory
        token: str | None = None,
    ):
        """Initialize the task agent.

        Args:
            backend_client: HTTP client for backend API (ignored, uses token)
            memory: Conversation memory store (ignored, OpenAI handles this)
            token: JWT token for authenticating backend API calls
        """
        self._runner = TaskAgentRunner(token=token)

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: str | None = None,
    ) -> AgentResponse:
        """Process a user message and return a response.

        Args:
            user_id: Authenticated user ID
            message: User's natural language message
            conversation_id: OpenAI conversation ID to resume (optional)

        Returns:
            AgentResponse with content and any tool calls made
        """
        return await self._runner.run(user_id, message, conversation_id)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TaskAgent",
    "TaskAgentRunner",
    "AgentResponse",
    "ToolCallResult",
    "AgentContext",
    "create_task_agent",
    "get_task_agent",
    "add_task",
    "list_tasks",
    "get_task",
    "update_task",
    "complete_task",
    "delete_task",
    "search_tasks",
    "filter_tasks",
]
