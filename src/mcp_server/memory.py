"""
Conversation history management.

This module provides conversation memory:
- In-memory storage for current session
- Database persistence for long-term storage
- Context tracking for follow-up questions

FR-014: Agent MUST maintain conversation history (last 10 messages minimum)
FR-030: System MUST store conversation history in PostgreSQL database
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog
from sqlmodel import Session, select

from src.db import get_engine
from src.models.chat import ConversationDB, MessageDB

logger = structlog.get_logger()

# Maximum messages to keep in context window
MAX_CONTEXT_MESSAGES = 10


@dataclass
class ConversationContext:
    """Context for tracking conversation state.

    Stores information about recent operations for
    handling follow-up questions like "mark that done".
    """

    last_task_ids: list[str] = field(default_factory=list)
    last_operation: str | None = None
    last_operation_time: datetime | None = None

    def set_task_context(self, task_ids: list[str], operation: str) -> None:
        """Update context after a task operation.

        Args:
            task_ids: Task IDs involved in the operation
            operation: Operation type (create, list, update, etc.)
        """
        self.last_task_ids = task_ids[-5:]  # Keep last 5 task IDs
        self.last_operation = operation
        self.last_operation_time = datetime.now(UTC)
        logger.debug(
            "context_updated",
            task_ids=task_ids[:3],  # Log first 3
            operation=operation,
        )

    def get_last_task_id(self) -> str | None:
        """Get the most recently mentioned task ID."""
        if self.last_task_ids:
            return self.last_task_ids[-1]
        return None

    def clear(self) -> None:
        """Clear the context."""
        self.last_task_ids = []
        self.last_operation = None
        self.last_operation_time = None


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None  # For tool responses
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI API message format."""
        msg: dict[str, Any] = {
            "role": self.role,
            "content": self.content,
        }

        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls

        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id

        if self.name and self.role == "tool":
            msg["name"] = self.name

        return msg


@dataclass
class Conversation:
    """A conversation session with history and context."""

    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    title: str | None = None
    messages: list[Message] = field(default_factory=list)
    context: ConversationContext = field(default_factory=ConversationContext)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.

        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

        # Auto-generate title from first user message
        if self.title is None and message.role == "user":
            self.title = message.content[:50]
            if len(message.content) > 50:
                self.title += "..."

        logger.debug(
            "message_added",
            conversation_id=self.id,
            role=message.role,
            message_count=len(self.messages),
        )

    def add_user_message(self, content: str) -> Message:
        """Add a user message.

        Args:
            content: Message content

        Returns:
            The created message
        """
        message = Message(role="user", content=content)
        self.add_message(message)
        return message

    def add_assistant_message(
        self,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> Message:
        """Add an assistant message.

        Args:
            content: Message content
            tool_calls: Optional tool calls made

        Returns:
            The created message
        """
        message = Message(role="assistant", content=content, tool_calls=tool_calls)
        self.add_message(message)
        return message

    def add_tool_message(
        self,
        tool_call_id: str,
        name: str,
        content: str,
    ) -> Message:
        """Add a tool response message.

        Args:
            tool_call_id: ID of the tool call being responded to
            name: Name of the tool
            content: Tool response content

        Returns:
            The created message
        """
        message = Message(
            role="tool",
            content=content,
            tool_call_id=tool_call_id,
            name=name,
        )
        self.add_message(message)
        return message

    def get_history_for_api(self, max_messages: int = MAX_CONTEXT_MESSAGES) -> list[dict[str, Any]]:
        """Get message history in OpenAI API format.

        Args:
            max_messages: Maximum number of messages to return

        Returns:
            List of messages in OpenAI format
        """
        # Get the last N messages
        recent_messages = self.messages[-max_messages:]
        return [msg.to_openai_format() for msg in recent_messages]

    def clear_history(self) -> None:
        """Clear all messages but keep context."""
        self.messages = []
        self.updated_at = datetime.now(UTC)


class ConversationMemory:
    """Persistent storage for conversation sessions.

    Manages conversations with database persistence and in-memory caching.
    FR-030: Store conversation history in PostgreSQL database
    """

    def __init__(self, max_cache_size: int = 100):
        """Initialize the memory store.

        Args:
            max_cache_size: Maximum conversations to keep in memory cache
        """
        self._cache: dict[str, Conversation] = {}
        self._max_cache_size = max_cache_size

    def get_or_create(
        self,
        conversation_id: str | None,
        user_id: str,
    ) -> Conversation:
        """Get existing conversation or create new one.

        Args:
            conversation_id: Optional existing conversation ID
            user_id: User ID for ownership

        Returns:
            Conversation instance
        """
        # Check in-memory cache first
        if conversation_id and conversation_id in self._cache:
            conversation = self._cache[conversation_id]
            if conversation.user_id == user_id:
                logger.debug(
                    "conversation_retrieved_from_cache",
                    conversation_id=conversation_id,
                    message_count=len(conversation.messages),
                )
                return conversation

        # Try loading from database
        if conversation_id:
            conversation = self._load_from_db(conversation_id, user_id)
            if conversation:
                self._cache[conversation.id] = conversation
                return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        self._save_to_db(conversation)
        self._cache[conversation.id] = conversation

        # Cleanup cache if needed
        self._cleanup_cache_if_needed()

        logger.info(
            "conversation_created",
            conversation_id=conversation.id,
            user_id=user_id,
        )

        return conversation

    def get(self, conversation_id: str) -> Conversation | None:
        """Get a conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation or None if not found
        """
        if conversation_id in self._cache:
            return self._cache[conversation_id]

        # Try loading from database
        engine = get_engine()
        with Session(engine) as session:
            conv_db = session.exec(
                select(ConversationDB).where(ConversationDB.id == conversation_id)
            ).first()

            if conv_db:
                conversation = self._db_to_conversation(conv_db, session)
                self._cache[conversation_id] = conversation
                return conversation

        return None

    def save_message(self, conversation: Conversation, message: Message) -> None:
        """Save a message to the database.

        Args:
            conversation: The conversation
            message: The message to save
        """
        engine = get_engine()
        with Session(engine) as session:
            # Update conversation's updated_at
            conv_db = session.exec(
                select(ConversationDB).where(ConversationDB.id == conversation.id)
            ).first()

            if conv_db:
                conv_db.updated_at = datetime.now(UTC)
                if conv_db.title is None and message.role == "user":
                    conv_db.title = message.content[:50]
                    if len(message.content) > 50:
                        conv_db.title += "..."
                session.add(conv_db)

            # Save message
            msg_db = MessageDB(
                conversation_id=conversation.id,
                role=message.role,
                content=message.content,
                tool_calls=message.tool_calls,
            )
            session.add(msg_db)
            session.commit()

            logger.debug(
                "message_saved_to_db",
                conversation_id=conversation.id,
                role=message.role,
            )

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        # Remove from cache
        if conversation_id in self._cache:
            del self._cache[conversation_id]

        # Delete from database (messages will be deleted via API)
        logger.info("conversation_deleted", conversation_id=conversation_id)
        return True

    def get_user_conversations(self, user_id: str) -> list[Conversation]:
        """Get all conversations for a user.

        Args:
            user_id: User ID

        Returns:
            List of conversations, sorted by updated_at descending
        """
        engine = get_engine()
        with Session(engine) as session:
            convs_db = session.exec(
                select(ConversationDB)
                .where(ConversationDB.user_id == user_id)
                .order_by(ConversationDB.updated_at.desc())
            ).all()

            conversations = []
            for conv_db in convs_db:
                # Use cached version if available
                if conv_db.id in self._cache:
                    conversations.append(self._cache[conv_db.id])
                else:
                    conversations.append(self._db_to_conversation(conv_db, session))

            return conversations

    def _load_from_db(self, conversation_id: str, user_id: str) -> Conversation | None:
        """Load a conversation from database.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for ownership verification

        Returns:
            Conversation or None if not found/unauthorized
        """
        engine = get_engine()
        with Session(engine) as session:
            conv_db = session.exec(
                select(ConversationDB).where(ConversationDB.id == conversation_id)
            ).first()

            if not conv_db:
                logger.debug(
                    "conversation_not_found_in_db",
                    conversation_id=conversation_id,
                )
                return None

            if conv_db.user_id != user_id:
                logger.warning(
                    "conversation_access_denied",
                    conversation_id=conversation_id,
                    owner=conv_db.user_id,
                    requester=user_id,
                )
                return None

            conversation = self._db_to_conversation(conv_db, session)
            logger.debug(
                "conversation_loaded_from_db",
                conversation_id=conversation_id,
                message_count=len(conversation.messages),
            )
            return conversation

    def _db_to_conversation(
        self,
        conv_db: ConversationDB,
        session: Session,
    ) -> Conversation:
        """Convert database model to Conversation instance.

        Args:
            conv_db: Database conversation model
            session: Database session for loading messages

        Returns:
            Conversation instance
        """
        # Load messages
        messages_db = session.exec(
            select(MessageDB)
            .where(MessageDB.conversation_id == conv_db.id)
            .order_by(MessageDB.created_at.asc())
        ).all()

        messages = [
            Message(
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                timestamp=msg.created_at,
            )
            for msg in messages_db
        ]

        return Conversation(
            id=conv_db.id,
            user_id=conv_db.user_id,
            title=conv_db.title,
            messages=messages,
            created_at=conv_db.created_at,
            updated_at=conv_db.updated_at,
        )

    def _save_to_db(self, conversation: Conversation) -> None:
        """Save a new conversation to database.

        Args:
            conversation: Conversation to save
        """
        engine = get_engine()
        with Session(engine) as session:
            conv_db = ConversationDB(
                id=conversation.id,
                user_id=conversation.user_id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
            session.add(conv_db)
            session.commit()

            logger.debug(
                "conversation_saved_to_db",
                conversation_id=conversation.id,
            )

    def _cleanup_cache_if_needed(self) -> None:
        """Remove oldest conversations from cache if over limit."""
        if len(self._cache) <= self._max_cache_size:
            return

        # Sort by updated_at and remove oldest
        sorted_convos = sorted(
            self._cache.items(),
            key=lambda x: x[1].updated_at,
        )

        # Remove oldest 10%
        to_remove = len(self._cache) - int(self._max_cache_size * 0.9)
        for conv_id, _ in sorted_convos[:to_remove]:
            del self._cache[conv_id]

        logger.info(
            "conversation_cache_cleanup",
            removed=to_remove,
            remaining=len(self._cache),
        )


# Global conversation memory instance
_memory = ConversationMemory()


def get_conversation_memory() -> ConversationMemory:
    """Get the global conversation memory instance."""
    return _memory


# Export classes and functions
__all__ = [
    "Message",
    "Conversation",
    "ConversationContext",
    "ConversationMemory",
    "get_conversation_memory",
    "MAX_CONTEXT_MESSAGES",
]
