"""Unit tests for storage backends."""

import pytest

from src.backends import InMemoryBackend, StorageBackend
from src.models import NotFoundError, Task


class TestStorageBackendProtocol:
    """Tests for StorageBackend protocol compliance."""

    def test_in_memory_backend_implements_protocol(self) -> None:
        """Test that InMemoryBackend implements StorageBackend protocol."""
        backend = InMemoryBackend()

        assert isinstance(backend, StorageBackend)


class TestInMemoryBackendSave:
    """Tests for InMemoryBackend save operation."""

    @pytest.mark.asyncio
    async def test_save_task(self) -> None:
        """Test saving a task."""
        backend = InMemoryBackend()
        task = Task(title="Test task")

        saved = await backend.save(task)

        assert saved.id == task.id
        assert saved.title == task.title

    @pytest.mark.asyncio
    async def test_save_increments_count(self) -> None:
        """Test that save increases task count."""
        backend = InMemoryBackend()
        task = Task(title="Test task")

        await backend.save(task)

        assert backend.count == 1

    @pytest.mark.asyncio
    async def test_save_multiple_tasks(self) -> None:
        """Test saving multiple tasks."""
        backend = InMemoryBackend()

        await backend.save(Task(title="Task 1"))
        await backend.save(Task(title="Task 2"))
        await backend.save(Task(title="Task 3"))

        assert backend.count == 3


class TestInMemoryBackendGet:
    """Tests for InMemoryBackend get operation."""

    @pytest.mark.asyncio
    async def test_get_existing_task(self) -> None:
        """Test getting an existing task."""
        backend = InMemoryBackend()
        task = Task(title="Test task")
        await backend.save(task)

        retrieved = await backend.get(task.id)

        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.title == task.title

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self) -> None:
        """Test getting a nonexistent task returns None."""
        backend = InMemoryBackend()

        retrieved = await backend.get("nonexistent-id")

        assert retrieved is None


class TestInMemoryBackendGetAll:
    """Tests for InMemoryBackend get_all operation."""

    @pytest.mark.asyncio
    async def test_get_all_empty(self) -> None:
        """Test getting all tasks when empty."""
        backend = InMemoryBackend()

        tasks = await backend.get_all()

        assert tasks == []

    @pytest.mark.asyncio
    async def test_get_all_with_tasks(self) -> None:
        """Test getting all tasks."""
        backend = InMemoryBackend()
        await backend.save(Task(title="Task 1"))
        await backend.save(Task(title="Task 2"))

        tasks = await backend.get_all()

        assert len(tasks) == 2
        titles = {t.title for t in tasks}
        assert titles == {"Task 1", "Task 2"}


class TestInMemoryBackendUpdate:
    """Tests for InMemoryBackend update operation."""

    @pytest.mark.asyncio
    async def test_update_existing_task(self) -> None:
        """Test updating an existing task."""
        backend = InMemoryBackend()
        task = Task(title="Original title")
        await backend.save(task)

        updated_task = task.update(title="Updated title")
        result = await backend.update(updated_task)

        assert result.title == "Updated title"

        # Verify persistence
        retrieved = await backend.get(task.id)
        assert retrieved is not None
        assert retrieved.title == "Updated title"

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self) -> None:
        """Test updating a nonexistent task raises NotFoundError."""
        backend = InMemoryBackend()
        task = Task(title="Test")

        with pytest.raises(NotFoundError) as exc_info:
            await backend.update(task)

        assert task.id in str(exc_info.value)


class TestInMemoryBackendDelete:
    """Tests for InMemoryBackend delete operation."""

    @pytest.mark.asyncio
    async def test_delete_existing_task(self) -> None:
        """Test deleting an existing task."""
        backend = InMemoryBackend()
        task = Task(title="Test")
        await backend.save(task)

        result = await backend.delete(task.id)

        assert result is True
        assert backend.count == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self) -> None:
        """Test deleting a nonexistent task returns False."""
        backend = InMemoryBackend()

        result = await backend.delete("nonexistent-id")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_reduces_count(self) -> None:
        """Test that delete decreases task count."""
        backend = InMemoryBackend()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        await backend.save(task1)
        await backend.save(task2)

        await backend.delete(task1.id)

        assert backend.count == 1


class TestInMemoryBackendQuery:
    """Tests for InMemoryBackend query operation."""

    @pytest.mark.asyncio
    async def test_query_all_no_filter(self) -> None:
        """Test query without filters returns all tasks."""
        backend = InMemoryBackend()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2").mark_complete()
        await backend.save(task1)
        await backend.save(task2)

        tasks = await backend.query()

        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_query_pending_only(self) -> None:
        """Test query with pending filter."""
        backend = InMemoryBackend()
        task1 = Task(title="Pending task")
        task2 = Task(title="Completed task").mark_complete()
        await backend.save(task1)
        await backend.save(task2)

        tasks = await backend.query(status="pending")

        assert len(tasks) == 1
        assert tasks[0].status == "pending"

    @pytest.mark.asyncio
    async def test_query_completed_only(self) -> None:
        """Test query with completed filter."""
        backend = InMemoryBackend()
        task1 = Task(title="Pending task")
        task2 = Task(title="Completed task").mark_complete()
        await backend.save(task1)
        await backend.save(task2)

        tasks = await backend.query(status="completed")

        assert len(tasks) == 1
        assert tasks[0].status == "completed"

    @pytest.mark.asyncio
    async def test_query_empty_result(self) -> None:
        """Test query that matches no tasks."""
        backend = InMemoryBackend()
        task = Task(title="Pending task")
        await backend.save(task)

        tasks = await backend.query(status="completed")

        assert tasks == []


class TestInMemoryBackendClear:
    """Tests for InMemoryBackend clear operation."""

    @pytest.mark.asyncio
    async def test_clear_empty_storage(self) -> None:
        """Test clearing empty storage."""
        backend = InMemoryBackend()

        count = await backend.clear()

        assert count == 0
        assert backend.count == 0

    @pytest.mark.asyncio
    async def test_clear_with_tasks(self) -> None:
        """Test clearing storage with tasks."""
        backend = InMemoryBackend()
        await backend.save(Task(title="Task 1"))
        await backend.save(Task(title="Task 2"))
        await backend.save(Task(title="Task 3"))

        count = await backend.clear()

        assert count == 3
        assert backend.count == 0

    @pytest.mark.asyncio
    async def test_clear_is_idempotent(self) -> None:
        """Test that clearing twice is safe."""
        backend = InMemoryBackend()
        await backend.save(Task(title="Task"))

        await backend.clear()
        count = await backend.clear()

        assert count == 0
