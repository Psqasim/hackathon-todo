"""Unit tests for exception hierarchy."""

import pytest

from src.models.exceptions import (
    AgentError,
    AgentInitError,
    NotFoundError,
    RoutingError,
    StorageError,
    ValidationError,
)


class TestAgentError:
    """Tests for base AgentError exception."""

    def test_create_basic_error(self) -> None:
        """Test creating a basic agent error."""
        error = AgentError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.agent_name is None

    def test_create_error_with_agent_name(self) -> None:
        """Test creating an error with agent context."""
        error = AgentError("Something went wrong", agent_name="task_manager")

        assert str(error) == "[task_manager] Something went wrong"
        assert error.agent_name == "task_manager"

    def test_error_is_exception(self) -> None:
        """Test that AgentError can be raised and caught."""
        with pytest.raises(AgentError) as exc_info:
            raise AgentError("Test error")

        assert "Test error" in str(exc_info.value)


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_create_validation_error(self) -> None:
        """Test creating a validation error."""
        error = ValidationError("Invalid value")

        assert "Invalid value" in str(error)
        assert error.field is None

    def test_create_validation_error_with_field(self) -> None:
        """Test creating a validation error with field context."""
        error = ValidationError("Cannot be empty", field="title")

        assert "Cannot be empty" in str(error)
        assert "(field: title)" in str(error)
        assert error.field == "title"

    def test_create_validation_error_with_agent(self) -> None:
        """Test creating a validation error with agent and field."""
        error = ValidationError(
            "Cannot be empty",
            field="title",
            agent_name="task_manager",
        )

        assert "[task_manager]" in str(error)
        assert "(field: title)" in str(error)

    def test_validation_error_inherits_from_agent_error(self) -> None:
        """Test that ValidationError is an AgentError."""
        error = ValidationError("Test")

        assert isinstance(error, AgentError)


class TestNotFoundError:
    """Tests for NotFoundError exception."""

    def test_create_not_found_error(self) -> None:
        """Test creating a not found error."""
        error = NotFoundError("Resource not found")

        assert "Resource not found" in str(error)

    def test_create_not_found_error_with_resource_info(self) -> None:
        """Test creating a not found error with resource context."""
        error = NotFoundError(
            "Not found",
            resource_type="task",
            resource_id="abc-123",
        )

        assert "Not found" in str(error)
        assert "type=task" in str(error)
        assert "id=abc-123" in str(error)

    def test_create_not_found_error_with_type_only(self) -> None:
        """Test creating a not found error with only resource type."""
        error = NotFoundError("Not found", resource_type="task")

        assert "(type=task)" in str(error)

    def test_not_found_error_inherits_from_agent_error(self) -> None:
        """Test that NotFoundError is an AgentError."""
        error = NotFoundError("Test")

        assert isinstance(error, AgentError)


class TestStorageError:
    """Tests for StorageError exception."""

    def test_create_storage_error(self) -> None:
        """Test creating a storage error."""
        error = StorageError("Failed to save")

        assert "Failed to save" in str(error)
        assert error.operation is None

    def test_create_storage_error_with_operation(self) -> None:
        """Test creating a storage error with operation context."""
        error = StorageError("Failed", operation="save")

        assert "Failed" in str(error)
        assert "(operation: save)" in str(error)
        assert error.operation == "save"

    def test_create_storage_error_with_agent(self) -> None:
        """Test creating a storage error with agent context."""
        error = StorageError(
            "Failed to save",
            operation="save",
            agent_name="storage_handler",
        )

        assert "[storage_handler]" in str(error)
        assert "(operation: save)" in str(error)

    def test_storage_error_inherits_from_agent_error(self) -> None:
        """Test that StorageError is an AgentError."""
        error = StorageError("Test")

        assert isinstance(error, AgentError)


class TestRoutingError:
    """Tests for RoutingError exception."""

    def test_create_routing_error(self) -> None:
        """Test creating a routing error."""
        error = RoutingError("Unknown route")

        assert "Unknown route" in str(error)
        assert error.action is None

    def test_create_routing_error_with_action(self) -> None:
        """Test creating a routing error with action context."""
        error = RoutingError("Unknown route", action="unknown_action")

        assert "Unknown route" in str(error)
        assert "(action: unknown_action)" in str(error)
        assert error.action == "unknown_action"

    def test_create_routing_error_with_agent(self) -> None:
        """Test creating a routing error with agent context."""
        error = RoutingError(
            "Route not found",
            action="task_add",
            agent_name="orchestrator",
        )

        assert "[orchestrator]" in str(error)
        assert "(action: task_add)" in str(error)

    def test_routing_error_inherits_from_agent_error(self) -> None:
        """Test that RoutingError is an AgentError."""
        error = RoutingError("Test")

        assert isinstance(error, AgentError)


class TestAgentInitError:
    """Tests for AgentInitError exception."""

    def test_create_init_error(self) -> None:
        """Test creating an init error."""
        error = AgentInitError("Failed to initialize")

        assert "Failed to initialize" in str(error)

    def test_create_init_error_with_agent(self) -> None:
        """Test creating an init error with agent context."""
        error = AgentInitError(
            "Missing dependency",
            agent_name="task_manager",
        )

        assert "[task_manager] Missing dependency" in str(error)

    def test_init_error_inherits_from_agent_error(self) -> None:
        """Test that AgentInitError is an AgentError."""
        error = AgentInitError("Test")

        assert isinstance(error, AgentError)


class TestExceptionHierarchy:
    """Tests for the exception hierarchy relationships."""

    def test_all_exceptions_catchable_as_agent_error(self) -> None:
        """Test that all custom exceptions can be caught as AgentError."""
        exceptions = [
            ValidationError("test"),
            NotFoundError("test"),
            StorageError("test"),
            RoutingError("test"),
            AgentInitError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, AgentError)

    def test_all_exceptions_catchable_as_exception(self) -> None:
        """Test that all custom exceptions can be caught as Exception."""
        exceptions = [
            AgentError("test"),
            ValidationError("test"),
            NotFoundError("test"),
            StorageError("test"),
            RoutingError("test"),
            AgentInitError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)
