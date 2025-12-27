"""
Agent communication message models.

Defines the message protocol for inter-agent communication.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class AgentMessage(BaseModel):
    """
    Message sent between agents.

    Attributes:
        request_id: Unique identifier for this request (UUID4).
        sender: Name of the sending agent.
        recipient: Name of the receiving agent.
        action: The action to perform (e.g., 'task_add', 'storage_save').
        payload: Action-specific data.
        timestamp: When the message was created.
        correlation_id: ID for tracing related messages across agents.
    """

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str = Field(..., min_length=1)
    recipient: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))

    @field_validator("sender", "recipient", "action")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        """Ensure string fields are not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace-only")
        return v.strip()

    model_config = {"frozen": False, "extra": "forbid"}


class AgentResponse(BaseModel):
    """
    Response from an agent after processing a message.

    Attributes:
        request_id: ID of the original request.
        sender: Name of the responding agent.
        status: 'success' or 'error'.
        result: Result data if successful.
        error: Error message if failed.
        timestamp: When the response was created.
    """

    request_id: str = Field(..., min_length=1)
    sender: str = Field(..., min_length=1)
    status: Literal["success", "error"]
    result: Any | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_result_xor_error(self) -> AgentResponse:
        """Ensure result XOR error based on status."""
        if self.status == "success":
            if self.error is not None:
                raise ValueError("Success response should not have an error")
        elif self.status == "error":
            if self.error is None:
                raise ValueError("Error response must have an error message")
            if self.result is not None:
                raise ValueError("Error response should not have a result")
        return self

    model_config = {"frozen": False, "extra": "forbid"}


class AgentInfo(BaseModel):
    """
    Information about a registered agent.

    Attributes:
        name: Unique identifier for the agent.
        status: Current operational status.
        version: Semantic version string (e.g., '1.0.0').
        supported_actions: List of actions this agent can handle.
    """

    name: str = Field(..., min_length=1)
    status: Literal["active", "inactive", "error"] = "inactive"
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    supported_actions: list[str] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def validate_semver(cls, v: str) -> str:
        """Validate semantic version format."""
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(f"Version must be in semver format (x.y.z), got: {v}")
        return v

    model_config = {"frozen": False, "extra": "forbid"}
