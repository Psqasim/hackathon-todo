# Data Model: Multi-Agent Architecture System

**Feature**: 001-multi-agent-architecture
**Date**: 2025-12-26
**Status**: Complete

## Entity Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        System Entities                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐         ┌──────────────┐                      │
│  │    Agent    │────────▶│ AgentMessage │                      │
│  │             │         └──────────────┘                      │
│  │ - name      │                │                              │
│  │ - status    │                │ generates                    │
│  │ - version   │                ▼                              │
│  │ - actions[] │         ┌──────────────┐                      │
│  └─────────────┘         │AgentResponse │                      │
│         │                └──────────────┘                      │
│         │                                                      │
│  implements                                                    │
│         │                                                      │
│         ▼                                                      │
│  ┌─────────────────────────────────────────┐                   │
│  │             Agent Subclasses            │                   │
│  ├──────────────┬──────────────┬──────────┬┤                   │
│  │ Orchestrator │ TaskManager  │ Storage  │ UIController │     │
│  └──────────────┴──────────────┴──────────┴──────────────┘     │
│                        │                                        │
│                        │ manages                                │
│                        ▼                                        │
│                 ┌─────────────┐                                 │
│                 │    Task     │                                 │
│                 │             │                                 │
│                 │ - id        │                                 │
│                 │ - title     │                                 │
│                 │ - completed │                                 │
│                 └─────────────┘                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Entities

### 1. AgentMessage

**Purpose**: Standard communication unit between agents.

**Attributes**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| request_id | str | Yes | Unique identifier (UUID4) | Valid UUID4 format |
| sender | str | Yes | Name of sending agent | Non-empty string |
| recipient | str | Yes | Name of target agent | Non-empty string |
| action | str | Yes | Operation to perform | Non-empty, lowercase |
| payload | dict[str, Any] | Yes | Request data | Valid JSON object |
| timestamp | datetime | Yes | Message creation time | ISO 8601 format |
| correlation_id | str | Yes | Tracing identifier | Valid UUID4 format |

**Constraints**:
- request_id must be unique per message
- correlation_id must be consistent across related messages
- timestamp must be UTC timezone

**Example**:
```python
AgentMessage(
    request_id="550e8400-e29b-41d4-a716-446655440000",
    sender="orchestrator",
    recipient="task_manager",
    action="task_add",
    payload={"title": "Buy groceries", "description": "Milk, eggs, bread"},
    timestamp=datetime(2025, 1, 3, 10, 30, 0),
    correlation_id="660e8400-e29b-41d4-a716-446655440001"
)
```

### 2. AgentResponse

**Purpose**: Standard response from agent message processing.

**Attributes**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| request_id | str | Yes | Original request ID | Must match request |
| sender | str | Yes | Responding agent name | Non-empty string |
| status | Literal["success", "error"] | Yes | Operation outcome | Enum value |
| result | Any | No | Operation result data | None if error |
| error | str | No | Error message | None if success |
| timestamp | datetime | Yes | Response creation time | ISO 8601 format |

**Constraints**:
- If status="success", result should be populated, error should be None
- If status="error", error should be populated, result should be None
- request_id must match the original AgentMessage.request_id

**Example (Success)**:
```python
AgentResponse(
    request_id="550e8400-e29b-41d4-a716-446655440000",
    sender="task_manager",
    status="success",
    result={"task_id": 1, "title": "Buy groceries", "completed": False},
    error=None,
    timestamp=datetime(2025, 1, 3, 10, 30, 1)
)
```

**Example (Error)**:
```python
AgentResponse(
    request_id="550e8400-e29b-41d4-a716-446655440000",
    sender="task_manager",
    status="error",
    result=None,
    error="Task title is required",
    timestamp=datetime(2025, 1, 3, 10, 30, 1)
)
```

### 3. Task

**Purpose**: Domain entity representing a todo item.

**Attributes**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | int | Yes (auto) | Unique identifier | Positive integer |
| title | str | Yes | Task title | 1-200 characters |
| description | str | No | Task details | Max 1000 characters |
| completed | bool | Yes | Completion status | Default: False |
| created_at | datetime | Yes (auto) | Creation timestamp | ISO 8601 format |
| updated_at | datetime | Yes (auto) | Last update timestamp | ISO 8601 format |

**Constraints**:
- id is auto-generated by Storage Agent
- title must be non-empty and max 200 chars
- description can be empty, max 1000 chars
- created_at set on creation, never changes
- updated_at set on creation, updates on any modification

**State Transitions**:
```
        create
  ∅ ─────────────▶ pending (completed=False)
                        │
                        │ complete
                        ▼
                   completed (completed=True)
                        │
                        │ uncomplete
                        ▼
                   pending (completed=False)
```

**Example**:
```python
Task(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False,
    created_at=datetime(2025, 1, 3, 10, 30, 0),
    updated_at=datetime(2025, 1, 3, 10, 30, 0)
)
```

### 4. AgentInfo

**Purpose**: Registration information for an agent with the Orchestrator.

**Attributes**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| name | str | Yes | Unique agent name | Non-empty, lowercase |
| status | Literal["active", "inactive", "error"] | Yes | Current status | Enum value |
| version | str | Yes | Agent version | Semver format |
| supported_actions | list[str] | Yes | Actions this agent handles | Non-empty list |

**Constraints**:
- name must be unique per system
- version follows semantic versioning (MAJOR.MINOR.PATCH)
- supported_actions defines routing rules

**Example**:
```python
AgentInfo(
    name="task_manager",
    status="active",
    version="1.0.0",
    supported_actions=["task_add", "task_delete", "task_update", "task_list", "task_complete"]
)
```

### 5. StorageOperation

**Purpose**: Internal model for storage operations.

**Attributes**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| operation | Literal["save", "get", "delete", "list", "query"] | Yes | Operation type | Enum value |
| entity_type | str | Yes | Type of entity | "task" for Phase I |
| entity_id | int | No | Entity identifier | Required for get/delete |
| data | dict | No | Entity data | Required for save |
| query | dict | No | Filter criteria | Optional for query |

**Example**:
```python
StorageOperation(
    operation="save",
    entity_type="task",
    entity_id=None,
    data={"title": "Buy groceries", "description": "Milk, eggs"},
    query=None
)
```

## Exception Types

### AgentError Hierarchy

```
Exception
    └── AgentError (base)
            ├── ValidationError      # Invalid input data
            ├── NotFoundError        # Entity not found
            ├── StorageError         # Persistence failure
            ├── RoutingError         # Unknown action/agent
            └── AgentInitError       # Agent startup failure
```

**Usage**:
- `ValidationError`: Task title empty, invalid message format
- `NotFoundError`: Task ID doesn't exist
- `StorageError`: Backend unavailable, write failure
- `RoutingError`: Unknown action prefix, unregistered agent
- `AgentInitError`: Agent failed during startup

## Relationships

### Agent → AgentMessage

- Agents send AgentMessage to Orchestrator or directly to other agents
- One agent can send many messages
- Messages are stateless (no persistence)

### AgentMessage → AgentResponse

- Each AgentMessage generates exactly one AgentResponse
- request_id links response to request
- correlation_id links multiple related requests

### TaskManager → Task

- TaskManager is the only agent that creates/modifies Task entities
- Tasks are validated by TaskManager before storage
- TaskManager delegates persistence to Storage Agent

### StorageAgent → Task (Persistence)

- Storage Agent persists Task entities
- Phase I: In-memory dictionary `Dict[int, Task]`
- Phase II+: PostgreSQL database
- Storage Agent doesn't validate business rules

## Index Strategy (Phase II+)

For Phase II when migrating to PostgreSQL:

| Entity | Index | Columns | Purpose |
|--------|-------|---------|---------|
| Task | PK | id | Primary key lookup |
| Task | IX_completed | completed | Filter by status |
| Task | IX_created | created_at | Sort by creation |

## Data Migration Path

### Phase I → Phase II

1. Export all Task entities from in-memory storage
2. Transform to SQLModel schema
3. Bulk insert into PostgreSQL
4. Verify row counts match
5. Switch Storage Agent backend

**Migration Script Requirements**:
- Idempotent (can run multiple times)
- Preserves created_at/updated_at timestamps
- Generates new IDs if conflicts exist
- Logs all operations for audit

## Validation Rules Summary

| Entity | Field | Rule |
|--------|-------|------|
| AgentMessage | request_id | UUID4 format |
| AgentMessage | sender | Non-empty string |
| AgentMessage | recipient | Non-empty string |
| AgentMessage | action | Non-empty, lowercase |
| AgentMessage | correlation_id | UUID4 format |
| AgentResponse | status | "success" or "error" |
| Task | title | 1-200 characters |
| Task | description | Max 1000 characters |
| Task | id | Positive integer |
| AgentInfo | version | Semver format |
