"""
Base Agent Abstract Base Class.

Defines the contract that all agents must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import structlog

from src.models import AgentInfo, AgentMessage, AgentResponse

if TYPE_CHECKING:
    from collections.abc import Callable

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    All agents must implement:
        - handle_message: Process incoming messages and return responses
        - get_info: Return agent metadata

    Provides:
        - Action registration via decorators
        - Automatic logging with structlog
        - Correlation ID propagation
        - Lifecycle management (start/stop)
    """

    def __init__(self, name: str, version: str = "1.0.0") -> None:
        """
        Initialize the base agent.

        Args:
            name: Unique identifier for this agent.
            version: Semantic version string (e.g., '1.0.0').
        """
        self._name = name
        self._version = version
        self._status: str = "inactive"
        self._actions: dict[str, Callable[..., AgentResponse]] = {}
        self._log = logger.bind(agent=name)

    @property
    def name(self) -> str:
        """Return the agent's name."""
        return self._name

    @property
    def version(self) -> str:
        """Return the agent's version."""
        return self._version

    @property
    def status(self) -> str:
        """Return the agent's current status."""
        return self._status

    @property
    def supported_actions(self) -> list[str]:
        """Return list of actions this agent can handle."""
        return list(self._actions.keys())

    def register_action(
        self,
        action: str,
        handler: Callable[..., AgentResponse],
    ) -> None:
        """
        Register an action handler.

        Args:
            action: The action name to handle.
            handler: The function to call for this action.
        """
        self._actions[action] = handler
        self._log.debug("registered_action", action=action)

    async def start(self) -> None:
        """
        Start the agent.

        Performs any necessary initialization and sets status to 'active'.
        Override in subclasses for custom startup logic.
        """
        self._status = "active"
        self._log.info("agent_started", version=self._version)

    async def stop(self) -> None:
        """
        Stop the agent.

        Performs any necessary cleanup and sets status to 'inactive'.
        Override in subclasses for custom shutdown logic.
        """
        self._status = "inactive"
        self._log.info("agent_stopped")

    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Handle an incoming message.

        This is the main entry point for agent message processing.
        Subclasses must implement this method.

        Args:
            message: The incoming message to process.

        Returns:
            AgentResponse with success/error status and result/error.
        """
        pass

    def get_info(self) -> AgentInfo:
        """
        Return metadata about this agent.

        Returns:
            AgentInfo with name, status, version, and supported actions.
        """
        return AgentInfo(
            name=self._name,
            status=self._status,  # type: ignore[arg-type]
            version=self._version,
            supported_actions=self.supported_actions,
        )

    def _create_success_response(
        self,
        request_id: str,
        result: object = None,
    ) -> AgentResponse:
        """
        Create a success response.

        Args:
            request_id: The original request ID.
            result: Optional result data.

        Returns:
            AgentResponse with success status.
        """
        return AgentResponse(
            request_id=request_id,
            sender=self._name,
            status="success",
            result=result,
        )

    def _create_error_response(
        self,
        request_id: str,
        error: str,
    ) -> AgentResponse:
        """
        Create an error response.

        Args:
            request_id: The original request ID.
            error: Error message.

        Returns:
            AgentResponse with error status.
        """
        return AgentResponse(
            request_id=request_id,
            sender=self._name,
            status="error",
            error=error,
        )


def action_handler(action: str) -> Callable[..., Callable[..., AgentResponse]]:
    """
    Decorator to register a method as an action handler.

    Usage:
        @action_handler("task_add")
        async def handle_task_add(self, message: AgentMessage) -> AgentResponse:
            ...

    Args:
        action: The action name this method handles.

    Returns:
        Decorator function.
    """

    def decorator(
        func: Callable[..., AgentResponse],
    ) -> Callable[..., AgentResponse]:
        func._action = action  # type: ignore[attr-defined]
        return func

    return decorator
