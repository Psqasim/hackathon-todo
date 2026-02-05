"""Unit tests for event models and Dapr publisher."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.events.models import ReminderEvent, TaskEvent
from src.events.publisher import DaprPublisher, get_publisher


class TestTaskEvent:
    """Test cases for TaskEvent model."""

    def test_task_event_creation(self):
        """Test creating a TaskEvent with all required fields."""
        event = TaskEvent(
            event_type="created",
            task_id=123,
            user_id="user_abc123",
            task_data={
                "id": 123,
                "title": "Review PR",
                "is_recurring": True,
            },
        )

        assert event.event_type == "created"
        assert event.task_id == 123
        assert event.user_id == "user_abc123"
        assert event.task_data["title"] == "Review PR"
        assert isinstance(event.timestamp, datetime)

    def test_task_event_with_custom_timestamp(self):
        """Test creating a TaskEvent with custom timestamp."""
        custom_time = datetime(2026, 2, 5, 12, 0, 0)
        event = TaskEvent(
            event_type="updated",
            task_id=456,
            user_id="user_xyz",
            task_data={"title": "Updated task"},
            timestamp=custom_time,
        )

        assert event.timestamp == custom_time

    def test_task_event_serialization(self):
        """Test TaskEvent JSON serialization."""
        event = TaskEvent(
            event_type="completed",
            task_id=789,
            user_id="user_test",
            task_data={"title": "Test task", "completed": True},
        )

        # Serialize to dict (JSON-compatible)
        data = event.model_dump(mode="json")

        assert data["event_type"] == "completed"
        assert data["task_id"] == 789
        assert data["user_id"] == "user_test"
        assert "timestamp" in data

    def test_task_event_event_types(self):
        """Test all valid event types."""
        event_types = ["created", "updated", "completed", "deleted"]

        for event_type in event_types:
            event = TaskEvent(
                event_type=event_type,
                task_id=1,
                user_id="user",
                task_data={},
            )
            assert event.event_type == event_type


class TestReminderEvent:
    """Test cases for ReminderEvent model."""

    def test_reminder_event_creation(self):
        """Test creating a ReminderEvent with all required fields."""
        due_at = datetime(2026, 2, 5, 10, 0, 0)
        remind_at = datetime(2026, 2, 5, 9, 0, 0)

        event = ReminderEvent(
            task_id=123,
            user_id="user_abc",
            title="Review PR",
            due_at=due_at,
            remind_at=remind_at,
        )

        assert event.task_id == 123
        assert event.user_id == "user_abc"
        assert event.title == "Review PR"
        assert event.due_at == due_at
        assert event.remind_at == remind_at
        assert isinstance(event.timestamp, datetime)

    def test_reminder_event_one_hour_before(self):
        """Test reminder is set 1 hour before due time."""
        due_at = datetime.now(UTC) + timedelta(hours=2)
        remind_at = due_at - timedelta(hours=1)

        event = ReminderEvent(
            task_id=456,
            user_id="user_xyz",
            title="Important task",
            due_at=due_at,
            remind_at=remind_at,
        )

        # Verify remind_at is exactly 1 hour before due_at
        time_diff = event.due_at - event.remind_at
        assert time_diff == timedelta(hours=1)

    def test_reminder_event_serialization(self):
        """Test ReminderEvent JSON serialization."""
        due_at = datetime(2026, 2, 5, 10, 0, 0)
        remind_at = datetime(2026, 2, 5, 9, 0, 0)

        event = ReminderEvent(
            task_id=789,
            user_id="user_test",
            title="Test reminder",
            due_at=due_at,
            remind_at=remind_at,
        )

        data = event.model_dump(mode="json")

        assert data["task_id"] == 789
        assert data["user_id"] == "user_test"
        assert data["title"] == "Test reminder"
        assert "due_at" in data
        assert "remind_at" in data
        assert "timestamp" in data


class TestDaprPublisher:
    """Test cases for DaprPublisher."""

    def test_publisher_initialization_disabled(self, monkeypatch):
        """Test publisher initializes with Dapr disabled by default."""
        monkeypatch.setenv("DAPR_ENABLED", "false")
        publisher = DaprPublisher()

        assert publisher.enabled is False
        assert publisher.dapr_port == "3500"
        assert publisher.pubsub_name == "taskflow-pubsub"
        assert publisher.base_url == "http://localhost:3500"

    def test_publisher_initialization_enabled(self, monkeypatch):
        """Test publisher initializes with Dapr enabled."""
        monkeypatch.setenv("DAPR_ENABLED", "true")
        monkeypatch.setenv("DAPR_HTTP_PORT", "4500")
        monkeypatch.setenv("PUBSUB_NAME", "custom-pubsub")

        publisher = DaprPublisher()

        assert publisher.enabled is True
        assert publisher.dapr_port == "4500"
        assert publisher.pubsub_name == "custom-pubsub"
        assert publisher.base_url == "http://localhost:4500"

    @pytest.mark.asyncio
    async def test_publish_when_disabled(self, monkeypatch):
        """Test publish returns False when Dapr is disabled."""
        monkeypatch.setenv("DAPR_ENABLED", "false")
        publisher = DaprPublisher()

        event = TaskEvent(
            event_type="created",
            task_id=1,
            user_id="user",
            task_data={},
        )

        result = await publisher.publish("task-events", event)

        assert result is False

    @pytest.mark.asyncio
    async def test_publish_success(self, monkeypatch):
        """Test successful event publishing to Dapr."""
        monkeypatch.setenv("DAPR_ENABLED", "true")
        publisher = DaprPublisher()

        event = TaskEvent(
            event_type="created",
            task_id=123,
            user_id="user_abc",
            task_data={"title": "Test task"},
        )

        # Mock httpx.AsyncClient
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await publisher.publish("task-events", event)

            assert result is True

    @pytest.mark.asyncio
    async def test_publish_connection_error(self, monkeypatch):
        """Test publish handles connection errors gracefully."""
        monkeypatch.setenv("DAPR_ENABLED", "true")
        publisher = DaprPublisher()

        event = TaskEvent(
            event_type="created",
            task_id=1,
            user_id="user",
            task_data={},
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            result = await publisher.publish("task-events", event)

            assert result is False

    @pytest.mark.asyncio
    async def test_publish_timeout(self, monkeypatch):
        """Test publish handles timeout errors gracefully."""
        monkeypatch.setenv("DAPR_ENABLED", "true")
        publisher = DaprPublisher()

        event = TaskEvent(
            event_type="created",
            task_id=1,
            user_id="user",
            task_data={},
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )

            result = await publisher.publish("task-events", event)

            assert result is False

    @pytest.mark.asyncio
    async def test_publish_task_event_convenience(self, monkeypatch):
        """Test convenience method for publishing task events."""
        monkeypatch.setenv("DAPR_ENABLED", "true")
        publisher = DaprPublisher()

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await publisher.publish_task_event(
                event_type="created",
                task_id=123,
                user_id="user_abc",
                task_data={"title": "Test task"},
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_publish_reminder_event_convenience(self, monkeypatch):
        """Test convenience method for publishing reminder events."""
        monkeypatch.setenv("DAPR_ENABLED", "true")
        publisher = DaprPublisher()

        due_at = datetime(2026, 2, 5, 10, 0, 0)
        remind_at = datetime(2026, 2, 5, 9, 0, 0)

        mock_response = Mock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await publisher.publish_reminder_event(
                task_id=456,
                user_id="user_xyz",
                title="Important task",
                due_at=due_at,
                remind_at=remind_at,
            )

            assert result is True

    def test_get_publisher_singleton(self):
        """Test get_publisher returns singleton instance."""
        publisher1 = get_publisher()
        publisher2 = get_publisher()

        assert publisher1 is publisher2
