"""
Exception hierarchy for the Multi-Agent Todo Application.

Provides structured error types for different failure scenarios.
"""

from __future__ import annotations


class AgentError(Exception):
    """
    Base exception for all agent-related errors.

    All custom exceptions in the multi-agent system inherit from this.
    """

    def __init__(self, message: str, agent_name: str | None = None) -> None:
        self.message = message
        self.agent_name = agent_name
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with optional agent context."""
        if self.agent_name:
            return f"[{self.agent_name}] {self.message}"
        return self.message


class ValidationError(AgentError):
    """
    Raised when input validation fails.

    Examples:
        - Empty task title
        - Description exceeds max length
        - Invalid action format
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        agent_name: str | None = None,
    ) -> None:
        self.field = field
        super().__init__(message, agent_name)

    def _format_message(self) -> str:
        """Format with field context if available."""
        base = super()._format_message()
        if self.field:
            return f"{base} (field: {self.field})"
        return base


class NotFoundError(AgentError):
    """
    Raised when a requested resource is not found.

    Examples:
        - Task with given ID doesn't exist
        - Agent not registered
    """

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        agent_name: str | None = None,
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message, agent_name)

    def _format_message(self) -> str:
        """Format with resource context if available."""
        base = super()._format_message()
        parts = []
        if self.resource_type:
            parts.append(f"type={self.resource_type}")
        if self.resource_id:
            parts.append(f"id={self.resource_id}")
        if parts:
            return f"{base} ({', '.join(parts)})"
        return base


class StorageError(AgentError):
    """
    Raised when storage operations fail.

    Examples:
        - Failed to save task
        - Failed to load tasks
        - Storage backend unavailable
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        agent_name: str | None = None,
    ) -> None:
        self.operation = operation
        super().__init__(message, agent_name)

    def _format_message(self) -> str:
        """Format with operation context if available."""
        base = super()._format_message()
        if self.operation:
            return f"{base} (operation: {self.operation})"
        return base


class RoutingError(AgentError):
    """
    Raised when message routing fails.

    Examples:
        - Unknown action prefix
        - Target agent not found
        - Circular routing detected
    """

    def __init__(
        self,
        message: str,
        action: str | None = None,
        agent_name: str | None = None,
    ) -> None:
        self.action = action
        super().__init__(message, agent_name)

    def _format_message(self) -> str:
        """Format with action context if available."""
        base = super()._format_message()
        if self.action:
            return f"{base} (action: {self.action})"
        return base


class AgentInitError(AgentError):
    """
    Raised when agent initialization fails.

    Examples:
        - Missing required dependencies
        - Configuration error
        - Failed to connect to backend
    """

    pass
