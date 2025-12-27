# Source Code Architecture

This directory contains the core implementation of the Multi-Agent Todo Application.

## Directory Structure

```
src/
├── __init__.py           # Package metadata (version, exports)
├── app.py                # Main application entry point and workflow orchestration
├── agents/               # Agent implementations
│   ├── __init__.py       # Agent exports and factory functions
│   ├── base.py           # BaseAgent abstract base class
│   ├── orchestrator.py   # Central message router and coordinator
│   ├── task_manager.py   # Task CRUD business logic
│   ├── storage_handler.py # Storage operations wrapper
│   └── ui_controller.py  # UI action handlers
├── models/               # Pydantic data models
│   ├── __init__.py       # Model exports
│   ├── messages.py       # AgentMessage, AgentResponse, AgentInfo
│   ├── tasks.py          # Task model with immutable updates
│   └── exceptions.py     # Exception hierarchy
├── backends/             # Storage backend implementations
│   ├── __init__.py       # Backend exports
│   ├── base.py           # StorageBackend protocol definition
│   └── memory.py         # InMemoryBackend implementation
└── adapters/             # UI/IO adapters
    ├── __init__.py       # Adapter exports
    └── console.py        # Rich console adapter
```

## Architecture Overview

### Multi-Agent System

The application uses a multi-agent architecture with the Orchestrator pattern:

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │     Agent       │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │ Task Manager  │ │    Storage    │ │      UI       │
   │    Agent      │ │    Handler    │ │  Controller   │
   └───────────────┘ └───────────────┘ └───────────────┘
           │                 │
           │                 ▼
           │         ┌───────────────┐
           └────────►│    Storage    │
                     │    Backend    │
                     └───────────────┘
```

### Message Routing

Messages are routed based on action prefixes:

| Prefix      | Target Agent        | Example Actions                    |
|-------------|--------------------|------------------------------------|
| `task_*`    | Task Manager       | task_add, task_list, task_complete |
| `storage_*` | Storage Handler    | storage_save, storage_get          |
| `ui_*`      | UI Controller      | ui_display_menu, ui_get_choice     |
| `system_*`  | Orchestrator       | system_status, system_shutdown     |

### Message Flow Example

```
1. User selects "Add Task" from menu
2. App sends AgentMessage(action="task_add", payload={title: "..."})
3. Orchestrator routes to TaskManagerAgent
4. TaskManagerAgent creates Task model
5. TaskManagerAgent sends storage_save to StorageHandlerAgent
6. StorageHandlerAgent persists via InMemoryBackend
7. Response flows back through the chain
```

## Component Details

### Agents (`agents/`)

**BaseAgent** (`base.py`):
- Abstract base class for all agents
- Provides action registration, lifecycle management
- Includes structlog integration for JSON logging

**OrchestratorAgent** (`orchestrator.py`):
- Central coordinator and message router
- Manages agent registry and routing table
- Handles system_* actions directly

**TaskManagerAgent** (`task_manager.py`):
- Business logic for task operations
- Validates input, applies business rules
- Delegates persistence to StorageHandler

**StorageHandlerAgent** (`storage_handler.py`):
- Wraps storage backend operations
- Handles Task serialization/deserialization
- Implements query filtering

**UIControllerAgent** (`ui_controller.py`):
- Handles UI actions via ConsoleAdapter
- Manages menu display, input collection
- Converts between dicts and Task models

### Models (`models/`)

**AgentMessage** (`messages.py`):
- Request message with sender, recipient, action, payload
- Auto-generated request_id and correlation_id
- Timestamp tracking

**AgentResponse** (`messages.py`):
- Response with status (success/error), result/error
- Links to original request_id

**Task** (`tasks.py`):
- Immutable task model with update() method
- Auto-generated UUID and timestamps
- Status: pending/completed

### Backends (`backends/`)

**StorageBackend** (`base.py`):
- Protocol defining storage operations
- All methods are async
- Returns Task models directly

**InMemoryBackend** (`memory.py`):
- Dict-based in-memory storage
- Thread-safe with asyncio.Lock
- Implements all StorageBackend methods

### Adapters (`adapters/`)

**ConsoleAdapter** (`console.py`):
- Rich library wrapper for terminal UI
- Styled tables, prompts, messages
- Consistent color scheme

## Development Workflow

### Adding a New Agent

1. Create new file in `agents/` directory
2. Extend `BaseAgent` class
3. Implement `handle_message()` method
4. Register action handlers in `__init__`
5. Add to orchestrator's routing table
6. Export from `agents/__init__.py`

### Adding a New Storage Backend

1. Create new file in `backends/` directory
2. Implement `StorageBackend` protocol
3. All methods must be async
4. Accept/return Task models
5. Export from `backends/__init__.py`

### Running the Application

```bash
# Interactive mode
uv run todo

# With debug logging
LOG_LEVEL=DEBUG uv run todo
```

### Running Tests

```bash
# All tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Specific agent tests
uv run pytest tests/unit/test_task_manager_agent.py -v
```

## Code Quality

- **Type Hints**: Full type annotations with mypy strict mode
- **Linting**: Ruff with import sorting and formatting
- **Logging**: structlog for structured JSON logging
- **Testing**: pytest-asyncio for async test support
- **Coverage**: Target 80%+ line coverage
