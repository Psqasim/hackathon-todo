"""
Pydantic models for chat functionality.

This module provides API request/response schemas for the chat interface.
Chat history is managed by OpenAI's Conversations API (NOT stored in PostgreSQL).

Architecture:
- PostgreSQL stores ONLY: Users, Tasks
- Chat history stored in OpenAI Conversations API via SDK sessions
- Backend remains stateless
- Frontend stores only conversation_id for continuity
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


# =============================================================================
# API Request/Response Models (Pydantic)
# =============================================================================


class ToolCall(BaseModel):
    """MCP tool invocation details."""

    id: str = Field(description="Unique identifier for the tool call")
    tool_name: str = Field(description="Name of the MCP tool called")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    result: dict[str, Any] | None = Field(default=None, description="Tool execution result")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChatMessage(BaseModel):
    """Single message in chat."""

    id: str = Field(default_factory=generate_uuid)
    role: Literal["user", "assistant", "system"] = Field(description="Message sender role")
    content: str = Field(description="Message text content")
    tool_calls: list[ToolCall] | None = Field(default=None, description="Tool calls if any")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    conversation_id: str | None = Field(
        default=None,
        description="OpenAI conversation ID to resume existing conversation"
    )


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    conversation_id: str = Field(description="OpenAI conversation ID for continuity")
    message: ChatMessage = Field(description="Assistant response message")


# =============================================================================
# Conversation List Models (for frontend sidebar)
# Note: These are populated from OpenAI Conversations API, NOT from PostgreSQL
# =============================================================================


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing in sidebar."""

    id: str = Field(description="OpenAI conversation ID")
    title: str | None = Field(default=None, description="First message preview as title")
    created_at: datetime = Field(description="When conversation started")
    updated_at: datetime = Field(description="Last message timestamp")
    message_count: int = Field(default=0, description="Number of messages")


class ConversationDetail(BaseModel):
    """Full conversation with messages from OpenAI API."""

    id: str = Field(description="OpenAI conversation ID")
    title: str | None = Field(default=None)
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessage] = Field(default_factory=list)


class ConversationListResponse(BaseModel):
    """Response for listing conversations."""

    conversations: list[ConversationSummary] = Field(default_factory=list)
    total: int = Field(default=0)


class DeleteResponse(BaseModel):
    """Response for delete operations."""

    deleted: bool = Field(default=True)
    id: str = Field(description="Deleted resource ID")


# =============================================================================
# SSE Stream Event Models
# =============================================================================


class StreamEventBase(BaseModel):
    """Base class for SSE stream events."""

    event: str = Field(description="Event type")


class MessageStartEvent(StreamEventBase):
    """Event sent at start of message generation."""

    event: Literal["message_start"] = "message_start"
    conversation_id: str
    message_id: str


class ContentDeltaEvent(StreamEventBase):
    """Event for streaming content chunks."""

    event: Literal["content_delta"] = "content_delta"
    delta: str = Field(description="Content chunk")


class ToolCallEvent(StreamEventBase):
    """Event when a tool is called."""

    event: Literal["tool_call"] = "tool_call"
    tool_name: str
    parameters: dict[str, Any]


class ToolResultEvent(StreamEventBase):
    """Event with tool execution result."""

    event: Literal["tool_result"] = "tool_result"
    tool_name: str
    result: dict[str, Any]
    success: bool


class MessageEndEvent(StreamEventBase):
    """Event sent when message is complete."""

    event: Literal["message_end"] = "message_end"
    full_content: str
    tool_calls_count: int = 0


class ErrorEvent(StreamEventBase):
    """Event sent on error."""

    event: Literal["error"] = "error"
    code: str
    message: str


# Export all models
__all__ = [
    # Request/Response
    "ChatRequest",
    "ChatResponse",
    "ChatMessage",
    "ToolCall",
    "ConversationSummary",
    "ConversationDetail",
    "ConversationListResponse",
    "DeleteResponse",
    # Stream Events
    "MessageStartEvent",
    "ContentDeltaEvent",
    "ToolCallEvent",
    "ToolResultEvent",
    "MessageEndEvent",
    "ErrorEvent",
    # Utils
    "generate_uuid",
]
