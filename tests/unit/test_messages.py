"""Unit tests for agent message models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.models.messages import AgentInfo, AgentMessage, AgentResponse


class TestAgentMessage:
    """Tests for AgentMessage model."""

    def test_create_message_with_required_fields(self) -> None:
        """Test creating a message with only required fields."""
        msg = AgentMessage(
            sender="orchestrator",
            recipient="task_manager",
            action="task_add",
        )

        assert msg.sender == "orchestrator"
        assert msg.recipient == "task_manager"
        assert msg.action == "task_add"
        assert msg.payload == {}
        assert msg.request_id  # Should be auto-generated
        assert msg.correlation_id  # Should be auto-generated
        assert isinstance(msg.timestamp, datetime)

    def test_create_message_with_payload(self) -> None:
        """Test creating a message with payload data."""
        payload = {"title": "Buy groceries", "description": "Milk, eggs, bread"}
        msg = AgentMessage(
            sender="ui_controller",
            recipient="orchestrator",
            action="task_add",
            payload=payload,
        )

        assert msg.payload == payload

    def test_message_strips_whitespace(self) -> None:
        """Test that string fields are stripped of whitespace."""
        msg = AgentMessage(
            sender="  orchestrator  ",
            recipient="  task_manager  ",
            action="  task_add  ",
        )

        assert msg.sender == "orchestrator"
        assert msg.recipient == "task_manager"
        assert msg.action == "task_add"

    def test_message_rejects_empty_sender(self) -> None:
        """Test that empty sender is rejected."""
        with pytest.raises(PydanticValidationError):
            AgentMessage(
                sender="",
                recipient="task_manager",
                action="task_add",
            )

    def test_message_rejects_whitespace_only_sender(self) -> None:
        """Test that whitespace-only sender is rejected."""
        with pytest.raises(PydanticValidationError):
            AgentMessage(
                sender="   ",
                recipient="task_manager",
                action="task_add",
            )

    def test_message_rejects_empty_recipient(self) -> None:
        """Test that empty recipient is rejected."""
        with pytest.raises(PydanticValidationError):
            AgentMessage(
                sender="orchestrator",
                recipient="",
                action="task_add",
            )

    def test_message_rejects_empty_action(self) -> None:
        """Test that empty action is rejected."""
        with pytest.raises(PydanticValidationError):
            AgentMessage(
                sender="orchestrator",
                recipient="task_manager",
                action="",
            )

    def test_message_request_id_is_unique(self) -> None:
        """Test that each message gets a unique request_id."""
        msg1 = AgentMessage(
            sender="orchestrator",
            recipient="task_manager",
            action="task_add",
        )
        msg2 = AgentMessage(
            sender="orchestrator",
            recipient="task_manager",
            action="task_add",
        )

        assert msg1.request_id != msg2.request_id

    def test_message_rejects_extra_fields(self) -> None:
        """Test that extra fields are rejected."""
        with pytest.raises(PydanticValidationError):
            AgentMessage(
                sender="orchestrator",
                recipient="task_manager",
                action="task_add",
                extra_field="not_allowed",  # type: ignore[call-arg]
            )


class TestAgentResponse:
    """Tests for AgentResponse model."""

    def test_create_success_response(self) -> None:
        """Test creating a success response."""
        response = AgentResponse(
            request_id="test-123",
            sender="task_manager",
            status="success",
            result={"task_id": "abc-123"},
        )

        assert response.status == "success"
        assert response.result == {"task_id": "abc-123"}
        assert response.error is None

    def test_create_error_response(self) -> None:
        """Test creating an error response."""
        response = AgentResponse(
            request_id="test-123",
            sender="task_manager",
            status="error",
            error="Task not found",
        )

        assert response.status == "error"
        assert response.error == "Task not found"
        assert response.result is None

    def test_success_response_rejects_error(self) -> None:
        """Test that success response cannot have error field."""
        with pytest.raises(PydanticValidationError):
            AgentResponse(
                request_id="test-123",
                sender="task_manager",
                status="success",
                result={"data": "value"},
                error="This should fail",
            )

    def test_error_response_requires_error_message(self) -> None:
        """Test that error response must have error message."""
        with pytest.raises(PydanticValidationError):
            AgentResponse(
                request_id="test-123",
                sender="task_manager",
                status="error",
            )

    def test_error_response_rejects_result(self) -> None:
        """Test that error response cannot have result field."""
        with pytest.raises(PydanticValidationError):
            AgentResponse(
                request_id="test-123",
                sender="task_manager",
                status="error",
                error="Some error",
                result={"data": "value"},
            )

    def test_response_timestamp_auto_generated(self) -> None:
        """Test that timestamp is auto-generated."""
        response = AgentResponse(
            request_id="test-123",
            sender="task_manager",
            status="success",
            result=None,
        )

        assert isinstance(response.timestamp, datetime)
        assert response.timestamp.tzinfo == UTC


class TestAgentInfo:
    """Tests for AgentInfo model."""

    def test_create_agent_info(self) -> None:
        """Test creating agent info with all fields."""
        info = AgentInfo(
            name="task_manager",
            status="active",
            version="1.0.0",
            supported_actions=["task_add", "task_list", "task_complete"],
        )

        assert info.name == "task_manager"
        assert info.status == "active"
        assert info.version == "1.0.0"
        assert info.supported_actions == ["task_add", "task_list", "task_complete"]

    def test_agent_info_defaults(self) -> None:
        """Test that agent info has correct defaults."""
        info = AgentInfo(name="test_agent", version="1.0.0")

        assert info.status == "inactive"
        assert info.supported_actions == []

    def test_valid_semver_versions(self) -> None:
        """Test various valid semantic version formats."""
        valid_versions = ["0.0.1", "1.0.0", "2.10.100", "123.456.789"]

        for version in valid_versions:
            info = AgentInfo(name="test", version=version)
            assert info.version == version

    def test_invalid_semver_versions(self) -> None:
        """Test that invalid version formats are rejected."""
        invalid_versions = [
            "1.0",
            "1",
            "v1.0.0",
            "1.0.0-alpha",
            "1.0.0.0",
            "a.b.c",
            "",
        ]

        for version in invalid_versions:
            with pytest.raises(PydanticValidationError):
                AgentInfo(name="test", version=version)

    def test_agent_info_status_values(self) -> None:
        """Test valid status values."""
        for status in ["active", "inactive", "error"]:
            info = AgentInfo(name="test", version="1.0.0", status=status)  # type: ignore[arg-type]
            assert info.status == status

    def test_agent_info_invalid_status(self) -> None:
        """Test that invalid status is rejected."""
        with pytest.raises(PydanticValidationError):
            AgentInfo(name="test", version="1.0.0", status="unknown")  # type: ignore[arg-type]
