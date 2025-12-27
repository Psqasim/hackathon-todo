# Agent Contracts: Multi-Agent Architecture System

**Feature**: 001-multi-agent-architecture
**Date**: 2025-12-26
**Version**: 1.0.0

## Overview

This document defines the contracts (interfaces) for all agents in the system.
Each contract specifies:
- Supported actions
- Input/output schemas
- Error conditions
- Usage examples

## Base Agent Contract

All agents inherit from this contract.

### Interface

```python
class BaseAgent(ABC):
    """Abstract base class defining the agent contract."""

    name: str                    # Unique agent identifier
    version: str                 # Semantic version (1.0.0)
    supported_actions: list[str] # Actions this agent handles

    @abstractmethod
    def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Process incoming message and return response.

        Args:
            message: Validated AgentMessage with action and payload

        Returns:
            AgentResponse with status, result, or error

        Raises:
            Never raises to caller - always returns AgentResponse
        """
        pass

    def start(self) -> None:
        """Initialize agent. Called before message processing."""
        pass

    def shutdown(self) -> None:
        """Cleanup agent resources. Called on system shutdown."""
        pass
```

---

## Main Orchestrator Contract

**Name**: `orchestrator`
**Version**: 1.0.0

### Purpose

Routes messages to appropriate subagents and manages system lifecycle.

### Supported Actions

| Action | Description | Routed To |
|--------|-------------|-----------|
| `task_*` | All task operations | Task Manager |
| `storage_*` | Direct storage operations | Storage Agent |
| `ui_*` | User interface operations | UI Controller |
| `system_status` | Get system health | Self |
| `system_shutdown` | Initiate shutdown | Self |

### Registration Interface

```python
def register_agent(self, agent: BaseAgent) -> None:
    """
    Register a subagent with the orchestrator.

    Args:
        agent: Agent instance implementing BaseAgent

    Raises:
        AgentInitError: If agent name conflicts or invalid
    """

def get_agent(self, name: str) -> BaseAgent | None:
    """
    Retrieve registered agent by name.

    Args:
        name: Agent name

    Returns:
        Agent instance or None if not found
    """

def list_agents(self) -> list[AgentInfo]:
    """
    List all registered agents with status.

    Returns:
        List of AgentInfo for all registered agents
    """
```

### Message Routing

```python
def route_message(self, message: AgentMessage) -> AgentResponse:
    """
    Route message to appropriate agent based on action prefix.

    Routing rules:
    - action.startswith("task_") → task_manager
    - action.startswith("storage_") → storage_agent
    - action.startswith("ui_") → ui_controller
    - action.startswith("system_") → self
    - else → RoutingError

    Args:
        message: AgentMessage with action and payload

    Returns:
        AgentResponse from target agent
    """
```

### System Actions

#### system_status

Get health status of all agents.

**Input Payload**: `{}`

**Output Result**:
```python
{
    "status": "healthy" | "degraded" | "error",
    "agents": [
        {
            "name": str,
            "status": "active" | "inactive" | "error",
            "version": str,
            "actions": list[str]
        }
    ],
    "uptime_seconds": float
}
```

#### system_shutdown

Initiate graceful system shutdown.

**Input Payload**: `{"force": bool}` (optional, default False)

**Output Result**:
```python
{
    "status": "shutdown_initiated",
    "pending_operations": int
}
```

---

## Task Manager Contract

**Name**: `task_manager`
**Version**: 1.0.0

### Purpose

Handles all task-related business logic and operations.

### Supported Actions

| Action | Description |
|--------|-------------|
| `task_add` | Create new task |
| `task_delete` | Remove task by ID |
| `task_update` | Modify task fields |
| `task_list` | Get all tasks |
| `task_get` | Get single task by ID |
| `task_complete` | Toggle completion status |

### Dependencies

- Storage Agent (for persistence)

### Actions Detail

#### task_add

Create a new task.

**Input Payload**:
```python
{
    "title": str,         # Required, 1-200 chars
    "description": str    # Optional, max 1000 chars
}
```

**Success Result**:
```python
{
    "task": {
        "id": int,
        "title": str,
        "description": str | None,
        "completed": False,
        "created_at": str,  # ISO 8601
        "updated_at": str   # ISO 8601
    }
}
```

**Error Conditions**:
- `ValidationError`: Title missing or too long
- `StorageError`: Persistence failure

#### task_delete

Delete a task by ID.

**Input Payload**:
```python
{
    "task_id": int  # Required, positive integer
}
```

**Success Result**:
```python
{
    "deleted": True,
    "task_id": int
}
```

**Error Conditions**:
- `ValidationError`: Invalid task_id format
- `NotFoundError`: Task ID doesn't exist

#### task_update

Update task fields.

**Input Payload**:
```python
{
    "task_id": int,            # Required
    "title": str | None,       # Optional, 1-200 chars
    "description": str | None  # Optional, max 1000 chars
}
```

**Success Result**:
```python
{
    "task": {
        "id": int,
        "title": str,
        "description": str | None,
        "completed": bool,
        "created_at": str,
        "updated_at": str  # Updated to current time
    }
}
```

**Error Conditions**:
- `ValidationError`: Invalid field values
- `NotFoundError`: Task ID doesn't exist

#### task_list

Get all tasks.

**Input Payload**:
```python
{
    "filter": {                    # Optional
        "completed": bool | None   # Filter by completion status
    }
}
```

**Success Result**:
```python
{
    "tasks": [
        {
            "id": int,
            "title": str,
            "description": str | None,
            "completed": bool,
            "created_at": str,
            "updated_at": str
        }
    ],
    "total": int
}
```

#### task_get

Get single task by ID.

**Input Payload**:
```python
{
    "task_id": int  # Required
}
```

**Success Result**:
```python
{
    "task": {
        "id": int,
        "title": str,
        "description": str | None,
        "completed": bool,
        "created_at": str,
        "updated_at": str
    }
}
```

**Error Conditions**:
- `NotFoundError`: Task ID doesn't exist

#### task_complete

Toggle task completion status.

**Input Payload**:
```python
{
    "task_id": int  # Required
}
```

**Success Result**:
```python
{
    "task": {
        "id": int,
        "title": str,
        "description": str | None,
        "completed": bool,  # Toggled value
        "created_at": str,
        "updated_at": str   # Updated to current time
    }
}
```

**Error Conditions**:
- `NotFoundError`: Task ID doesn't exist

---

## Storage Agent Contract

**Name**: `storage_agent`
**Version**: 1.0.0

### Purpose

Manages all data persistence with pluggable backends.

### Supported Actions

| Action | Description |
|--------|-------------|
| `storage_save` | Store entity |
| `storage_get` | Retrieve by ID |
| `storage_delete` | Remove by ID |
| `storage_list` | List all entities |
| `storage_query` | Filter entities |

### Backend Protocol

Storage Agent delegates to a backend implementing:

```python
class StorageBackend(Protocol):
    """Protocol for storage backend implementations."""

    def save(self, entity_type: str, data: dict) -> dict:
        """Save entity, return with generated ID."""
        ...

    def get(self, entity_type: str, entity_id: int) -> dict | None:
        """Get entity by ID, return None if not found."""
        ...

    def delete(self, entity_type: str, entity_id: int) -> bool:
        """Delete entity, return True if deleted."""
        ...

    def list(self, entity_type: str) -> list[dict]:
        """List all entities of type."""
        ...

    def query(self, entity_type: str, filters: dict) -> list[dict]:
        """Filter entities by criteria."""
        ...
```

### Actions Detail

#### storage_save

Store an entity.

**Input Payload**:
```python
{
    "entity_type": str,  # "task"
    "data": dict         # Entity data without ID
}
```

**Success Result**:
```python
{
    "entity": dict,      # Saved entity with generated ID
    "entity_id": int
}
```

#### storage_get

Retrieve entity by ID.

**Input Payload**:
```python
{
    "entity_type": str,
    "entity_id": int
}
```

**Success Result**:
```python
{
    "entity": dict | None  # None if not found
}
```

#### storage_delete

Delete entity by ID.

**Input Payload**:
```python
{
    "entity_type": str,
    "entity_id": int
}
```

**Success Result**:
```python
{
    "deleted": bool  # True if deleted, False if not found
}
```

#### storage_list

List all entities of type.

**Input Payload**:
```python
{
    "entity_type": str
}
```

**Success Result**:
```python
{
    "entities": list[dict],
    "count": int
}
```

#### storage_query

Filter entities.

**Input Payload**:
```python
{
    "entity_type": str,
    "filters": {
        "field_name": value  # Equality filter
    }
}
```

**Success Result**:
```python
{
    "entities": list[dict],
    "count": int
}
```

---

## UI Controller Contract

**Name**: `ui_controller`
**Version**: 1.0.0

### Purpose

Handles all user interaction and presentation logic.

### Supported Actions

| Action | Description |
|--------|-------------|
| `ui_show_menu` | Display main menu |
| `ui_show_tasks` | Display task list |
| `ui_get_input` | Prompt for input |
| `ui_show_message` | Display message |
| `ui_confirm` | Yes/no prompt |

### Adapter Protocol

UI Controller uses adapters for different interfaces:

```python
class UIAdapter(Protocol):
    """Protocol for UI implementations."""

    def display(self, content: str, style: str = "default") -> None:
        """Display content to user."""
        ...

    def prompt(self, message: str, default: str = "") -> str:
        """Get text input from user."""
        ...

    def confirm(self, message: str) -> bool:
        """Get yes/no from user."""
        ...

    def menu(self, title: str, options: list[str]) -> int:
        """Display menu, return selected index."""
        ...
```

### Actions Detail

#### ui_show_menu

Display main menu and get selection.

**Input Payload**:
```python
{
    "title": str,         # Menu title
    "options": list[str]  # Menu options
}
```

**Success Result**:
```python
{
    "selection": int,     # 0-based index
    "option": str         # Selected option text
}
```

#### ui_show_tasks

Display task list.

**Input Payload**:
```python
{
    "tasks": list[dict],  # Task objects
    "title": str          # Optional, default "Tasks"
}
```

**Success Result**:
```python
{
    "displayed": True,
    "count": int
}
```

#### ui_get_input

Prompt user for text input.

**Input Payload**:
```python
{
    "prompt": str,           # Prompt message
    "default": str | None,   # Default value
    "required": bool         # Whether input required
}
```

**Success Result**:
```python
{
    "value": str  # User input (may be empty if not required)
}
```

**Error Conditions**:
- `ValidationError`: Required input empty

#### ui_show_message

Display informational message.

**Input Payload**:
```python
{
    "message": str,
    "level": "info" | "success" | "warning" | "error"
}
```

**Success Result**:
```python
{
    "displayed": True
}
```

#### ui_confirm

Yes/no confirmation prompt.

**Input Payload**:
```python
{
    "message": str,
    "default": bool  # Default if user presses Enter
}
```

**Success Result**:
```python
{
    "confirmed": bool
}
```

---

## Message Schemas (Pydantic)

```python
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    """Standard message format for agent communication."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str
    recipient: str
    action: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str

class AgentResponse(BaseModel):
    """Standard response format from agents."""

    request_id: str
    sender: str
    status: Literal["success", "error"]
    result: Any = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentInfo(BaseModel):
    """Agent registration information."""

    name: str
    status: Literal["active", "inactive", "error"]
    version: str
    supported_actions: list[str]
```

---

## Error Response Format

All errors return AgentResponse with:

```python
AgentResponse(
    request_id="original-request-id",
    sender="agent-name",
    status="error",
    result=None,
    error="Human-readable error message",
    timestamp=datetime.utcnow()
)
```

Error message format:
- `[ErrorType]: Description`
- Example: `[ValidationError]: Task title is required`
- Example: `[NotFoundError]: Task with ID 42 not found`
