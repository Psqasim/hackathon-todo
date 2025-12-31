"""
HTTP client for FastAPI backend.

This module provides an async HTTP client using httpx to call
the existing FastAPI backend endpoints for task operations.

FR-010: MCP server MUST call existing FastAPI endpoints (NO direct database access)
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


def get_mcp_backend_url() -> str:
    """Get the backend URL for MCP server to call.

    Priority:
    1. MCP_BACKEND_URL environment variable
    2. BACKEND_URL environment variable
    3. Railway auto-detection (if running on Railway)
    4. Default to localhost
    """
    # Check explicit MCP_BACKEND_URL first
    mcp_url = os.getenv("MCP_BACKEND_URL")
    if mcp_url:
        return mcp_url

    # Check BACKEND_URL (used by the main app)
    backend_url = os.getenv("BACKEND_URL")
    if backend_url:
        return backend_url

    # Auto-detect Railway environment
    railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_public_domain:
        return f"https://{railway_public_domain}"

    # Default to localhost for development
    return "http://localhost:8000"


# Backend URL configuration (computed once at module load)
MCP_BACKEND_URL = get_mcp_backend_url()

# HTTP client timeout settings
TIMEOUT_SECONDS = 30.0


class BackendClientError(Exception):
    """Exception raised when backend API call fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Alias for cleaner imports
BackendError = BackendClientError


class BackendClient:
    """Async HTTP client for calling FastAPI backend.

    This client wraps httpx to provide a clean interface for
    MCP tools to call the existing backend API endpoints.
    """

    def __init__(self, base_url: str | None = None, token: str | None = None):
        """Initialize the backend client.

        Args:
            base_url: Backend URL (defaults to MCP_BACKEND_URL env var)
            token: JWT token for authentication
        """
        self.base_url = (base_url or MCP_BACKEND_URL).rstrip("/")
        self.token = token
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=TIMEOUT_SECONDS,
                headers=self._get_headers(),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check if backend is reachable.

        Returns:
            True if backend responds to health check
        """
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request to the backend.

        Args:
            path: API endpoint path (e.g., "/api/users/123/tasks")
            params: Query parameters

        Returns:
            Response JSON as dict

        Raises:
            BackendClientError: If request fails
        """
        try:
            client = await self._get_client()
            response = await client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendClientError(
                f"Backend returned {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise BackendClientError(f"Failed to connect to backend: {e!s}") from e

    async def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a POST request to the backend.

        Args:
            path: API endpoint path
            json: Request body as dict

        Returns:
            Response JSON as dict

        Raises:
            BackendClientError: If request fails
        """
        try:
            client = await self._get_client()
            response = await client.post(path, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendClientError(
                f"Backend returned {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise BackendClientError(f"Failed to connect to backend: {e!s}") from e

    async def patch(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a PATCH request to the backend.

        Args:
            path: API endpoint path
            json: Request body as dict

        Returns:
            Response JSON as dict

        Raises:
            BackendClientError: If request fails
        """
        try:
            client = await self._get_client()
            response = await client.patch(path, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendClientError(
                f"Backend returned {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise BackendClientError(f"Failed to connect to backend: {e!s}") from e

    async def put(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a PUT request to the backend.

        Args:
            path: API endpoint path
            json: Request body as dict

        Returns:
            Response JSON as dict

        Raises:
            BackendClientError: If request fails
        """
        try:
            client = await self._get_client()
            response = await client.put(path, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendClientError(
                f"Backend returned {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise BackendClientError(f"Failed to connect to backend: {e!s}") from e

    async def delete(self, path: str) -> dict[str, Any]:
        """Make a DELETE request to the backend.

        Args:
            path: API endpoint path

        Returns:
            Response JSON as dict

        Raises:
            BackendClientError: If request fails
        """
        try:
            client = await self._get_client()
            response = await client.delete(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendClientError(
                f"Backend returned {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise BackendClientError(f"Failed to connect to backend: {e!s}") from e

    # Convenience methods for task operations

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new task for a user.

        Args:
            user_id: User UUID
            title: Task title
            description: Task description
            priority: Priority level (low, medium, high, urgent)
            due_date: Due date in ISO format
            tags: List of tags

        Returns:
            Created task data
        """
        payload = {
            "title": title,
            "description": description,
            "priority": priority,
        }
        if due_date:
            payload["due_date"] = due_date
        if tags:
            payload["tags"] = tags

        return await self.post(f"/api/users/{user_id}/tasks", json=payload)

    async def get_tasks(
        self,
        user_id: str,
        status: str | None = None,
        priority: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get tasks for a user.

        Args:
            user_id: User UUID
            status: Filter by status (pending, completed)
            priority: Filter by priority
            limit: Maximum number of tasks

        Returns:
            List of tasks
        """
        params: dict[str, Any] = {"limit": limit}
        if status and status != "all":
            params["status"] = status
        if priority:
            params["priority"] = priority

        return await self.get(f"/api/users/{user_id}/tasks", params=params)

    async def get_task(self, user_id: str, task_id: str) -> dict[str, Any]:
        """Get a specific task.

        Args:
            user_id: User UUID
            task_id: Task UUID

        Returns:
            Task data
        """
        return await self.get(f"/api/users/{user_id}/tasks/{task_id}")

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        **updates: Any,
    ) -> dict[str, Any]:
        """Update a task.

        Args:
            user_id: User UUID
            task_id: Task UUID
            **updates: Fields to update

        Returns:
            Updated task data
        """
        # Filter out None values
        payload = {k: v for k, v in updates.items() if v is not None}
        return await self.put(f"/api/users/{user_id}/tasks/{task_id}", json=payload)

    async def delete_task(self, user_id: str, task_id: str) -> dict[str, Any]:
        """Delete a task.

        Args:
            user_id: User UUID
            task_id: Task UUID

        Returns:
            Deletion confirmation
        """
        return await self.delete(f"/api/users/{user_id}/tasks/{task_id}")

    async def complete_task(
        self,
        user_id: str,
        task_id: str,
        completed: bool = True,
    ) -> dict[str, Any]:
        """Mark a task as complete or pending.

        Args:
            user_id: User UUID
            task_id: Task UUID
            completed: True to mark complete, False for pending

        Returns:
            Updated task data
        """
        # Use the dedicated complete endpoint with PATCH
        return await self.patch(
            f"/api/users/{user_id}/tasks/{task_id}/complete",
            json={"completed": completed},
        )

    async def search_tasks(
        self,
        user_id: str,
        query: str,
    ) -> list[dict[str, Any]]:
        """Search tasks by keyword in title or description.

        Args:
            user_id: User UUID
            query: Search keyword

        Returns:
            List of matching tasks
        """
        # Fetch all tasks and filter client-side (no search endpoint exists)
        result = await self.get_tasks(user_id, limit=100)
        tasks = result.get("tasks", []) if isinstance(result, dict) else result

        # Case-insensitive search in title and description
        query_lower = query.lower()
        matching_tasks = [
            task
            for task in tasks
            if query_lower in (task.get("title", "") or "").lower()
            or query_lower in (task.get("description", "") or "").lower()
        ]

        return matching_tasks

    async def filter_tasks(
        self,
        user_id: str,
        status: str | None = None,
        priority: str | None = None,
        due_before: str | None = None,
        due_after: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Filter tasks by multiple criteria.

        Args:
            user_id: User UUID
            status: Filter by status
            priority: Filter by priority
            due_before: Tasks due before this date
            due_after: Tasks due after this date
            tags: Filter by tags

        Returns:
            List of matching tasks
        """
        params: dict[str, Any] = {}
        if status and status != "all":
            params["status"] = status
        if priority:
            params["priority"] = priority
        if due_before:
            params["due_before"] = due_before
        if due_after:
            params["due_after"] = due_after
        if tags:
            params["tags"] = ",".join(tags)

        result = await self.get(f"/api/users/{user_id}/tasks", params=params)
        return result if isinstance(result, list) else result.get("tasks", [])
