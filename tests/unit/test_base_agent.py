"""Unit tests for BaseAgent ABC."""

import pytest

from src.agents.base import BaseAgent, action_handler
from src.models import AgentMessage, AgentResponse


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""

    def __init__(self, name: str = "test_agent", version: str = "1.0.0") -> None:
        super().__init__(name, version)
        self.register_action("test_action", self._handle_test_action)

    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """Handle incoming messages."""
        if message.action in self._actions:
            return self._actions[message.action](message)
        return self._create_error_response(
            message.request_id,
            f"Unknown action: {message.action}",
        )

    def _handle_test_action(self, message: AgentMessage) -> AgentResponse:
        """Handle test_action."""
        return self._create_success_response(
            message.request_id,
            {"handled": True},
        )


class TestBaseAgentInitialization:
    """Tests for BaseAgent initialization."""

    def test_create_agent(self) -> None:
        """Test creating an agent with name and version."""
        agent = ConcreteAgent("my_agent", "2.0.0")

        assert agent.name == "my_agent"
        assert agent.version == "2.0.0"
        assert agent.status == "inactive"

    def test_default_version(self) -> None:
        """Test that version defaults to 1.0.0."""
        agent = ConcreteAgent("test")

        assert agent.version == "1.0.0"

    def test_initial_status_is_inactive(self) -> None:
        """Test that agent starts as inactive."""
        agent = ConcreteAgent("test")

        assert agent.status == "inactive"


class TestBaseAgentLifecycle:
    """Tests for agent lifecycle management."""

    @pytest.mark.asyncio
    async def test_start_sets_status_active(self) -> None:
        """Test that start() sets status to active."""
        agent = ConcreteAgent("test")

        await agent.start()

        assert agent.status == "active"

    @pytest.mark.asyncio
    async def test_stop_sets_status_inactive(self) -> None:
        """Test that stop() sets status to inactive."""
        agent = ConcreteAgent("test")
        await agent.start()

        await agent.stop()

        assert agent.status == "inactive"


class TestBaseAgentActions:
    """Tests for action registration and handling."""

    def test_register_action(self) -> None:
        """Test registering an action handler."""
        agent = ConcreteAgent("test")

        def handler(msg: AgentMessage) -> AgentResponse:
            return agent._create_success_response(msg.request_id)

        agent.register_action("new_action", handler)

        assert "new_action" in agent.supported_actions

    def test_supported_actions(self) -> None:
        """Test that supported_actions returns registered actions."""
        agent = ConcreteAgent("test")

        actions = agent.supported_actions

        assert "test_action" in actions

    @pytest.mark.asyncio
    async def test_handle_registered_action(self) -> None:
        """Test handling a registered action."""
        agent = ConcreteAgent("test")
        message = AgentMessage(
            sender="client",
            recipient="test",
            action="test_action",
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result == {"handled": True}

    @pytest.mark.asyncio
    async def test_handle_unknown_action(self) -> None:
        """Test handling an unknown action returns error."""
        agent = ConcreteAgent("test")
        message = AgentMessage(
            sender="client",
            recipient="test",
            action="unknown_action",
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Unknown action" in (response.error or "")


class TestBaseAgentInfo:
    """Tests for agent info."""

    @pytest.mark.asyncio
    async def test_get_info_inactive(self) -> None:
        """Test get_info when agent is inactive."""
        agent = ConcreteAgent("test_agent", "1.2.3")

        info = agent.get_info()

        assert info.name == "test_agent"
        assert info.status == "inactive"
        assert info.version == "1.2.3"
        assert "test_action" in info.supported_actions

    @pytest.mark.asyncio
    async def test_get_info_active(self) -> None:
        """Test get_info when agent is active."""
        agent = ConcreteAgent("test_agent", "1.2.3")
        await agent.start()

        info = agent.get_info()

        assert info.status == "active"


class TestBaseAgentResponseHelpers:
    """Tests for response helper methods."""

    def test_create_success_response(self) -> None:
        """Test creating a success response."""
        agent = ConcreteAgent("test")

        response = agent._create_success_response(
            "req-123",
            {"data": "value"},
        )

        assert response.request_id == "req-123"
        assert response.sender == "test"
        assert response.status == "success"
        assert response.result == {"data": "value"}

    def test_create_success_response_no_result(self) -> None:
        """Test creating a success response without result."""
        agent = ConcreteAgent("test")

        response = agent._create_success_response("req-123")

        assert response.status == "success"
        assert response.result is None

    def test_create_error_response(self) -> None:
        """Test creating an error response."""
        agent = ConcreteAgent("test")

        response = agent._create_error_response(
            "req-123",
            "Something went wrong",
        )

        assert response.request_id == "req-123"
        assert response.sender == "test"
        assert response.status == "error"
        assert response.error == "Something went wrong"


class TestActionHandlerDecorator:
    """Tests for action_handler decorator."""

    def test_decorator_sets_action_attribute(self) -> None:
        """Test that decorator sets _action attribute."""

        @action_handler("my_action")
        def handler(message: AgentMessage) -> AgentResponse:
            pass  # type: ignore[return-value]

        assert hasattr(handler, "_action")
        assert handler._action == "my_action"  # type: ignore[attr-defined]
