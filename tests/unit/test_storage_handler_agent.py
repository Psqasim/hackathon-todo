"""Unit tests for StorageHandlerAgent."""

import pytest

from src.agents import StorageHandlerAgent
from src.backends import InMemoryBackend
from src.models import AgentMessage, Task


@pytest.fixture
def backend() -> InMemoryBackend:
    """Create a fresh in-memory backend."""
    return InMemoryBackend()


@pytest.fixture
def agent(backend: InMemoryBackend) -> StorageHandlerAgent:
    """Create a storage handler agent."""
    return StorageHandlerAgent(backend)


class TestStorageHandlerAgentInit:
    """Tests for StorageHandlerAgent initialization."""

    def test_registers_all_actions(self, agent: StorageHandlerAgent) -> None:
        """Test that all storage actions are registered."""
        expected_actions = [
            "storage_save",
            "storage_get",
            "storage_get_all",
            "storage_update",
            "storage_delete",
            "storage_query",
            "storage_clear",
        ]
        for action in expected_actions:
            assert action in agent.supported_actions


class TestStorageHandlerSave:
    """Tests for storage_save action."""

    @pytest.mark.asyncio
    async def test_save_task_from_dict(self, agent: StorageHandlerAgent) -> None:
        """Test saving a task from dict payload."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_save",
            payload={"task": {"title": "Test task"}},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["title"] == "Test task"

    @pytest.mark.asyncio
    async def test_save_task_from_model(self, agent: StorageHandlerAgent) -> None:
        """Test saving a task from Task model."""
        task = Task(title="Test task")
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_save",
            payload={"task": task},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"

    @pytest.mark.asyncio
    async def test_save_missing_task_returns_error(self, agent: StorageHandlerAgent) -> None:
        """Test that missing task in payload returns error."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_save",
            payload={},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Missing 'task'" in (response.error or "")


class TestStorageHandlerGet:
    """Tests for storage_get action."""

    @pytest.mark.asyncio
    async def test_get_existing_task(
        self,
        agent: StorageHandlerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test getting an existing task."""
        task = Task(title="Test")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_get",
            payload={"task_id": task.id},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["id"] == task.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, agent: StorageHandlerAgent) -> None:
        """Test getting a nonexistent task returns error."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_get",
            payload={"task_id": "nonexistent"},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "not found" in (response.error or "").lower()

    @pytest.mark.asyncio
    async def test_get_missing_task_id(self, agent: StorageHandlerAgent) -> None:
        """Test that missing task_id returns error."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_get",
            payload={},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Missing 'task_id'" in (response.error or "")


class TestStorageHandlerGetAll:
    """Tests for storage_get_all action."""

    @pytest.mark.asyncio
    async def test_get_all_empty(self, agent: StorageHandlerAgent) -> None:
        """Test getting all tasks when empty."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_get_all",
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["tasks"] == []

    @pytest.mark.asyncio
    async def test_get_all_with_tasks(
        self,
        agent: StorageHandlerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test getting all tasks."""
        await backend.save(Task(title="Task 1"))
        await backend.save(Task(title="Task 2"))

        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_get_all",
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert len(response.result["tasks"]) == 2


class TestStorageHandlerUpdate:
    """Tests for storage_update action."""

    @pytest.mark.asyncio
    async def test_update_existing_task(
        self,
        agent: StorageHandlerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test updating an existing task."""
        task = Task(title="Original")
        await backend.save(task)

        updated = task.update(title="Updated")
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_update",
            payload={"task": updated.model_dump()},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["task"]["title"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self, agent: StorageHandlerAgent) -> None:
        """Test updating a nonexistent task returns error."""
        task = Task(title="Test")
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_update",
            payload={"task": task.model_dump()},
        )

        response = await agent.handle_message(message)

        assert response.status == "error"


class TestStorageHandlerDelete:
    """Tests for storage_delete action."""

    @pytest.mark.asyncio
    async def test_delete_existing_task(
        self,
        agent: StorageHandlerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test deleting an existing task."""
        task = Task(title="To delete")
        await backend.save(task)

        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_delete",
            payload={"task_id": task.id},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["deleted"] is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, agent: StorageHandlerAgent) -> None:
        """Test deleting a nonexistent task."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_delete",
            payload={"task_id": "nonexistent"},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["deleted"] is False


class TestStorageHandlerQuery:
    """Tests for storage_query action."""

    @pytest.mark.asyncio
    async def test_query_with_status_filter(
        self,
        agent: StorageHandlerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test querying with status filter."""
        await backend.save(Task(title="Pending"))
        await backend.save(Task(title="Completed").mark_complete())

        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_query",
            payload={"status": "pending"},
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["count"] == 1


class TestStorageHandlerClear:
    """Tests for storage_clear action."""

    @pytest.mark.asyncio
    async def test_clear_storage(
        self,
        agent: StorageHandlerAgent,
        backend: InMemoryBackend,
    ) -> None:
        """Test clearing all tasks."""
        await backend.save(Task(title="Task 1"))
        await backend.save(Task(title="Task 2"))

        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_clear",
        )

        response = await agent.handle_message(message)

        assert response.status == "success"
        assert response.result["cleared"] == 2


class TestStorageHandlerUnknownAction:
    """Tests for unknown action handling."""

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self, agent: StorageHandlerAgent) -> None:
        """Test that unknown action returns error."""
        message = AgentMessage(
            sender="test",
            recipient="storage_handler",
            action="storage_unknown",
        )

        response = await agent.handle_message(message)

        assert response.status == "error"
        assert "Unknown storage action" in (response.error or "")
