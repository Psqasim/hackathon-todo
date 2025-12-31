# Data Model: AI Chatbot with MCP Integration

**Feature**: 003-ai-chatbot-mcp
**Date**: 2025-12-30
**Status**: Complete

---

## Overview

Phase III adds conversation persistence to the existing database schema. The MCP server communicates with the OpenAI API and the existing FastAPI backend, storing conversation history for continuity.

---

## New Entities

### Conversation

Represents a chat session between a user and the AI agent.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique conversation identifier |
| user_id | UUID | FK → users.id, NOT NULL | Owner of the conversation |
| title | VARCHAR(200) | NULL | Auto-generated title from first message |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation started |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (frequent lookups by user)

**Relationships**:
- Conversation → User: Many-to-One (many conversations per user)
- Conversation → Message: One-to-Many (conversation has many messages)

---

### Message

Represents a single message in a conversation (user or assistant).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique message identifier |
| conversation_id | UUID | FK → conversations.id, NOT NULL | Parent conversation |
| role | VARCHAR(20) | NOT NULL | 'user', 'assistant', or 'system' |
| content | TEXT | NOT NULL | Message text content |
| tool_calls | JSONB | NULL | MCP tool invocations (if any) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent |

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` (message retrieval)
- `idx_messages_created_at` on `created_at` (ordering)

**Relationships**:
- Message → Conversation: Many-to-One

**Tool Calls JSON Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "tool_name": { "type": "string" },
      "parameters": { "type": "object" },
      "result": { "type": "object" },
      "timestamp": { "type": "string", "format": "date-time" }
    }
  }
}
```

---

## Existing Entities (No Changes)

### User (from Phase II)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | User email |
| name | VARCHAR(100) | Display name |
| hashed_password | VARCHAR(255) | Password hash |
| created_at | TIMESTAMP | Account creation |

### Task (from Phase II)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK → users.id |
| title | VARCHAR(200) | Task title |
| description | TEXT | Task description |
| status | VARCHAR(20) | 'pending' or 'completed' |
| priority | VARCHAR(20) | low/medium/high/urgent |
| due_date | TIMESTAMP | Optional due date |
| tags | JSONB | Array of tag strings |
| is_recurring | BOOLEAN | Recurring task flag |
| recurrence_pattern | VARCHAR(20) | daily/weekly/monthly/yearly |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |
| completed_at | TIMESTAMP | Completion time |

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
│─────────────────│
│ id (PK)         │
│ email           │
│ name            │
│ hashed_password │
│ created_at      │
└───────┬─────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐      ┌─────────────────┐
│     Task        │      │  Conversation   │
│─────────────────│      │─────────────────│
│ id (PK)         │      │ id (PK)         │
│ user_id (FK) ◄──┼──────┤ user_id (FK)    │
│ title           │      │ title           │
│ description     │      │ created_at      │
│ status          │      │ updated_at      │
│ priority        │      └───────┬─────────┘
│ due_date        │              │
│ tags            │              │ 1:N
│ ...             │              ▼
└─────────────────┘      ┌─────────────────┐
                         │    Message      │
                         │─────────────────│
                         │ id (PK)         │
                         │ conversation_id │
                         │ role            │
                         │ content         │
                         │ tool_calls      │
                         │ created_at      │
                         └─────────────────┘
```

---

## SQLModel Definitions

### ConversationDB

```python
from sqlmodel import SQLModel, Field as SQLField
from datetime import datetime, UTC

class ConversationDB(SQLModel, table=True):
    """Database model for chat conversations."""

    __tablename__ = "conversations"

    id: str = SQLField(default_factory=generate_uuid, primary_key=True)
    user_id: str = SQLField(foreign_key="users.id", index=True)
    title: str | None = SQLField(default=None, max_length=200)
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
```

### MessageDB

```python
from sqlmodel import JSON, Column

class MessageDB(SQLModel, table=True):
    """Database model for chat messages."""

    __tablename__ = "messages"

    id: str = SQLField(default_factory=generate_uuid, primary_key=True)
    conversation_id: str = SQLField(foreign_key="conversations.id", index=True)
    role: str = SQLField(max_length=20)  # 'user', 'assistant', 'system'
    content: str = SQLField()
    tool_calls: list[dict] | None = SQLField(
        default=None,
        sa_column=Column(JSON)
    )
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
```

---

## Pydantic Models (API)

### ChatRequest

```python
class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str | None = None  # Resume existing conversation
```

### ChatMessage

```python
class ChatMessage(BaseModel):
    """Single message in chat response."""
    role: Literal["user", "assistant", "system"]
    content: str
    tool_calls: list[ToolCall] | None = None
    created_at: datetime
```

### ToolCall

```python
class ToolCall(BaseModel):
    """MCP tool invocation details."""
    id: str
    tool_name: str
    parameters: dict
    result: dict | None = None
    timestamp: datetime
```

### ChatResponse

```python
class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    conversation_id: str
    message: ChatMessage
```

---

## State Transitions

### Conversation States

```
Created → Active → Archived
   ↓
  (user deletes)
   ↓
Deleted
```

### Message Flow

```
User Input → Message Created (role=user)
    ↓
OpenAI Processing
    ↓
Tool Calls (optional) → MCP Tools Execute → Results Stored
    ↓
Agent Response → Message Created (role=assistant)
```

---

## Validation Rules

### Conversation

1. `user_id` must reference existing user
2. `title` auto-generated from first user message (first 50 chars)
3. `updated_at` updated on each new message

### Message

1. `conversation_id` must reference existing conversation
2. `role` must be one of: 'user', 'assistant', 'system'
3. `content` cannot be empty
4. `tool_calls` must match ToolCall schema if present

---

## Migration Strategy

Phase III adds new tables without modifying existing ones:

```sql
-- Migration: 003_add_conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

---

## Data Retention

- Conversations older than 90 days MAY be archived (future enhancement)
- Messages are retained as long as parent conversation exists
- User deletion cascades to all conversations and messages
