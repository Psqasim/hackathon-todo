"""Unit tests for Task model."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.models.tasks import Task


class TestTaskCreation:
    """Tests for Task model creation and validation."""

    def test_create_task_with_title_only(self) -> None:
        """Test creating a task with only required title."""
        task = Task(title="Buy groceries")

        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == "pending"
        assert task.completed_at is None
        assert task.id  # Should be auto-generated
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_with_all_fields(self) -> None:
        """Test creating a task with all fields."""
        task = Task(
            title="Buy groceries",
            description="Milk, eggs, bread",
        )

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_task_strips_title_whitespace(self) -> None:
        """Test that title whitespace is stripped."""
        task = Task(title="  Buy groceries  ")

        assert task.title == "Buy groceries"

    def test_task_strips_description_whitespace(self) -> None:
        """Test that description whitespace is stripped."""
        task = Task(title="Test", description="  Some description  ")

        assert task.description == "Some description"

    def test_task_rejects_empty_title(self) -> None:
        """Test that empty title is rejected."""
        with pytest.raises(PydanticValidationError):
            Task(title="")

    def test_task_rejects_whitespace_only_title(self) -> None:
        """Test that whitespace-only title is rejected."""
        with pytest.raises(PydanticValidationError):
            Task(title="   ")

    def test_task_rejects_title_too_long(self) -> None:
        """Test that title exceeding 200 characters is rejected."""
        with pytest.raises(PydanticValidationError):
            Task(title="x" * 201)

    def test_task_accepts_max_length_title(self) -> None:
        """Test that title at exactly 200 characters is accepted."""
        task = Task(title="x" * 200)

        assert len(task.title) == 200

    def test_task_rejects_description_too_long(self) -> None:
        """Test that description exceeding 1000 characters is rejected."""
        with pytest.raises(PydanticValidationError):
            Task(title="Test", description="x" * 1001)

    def test_task_accepts_max_length_description(self) -> None:
        """Test that description at exactly 1000 characters is accepted."""
        task = Task(title="Test", description="x" * 1000)

        assert len(task.description or "") == 1000

    def test_whitespace_only_description_becomes_none(self) -> None:
        """Test that whitespace-only description is converted to None."""
        task = Task(title="Test", description="   ")

        assert task.description is None

    def test_task_id_is_unique(self) -> None:
        """Test that each task gets a unique ID."""
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        assert task1.id != task2.id


class TestTaskStatusMethods:
    """Tests for Task status transition methods."""

    def test_mark_complete(self) -> None:
        """Test marking a task as complete."""
        task = Task(title="Test task")
        completed = task.mark_complete()

        assert completed.status == "completed"
        assert completed.completed_at is not None
        assert completed.id == task.id
        assert completed.title == task.title

    def test_mark_complete_updates_timestamp(self) -> None:
        """Test that mark_complete updates the updated_at timestamp."""
        task = Task(title="Test task")
        original_updated = task.updated_at

        completed = task.mark_complete()

        assert completed.updated_at >= original_updated

    def test_mark_pending(self) -> None:
        """Test marking a completed task as pending."""
        task = Task(title="Test task")
        completed = task.mark_complete()
        pending = completed.mark_pending()

        assert pending.status == "pending"
        assert pending.completed_at is None

    def test_mark_pending_preserves_id(self) -> None:
        """Test that mark_pending preserves the task ID."""
        task = Task(title="Test task")
        completed = task.mark_complete()
        pending = completed.mark_pending()

        assert pending.id == task.id

    def test_original_task_unchanged_after_complete(self) -> None:
        """Test that original task is not mutated by mark_complete."""
        task = Task(title="Test task")
        _ = task.mark_complete()

        assert task.status == "pending"
        assert task.completed_at is None


class TestTaskUpdate:
    """Tests for Task update method."""

    def test_update_title(self) -> None:
        """Test updating task title."""
        task = Task(title="Original title")
        updated = task.update(title="New title")

        assert updated.title == "New title"
        assert updated.id == task.id

    def test_update_description(self) -> None:
        """Test updating task description."""
        task = Task(title="Test", description="Original")
        updated = task.update(description="New description")

        assert updated.description == "New description"
        assert updated.title == task.title

    def test_update_both_fields(self) -> None:
        """Test updating both title and description."""
        task = Task(title="Original", description="Old desc")
        updated = task.update(title="New title", description="New desc")

        assert updated.title == "New title"
        assert updated.description == "New desc"

    def test_update_timestamp(self) -> None:
        """Test that update changes the updated_at timestamp."""
        task = Task(title="Test")
        original_updated = task.updated_at

        updated = task.update(title="New title")

        assert updated.updated_at >= original_updated

    def test_original_task_unchanged_after_update(self) -> None:
        """Test that original task is not mutated by update."""
        task = Task(title="Original")
        _ = task.update(title="New")

        assert task.title == "Original"


class TestTaskTimestamps:
    """Tests for Task timestamp handling."""

    def test_created_at_is_utc(self) -> None:
        """Test that created_at is in UTC."""
        task = Task(title="Test")

        assert task.created_at.tzinfo == UTC

    def test_updated_at_is_utc(self) -> None:
        """Test that updated_at is in UTC."""
        task = Task(title="Test")

        assert task.updated_at.tzinfo == UTC

    def test_completed_at_is_utc(self) -> None:
        """Test that completed_at is in UTC when set."""
        task = Task(title="Test").mark_complete()

        assert task.completed_at is not None
        assert task.completed_at.tzinfo == UTC
