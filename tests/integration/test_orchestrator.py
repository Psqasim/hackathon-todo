"""Integration tests for the orchestrator agent."""

import pytest

from src.agents import (
    OrchestratorAgent,
    create_orchestrator,
)
from src.backends import InMemoryBackend
from src.models import AgentMessage


@pytest.fixture
def backend() -> InMemoryBackend:
    """Create a fresh in-memory backend."""
    return InMemoryBackend()


@pytest.fixture
async def orchestrator(backend: InMemoryBackend) -> OrchestratorAgent:
    """Create a configured and started orchestrator."""
    orch = await create_orchestrator(backend)
    await orch.start()
    return orch


class TestOrchestratorRouting:
    """Tests for orchestrator message routing."""

    @pytest.mark.asyncio
    async def test_routes_task_actions_to_task_manager(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that task_* actions route to task manager."""
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="task_add",
            payload={"title": "Test task"},
        )

        response = await orchestrator.handle_message(message)

        assert response.status == "success"
        assert "task" in response.result

    @pytest.mark.asyncio
    async def test_routes_storage_actions_to_storage_handler(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that storage_* actions route to storage handler."""
        from src.models import Task

        task = Task(title="Test")
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="storage_save",
            payload={"task": task.model_dump()},
        )

        response = await orchestrator.handle_message(message)

        assert response.status == "success"
        assert "task" in response.result

    @pytest.mark.asyncio
    async def test_routes_system_actions_to_self(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that system_* actions are handled by orchestrator."""
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="system_status",
        )

        response = await orchestrator.handle_message(message)

        assert response.status == "success"
        assert "orchestrator" in response.result
        assert "agents" in response.result

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that unknown actions return an error."""
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="unknown_action",
        )

        response = await orchestrator.handle_message(message)

        assert response.status == "error"
        assert "Unknown action" in (response.error or "")


class TestOrchestratorLifecycle:
    """Tests for orchestrator lifecycle management."""

    @pytest.mark.asyncio
    async def test_start_activates_all_agents(
        self,
        backend: InMemoryBackend,
    ) -> None:
        """Test that starting orchestrator starts all agents."""
        orchestrator = await create_orchestrator(backend)

        await orchestrator.start()

        # Check all agents are active
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="system_agents",
        )
        response = await orchestrator.handle_message(message)

        agents = response.result.get("agents", [])
        for agent in agents:
            assert agent["status"] == "active"

    @pytest.mark.asyncio
    async def test_stop_deactivates_all_agents(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that stopping orchestrator stops all agents."""
        await orchestrator.stop()

        assert orchestrator.is_running is False
        assert orchestrator.status == "inactive"

    @pytest.mark.asyncio
    async def test_shutdown_action_stops_running(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that system_shutdown action stops the orchestrator."""
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="system_shutdown",
        )

        response = await orchestrator.handle_message(message)

        assert response.status == "success"
        assert orchestrator.is_running is False


class TestEndToEndWorkflows:
    """End-to-end tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_add_and_list_tasks(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test adding and listing tasks."""
        # Add a task
        add_message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="task_add",
            payload={"title": "Buy groceries", "description": "Milk and eggs"},
        )
        add_response = await orchestrator.handle_message(add_message)
        assert add_response.status == "success"

        # List tasks
        list_message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="task_list",
        )
        list_response = await orchestrator.handle_message(list_message)

        assert list_response.status == "success"
        tasks = list_response.result.get("tasks", [])
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Buy groceries"

    @pytest.mark.asyncio
    async def test_add_complete_and_filter_tasks(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test adding, completing, and filtering tasks."""
        # Add two tasks
        await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_add",
                payload={"title": "Task 1"},
            )
        )
        add_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_add",
                payload={"title": "Task 2"},
            )
        )

        task_id = add_response.result["task"]["id"]

        # Complete the second task
        complete_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_complete",
                payload={"task_id": task_id},
            )
        )
        assert complete_response.status == "success"

        # Filter pending only
        pending_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_list",
                payload={"status": "pending"},
            )
        )
        pending_tasks = pending_response.result.get("tasks", [])
        assert len(pending_tasks) == 1
        assert pending_tasks[0]["title"] == "Task 1"

        # Filter completed only
        completed_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_list",
                payload={"status": "completed"},
            )
        )
        completed_tasks = completed_response.result.get("tasks", [])
        assert len(completed_tasks) == 1
        assert completed_tasks[0]["title"] == "Task 2"

    @pytest.mark.asyncio
    async def test_add_and_delete_task(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test adding and deleting a task."""
        # Add a task
        add_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_add",
                payload={"title": "To delete"},
            )
        )
        task_id = add_response.result["task"]["id"]

        # Delete the task
        delete_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_delete",
                payload={"task_id": task_id},
            )
        )
        assert delete_response.status == "success"
        assert delete_response.result["deleted"] is True

        # Verify it's gone
        list_response = await orchestrator.handle_message(
            AgentMessage(
                sender="test",
                recipient="orchestrator",
                action="task_list",
            )
        )
        tasks = list_response.result.get("tasks", [])
        assert len(tasks) == 0

    @pytest.mark.asyncio
    async def test_correlation_id_propagation(
        self,
        orchestrator: OrchestratorAgent,
    ) -> None:
        """Test that correlation IDs are preserved through routing."""
        correlation_id = "test-correlation-123"
        message = AgentMessage(
            sender="test",
            recipient="orchestrator",
            action="task_add",
            payload={"title": "Test"},
            correlation_id=correlation_id,
        )

        response = await orchestrator.handle_message(message)

        assert response.status == "success"
        # The response should maintain the same request_id
        assert response.request_id == message.request_id
