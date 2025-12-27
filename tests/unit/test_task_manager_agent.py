"""Unit tests for TaskManagerAgent."""

import pytest

from src.agents import StorageHandlerAgent, TaskManagerAgent
from src.backends import InMemoryBackend
from src.models import AgentMessage, Task


@pytest.fixture
def backend() -> InMemoryBackend:
    """Create a fresh in-memory backend."""
    return InMemoryBackend()


@pytest.fixture
def storage_agent(backend: InMemoryBackend) -> StorageHandlerAgent:
    """Create a storage handler agent."""
    return StorageHandlerAgent(backend)


@pytest.fixture
def agent(storage_agent: StorageHandlerAgent) -> TaskManagerAgent:
    """Create a task manager agent."""
    return TaskManagerAgent(storage_agent)


class TestTaskManagerAgentInit:
    """Tests for TaskManagerAgent initialization."""

    def test_registers_all_actions(self, agent: TaskManagerAgent) -> None:
        """Test that all task actions are registered."""
        expected_actions = [
            "task_add",
            "task_list",
            "task_complete",
            "task_delete",
            "task_get",
            "task_update",
        ]
        for action in expected_actions:
            assert action in agent.supported_actions


class TestTaskManagerAdd:
    """Tests for task_add action."""

    @pytest.mark.asyncio
    async def test_add_task_success(self, agent: TaskManagerAgent) -> None:
        """Test adding a task successfully."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_add",
            payload={"title": "New task", "description": "Test description"},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        task = response.result["task"]
        assert task["title"] == "New task"
        assert task["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_add_task_missing_title(self, agent: TaskManagerAgent) -> None:
        """Test that missing title returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_add",
            payload={"description": "No title"},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Missing 'title'" in (response.error or "")


class TestTaskManagerList:
    """Tests for task_list action."""

    @pytest.mark.asyncio
    async def test_list_all_tasks(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test listing all tasks."""
        await backend.save(Task(title="Task 1"))
        await backend.save(Task(title="Task 2"))

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_list",
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["count"] == 2

    @pytest.mark.asyncio
    async def test_list_pending_only(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test listing pending tasks only."""
        await backend.save(Task(title="Pending"))
        await backend.save(Task(title="Completed").mark_complete())

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_list",
            payload={"status": "pending"},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["count"] == 1
        assert response.result["tasks"][0]["title"] == "Pending"


class TestTaskManagerComplete:
    """Tests for task_complete action."""

    @pytest.mark.asyncio
    async def test_complete_task_success(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test completing a task successfully."""
        task = Task(title="To complete")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_complete",
            payload={"task_id": task.id},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_complete_nonexistent_task(self, agent: TaskManagerAgent) -> None:
        """Test completing a nonexistent task returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_complete",
            payload={"task_id": "nonexistent"},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"

    @pytest.mark.asyncio
    async def test_complete_missing_task_id(self, agent: TaskManagerAgent) -> None:
        """Test that missing task_id returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_complete",
            payload={},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Missing 'task_id'" in (response.error or "")


class TestTaskManagerDelete:
    """Tests for task_delete action."""

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test deleting a task successfully."""
        task = Task(title="To delete")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_delete",
            payload={"task_id": task.id},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["deleted"] is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, agent: TaskManagerAgent) -> None:
        """Test deleting a nonexistent task returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_delete",
            payload={"task_id": "nonexistent"},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"


class TestTaskManagerGet:
    """Tests for task_get action."""

    @pytest.mark.asyncio
    async def test_get_task_success(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test getting a task successfully."""
        task = Task(title="To get", description="Details")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_get",
            payload={"task_id": task.id},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["title"] == "To get"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, agent: TaskManagerAgent) -> None:
        """Test getting a nonexistent task returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_get",
            payload={"task_id": "nonexistent"},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"


class TestTaskManagerUpdate:
    """Tests for task_update action."""

    @pytest.mark.asyncio
    async def test_update_title(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test updating task title."""
        task = Task(title="Original")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_update",
            payload={"task_id": task.id, "title": "Updated"},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["title"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_description(
        self,
        agent: TaskManagerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test updating task description."""
        task = Task(title="Test", description="Old")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_update",
            payload={"task_id": task.id, "description": "New"},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["description"] == "New"

    @pytest.mark.asyncio
    async def test_update_no_fields(self, agent: TaskManagerAgent) -> None:
        """Test that update with no fields returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_update",
            payload={"task_id": "some-id"},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "No update fields" in (response.error or "")


class TestTaskManagerUnknownAction:
    """Tests for unknown action handling."""

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self, agent: TaskManagerAgent) -> None:
        """Test that unknown action returns error."""
        message = AgentMessage(
            sender="test",
            recipient="task_manager",
            action="task_unknown",
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Unknown task action" in (response.error or "")
