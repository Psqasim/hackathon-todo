"""
Orchestrator Agent.

Central coordinator that routes messages between agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.base import BaseAgent
from src.models import (
    AgentMessage,
    AgentResponse,
)

if TYPE_CHECKING:
    pass


class OrchestratorAgent(BaseAgent):
    """
    Central orchestrator agent that coordinates all other agents.

    Routes messages based on action prefixes:
        - task_* -> TaskManagerAgent
        - storage_* -> StorageHandlerAgent
        - ui_* -> UIControllerAgent
        - system_* -> Self (orchestrator)

    Handles system actions:
        - system_status: Get system status
        - system_agents: List registered agents
        - system_shutdown: Graceful shutdown
    """

    # Action prefix to agent name mapping
    ROUTE_PREFIXES = {
        "task_": "task_manager",
        "storage_": "storage_handler",
        "ui_": "ui_controller",
        "system_": "orchestrator",
    }

    def __init__(
        self,
        name: str = "orchestrator",
        version: str = "1.0.0",
    ) -> None:
        """
        Initialize the orchestrator agent.

        Args:
            name: Agent name.
            version: Agent version.
        """
        super().__init__(name, version)
        self._agents: dict[str, BaseAgent] = {}
        self._running = False

        # Register system action handlers
        self.register_action("system_status", self._handle_status)
        self.register_action("system_agents", self._handle_agents)
        self.register_action("system_shutdown", self._handle_shutdown)

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent to register.
        """
        self._agents[agent.name] = agent
        self._log.info("agent_registered", agent_name=agent.name)

    def get_agent(self, name: str) -> BaseAgent | None:
        """
        Get a registered agent by name.

        Args:
            name: Agent name.

        Returns:
            The agent if found, None otherwise.
        """
        return self._agents.get(name)

    async def start(self) -> None:
        """Start the orchestrator and all registered agents."""
        await super().start()
        self._running = True

        # Start all registered agents
        for agent in self._agents.values():
            await agent.start()
            self._log.info("started_agent", agent_name=agent.name)

    async def stop(self) -> None:
        """Stop the orchestrator and all registered agents."""
        self._running = False

        # Stop all registered agents
        for agent in self._agents.values():
            await agent.stop()
            self._log.info("stopped_agent", agent_name=agent.name)

        await super().stop()

    @property
    def is_running(self) -> bool:
        """Check if the orchestrator is running."""
        return self._running

    def _get_route_for_action(self, action: str) -> str | None:
        """
        Determine which agent should handle an action.

        Args:
            action: The action name.

        Returns:
            Agent name if a route is found, None otherwise.
        """
        for prefix, agent_name in self.ROUTE_PREFIXES.items():
            if action.startswith(prefix):
                return agent_name
        return None

    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Handle incoming messages by routing to appropriate agent.

        Args:
            message: The incoming message.

        Returns:
            AgentResponse from the target agent or error.
        """
        self._log.info(
            "routing_message",
            action=message.action,
            sender=message.sender,
            request_id=message.request_id,
        )

        # Determine route
        agent_name = self._get_route_for_action(message.action)

        if agent_name is None:
            self._log.warning("unknown_route", action=message.action)
            return self._create_error_response(
                message.request_id,
                f"Unknown action: {message.action}. "
                f"Expected prefixes: {list(self.ROUTE_PREFIXES.keys())}",
            )

        # Handle system actions ourselves
        if agent_name == "orchestrator":
            handler = self._actions.get(message.action)
            if handler is None:
                return self._create_error_response(
                    message.request_id,
                    f"Unknown system action: {message.action}",
                )
            try:
                return await handler(message)
            except Exception as e:
                self._log.error("system_action_error", error=str(e))
                return self._create_error_response(
                    message.request_id,
                    f"System error: {e}",
                )

        # Get target agent
        agent = self._agents.get(agent_name)
        if agent is None:
            self._log.error("agent_not_found", agent_name=agent_name)
            return self._create_error_response(
                message.request_id,
                f"Agent not registered: {agent_name}",
            )

        # Forward message to agent
        try:
            response = await agent.handle_message(message)
            self._log.info(
                "message_routed",
                action=message.action,
                target=agent_name,
                status=response.status,
            )
            return response
        except Exception as e:
            self._log.error(
                "routing_error",
                action=message.action,
                target=agent_name,
                error=str(e),
            )
            return self._create_error_response(
                message.request_id,
                f"Error routing to {agent_name}: {e}",
            )

    async def _handle_status(self, message: AgentMessage) -> AgentResponse:
        """Handle system_status action."""
        agents_info = []
        for agent in self._agents.values():
            info = agent.get_info()
            agents_info.append(info.model_dump())

        return self._create_success_response(
            message.request_id,
            {
                "orchestrator": {
                    "name": self._name,
                    "version": self._version,
                    "status": self._status,
                    "running": self._running,
                },
                "agents": agents_info,
                "total_agents": len(self._agents),
            },
        )

    async def _handle_agents(self, message: AgentMessage) -> AgentResponse:
        """Handle system_agents action."""
        agents = [agent.get_info().model_dump() for agent in self._agents.values()]

        return self._create_success_response(
            message.request_id,
            {"agents": agents, "count": len(agents)},
        )

    async def _handle_shutdown(self, message: AgentMessage) -> AgentResponse:
        """Handle system_shutdown action."""
        self._log.info("shutdown_requested")
        self._running = False

        return self._create_success_response(
            message.request_id,
            {"shutdown": True},
        )


async def create_orchestrator(
    storage_backend: StorageBackend,  # noqa: F821
) -> OrchestratorAgent:
    """
    Factory function to create a fully configured orchestrator.

    Creates and wires up all agents:
        - StorageHandlerAgent with provided backend
        - TaskManagerAgent with storage dependency
        - UIControllerAgent with console adapter
        - OrchestratorAgent with all agents registered

    Args:
        storage_backend: Storage backend implementation.

    Returns:
        Configured and started OrchestratorAgent.
    """
    from src.adapters.console import ConsoleAdapter
    from src.agents.storage_handler import StorageHandlerAgent
    from src.agents.task_manager import TaskManagerAgent
    from src.agents.ui_controller import UIControllerAgent

    # Create agents
    storage_agent = StorageHandlerAgent(storage_backend)
    task_agent = TaskManagerAgent(storage_agent)
    ui_agent = UIControllerAgent(ConsoleAdapter())

    # Create and configure orchestrator
    orchestrator = OrchestratorAgent()
    orchestrator.register_agent(storage_agent)
    orchestrator.register_agent(task_agent)
    orchestrator.register_agent(ui_agent)

    return orchestrator
