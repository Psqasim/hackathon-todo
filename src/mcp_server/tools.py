"""
MCP tool definitions for task management.

This module implements the 8 MCP tools that the OpenAI agent can call:
- add_task: Create a new task
- list_tasks: Get all tasks with optional filters
- get_task: Get a specific task by ID
- update_task: Update an existing task
- delete_task: Delete a task
- complete_task: Toggle task completion status
- search_tasks: Search tasks by keyword
- filter_tasks: Filter tasks by multiple criteria

FR-002 through FR-009: Each tool implements a specific task management operation
"""

from __future__ import annotations

from typing import Annotated, Any

import structlog
from pydantic import Field

from src.mcp_server.backend_client import BackendClient, BackendError
from src.mcp_server.server import mcp

logger = structlog.get_logger()

# Global backend client (configured per-request with user auth)
_default_client = BackendClient()


def _get_client(token: str | None = None) -> BackendClient:
    """Get a backend client with optional auth token."""
    if token:
        return BackendClient(token=token)
    return _default_client


# =============================================================================
# MCP Tool Definitions
# =============================================================================


@mcp.tool()
async def add_task(
    user_id: Annotated[str, Field(description="User UUID")],
    title: Annotated[str, Field(description="Task title (required)")],
    description: Annotated[str | None, Field(description="Task description")] = None,
    priority: Annotated[str | None, Field(description="Priority: low, medium, high, urgent")] = "medium",
    due_date: Annotated[str | None, Field(description="Due date in ISO format")] = None,
    tags: Annotated[list[str] | None, Field(description="List of tags")] = None,
) -> dict[str, Any]:
    """Create a new task for a user.

    FR-002: add_task tool creates a new task with title, description,
    priority, due_date, and optional tags.
    """
    logger.info("mcp_tool_add_task", user_id=user_id, title=title)

    try:
        client = _get_client()
        result = await client.create_task(
            user_id=user_id,
            title=title,
            description=description or "",
            priority=priority or "medium",
            due_date=due_date,
            tags=tags,
        )
        logger.info("mcp_tool_add_task_success", task_id=result.get("id"))
        return {"success": True, "task": result}
    except BackendError as e:
        logger.error("mcp_tool_add_task_failed", error=str(e))
        return {"success": False, "error": str(e)}


@mcp.tool()
async def list_tasks(
    user_id: Annotated[str, Field(description="User UUID")],
    status: Annotated[str | None, Field(description="Filter: pending, completed, all")] = None,
    priority: Annotated[str | None, Field(description="Filter by priority")] = None,
    limit: Annotated[int | None, Field(description="Maximum tasks to return")] = 20,
) -> dict[str, Any]:
    """Get a list of tasks for a user.

    FR-003: list_tasks returns user's tasks with optional status
    and priority filters.
    """
    logger.info("mcp_tool_list_tasks", user_id=user_id, status=status, priority=priority)

    try:
        client = _get_client()
        result = await client.get_tasks(
            user_id=user_id,
            status=status,
            priority=priority,
            limit=limit or 20,
        )
        tasks = result if isinstance(result, list) else result.get("tasks", [])
        logger.info("mcp_tool_list_tasks_success", count=len(tasks))
        return {"success": True, "tasks": tasks, "count": len(tasks)}
    except BackendError as e:
        logger.error("mcp_tool_list_tasks_failed", error=str(e))
        return {"success": False, "error": str(e), "tasks": [], "count": 0}


@mcp.tool()
async def get_task(
    user_id: Annotated[str, Field(description="User UUID")],
    task_id: Annotated[str, Field(description="Task UUID")],
) -> dict[str, Any]:
    """Get details of a specific task.

    FR-004: get_task returns full task details by ID.
    """
    logger.info("mcp_tool_get_task", user_id=user_id, task_id=task_id)

    try:
        client = _get_client()
        result = await client.get_task(user_id, task_id)
        logger.info("mcp_tool_get_task_success", task_id=task_id)
        return {"success": True, "task": result}
    except BackendError as e:
        logger.error("mcp_tool_get_task_failed", error=str(e))
        return {"success": False, "error": str(e)}


@mcp.tool()
async def update_task(
    user_id: Annotated[str, Field(description="User UUID")],
    task_id: Annotated[str, Field(description="Task UUID")],
    title: Annotated[str | None, Field(description="New title")] = None,
    description: Annotated[str | None, Field(description="New description")] = None,
    priority: Annotated[str | None, Field(description="New priority")] = None,
    due_date: Annotated[str | None, Field(description="New due date")] = None,
    tags: Annotated[list[str] | None, Field(description="New tags")] = None,
) -> dict[str, Any]:
    """Update an existing task.

    FR-005: update_task modifies task fields.
    """
    logger.info("mcp_tool_update_task", user_id=user_id, task_id=task_id)

    try:
        client = _get_client()
        updates = {}
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

        result = await client.update_task(user_id, task_id, **updates)
        logger.info("mcp_tool_update_task_success", task_id=task_id)
        return {"success": True, "task": result}
    except BackendError as e:
        logger.error("mcp_tool_update_task_failed", error=str(e))
        return {"success": False, "error": str(e)}


@mcp.tool()
async def delete_task(
    user_id: Annotated[str, Field(description="User UUID")],
    task_id: Annotated[str, Field(description="Task UUID")],
) -> dict[str, Any]:
    """Delete a task permanently.

    FR-006: delete_task removes a task (confirmation handled by agent).
    """
    logger.info("mcp_tool_delete_task", user_id=user_id, task_id=task_id)

    try:
        client = _get_client()
        await client.delete_task(user_id, task_id)
        logger.info("mcp_tool_delete_task_success", task_id=task_id)
        return {"success": True, "deleted": True, "task_id": task_id}
    except BackendError as e:
        logger.error("mcp_tool_delete_task_failed", error=str(e))
        return {"success": False, "error": str(e)}


@mcp.tool()
async def complete_task(
    user_id: Annotated[str, Field(description="User UUID")],
    task_id: Annotated[str, Field(description="Task UUID")],
    completed: Annotated[bool, Field(description="True to complete, False to revert")] = True,
) -> dict[str, Any]:
    """Mark a task as completed or revert to pending.

    FR-007: complete_task toggles task completion status.
    """
    logger.info("mcp_tool_complete_task", user_id=user_id, task_id=task_id, completed=completed)

    try:
        client = _get_client()
        result = await client.complete_task(user_id, task_id, completed)
        status = "completed" if completed else "pending"
        logger.info("mcp_tool_complete_task_success", task_id=task_id, status=status)
        return {"success": True, "task": result, "status": status}
    except BackendError as e:
        logger.error("mcp_tool_complete_task_failed", error=str(e))
        return {"success": False, "error": str(e)}


@mcp.tool()
async def search_tasks(
    user_id: Annotated[str, Field(description="User UUID")],
    query: Annotated[str, Field(description="Search keyword")],
) -> dict[str, Any]:
    """Search tasks by keyword in title or description.

    FR-008: search_tasks finds tasks matching a keyword.
    """
    logger.info("mcp_tool_search_tasks", user_id=user_id, query=query)

    try:
        client = _get_client()
        result = await client.search_tasks(user_id, query)
        tasks = result if isinstance(result, list) else []
        logger.info("mcp_tool_search_tasks_success", count=len(tasks))
        return {"success": True, "tasks": tasks, "count": len(tasks), "query": query}
    except BackendError as e:
        logger.error("mcp_tool_search_tasks_failed", error=str(e))
        return {"success": False, "error": str(e), "tasks": [], "count": 0}


@mcp.tool()
async def filter_tasks(
    user_id: Annotated[str, Field(description="User UUID")],
    status: Annotated[str | None, Field(description="Filter by status")] = None,
    priority: Annotated[str | None, Field(description="Filter by priority")] = None,
    due_before: Annotated[str | None, Field(description="Tasks due before date")] = None,
    due_after: Annotated[str | None, Field(description="Tasks due after date")] = None,
    tags: Annotated[list[str] | None, Field(description="Filter by tags")] = None,
) -> dict[str, Any]:
    """Filter tasks by multiple criteria.

    FR-009: filter_tasks applies multiple filters to task list.
    """
    logger.info(
        "mcp_tool_filter_tasks",
        user_id=user_id,
        status=status,
        priority=priority,
        due_before=due_before,
        due_after=due_after,
    )

    try:
        client = _get_client()
        result = await client.filter_tasks(
            user_id=user_id,
            status=status,
            priority=priority,
            due_before=due_before,
            due_after=due_after,
            tags=tags,
        )
        tasks = result if isinstance(result, list) else []
        logger.info("mcp_tool_filter_tasks_success", count=len(tasks))
        return {"success": True, "tasks": tasks, "count": len(tasks)}
    except BackendError as e:
        logger.error("mcp_tool_filter_tasks_failed", error=str(e))
        return {"success": False, "error": str(e), "tasks": [], "count": 0}


# Export all tools
__all__ = [
    "add_task",
    "list_tasks",
    "get_task",
    "update_task",
    "delete_task",
    "complete_task",
    "search_tasks",
    "filter_tasks",
]
