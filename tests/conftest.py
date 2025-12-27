"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_task_data() -> dict[str, str]:
    """Return sample data for creating a task."""
    return {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
    }


@pytest.fixture
def sample_message_data() -> dict[str, str]:
    """Return sample data for creating an agent message."""
    return {
        "sender": "orchestrator",
        "recipient": "task_manager",
        "action": "task_add",
    }
