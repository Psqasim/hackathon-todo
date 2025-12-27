# Hackathon Todo - Multi-Agent Architecture

A comprehensive multi-agent Todo application built with Spec-Driven Development (SDD).

## Overview

This project implements a multi-agent architecture for a Todo application that evolves through 5 phases:
- **Phase I**: Console App (In-Memory) - **Current Implementation**
- **Phase II**: Web App (Database)
- **Phase III**: AI Chatbot (MCP Integration)
- **Phase IV**: Local Kubernetes
- **Phase V**: Cloud Deployment

## Architecture

### Agents
- **Orchestrator Agent**: Central coordinator routing messages between subagents
- **Task Manager Agent**: Business logic for task CRUD operations
- **Storage Handler Agent**: Data persistence layer with pluggable backends
- **UI Controller Agent**: Console interface using Rich library

### Message Routing
Messages are routed based on action prefixes:
- `task_*` -> Task Manager Agent
- `storage_*` -> Storage Handler Agent
- `ui_*` -> UI Controller Agent
- `system_*` -> Orchestrator Agent

## Quick Start

### Prerequisites
- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Psqasim/hackathon-todo.git
cd hackathon-todo

# Install dependencies (including dev dependencies)
uv sync --all-extras
```

### Running the Application

```bash
# Run the interactive todo app
uv run todo
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/

# Run tests with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in your browser

# Run specific test file
uv run pytest tests/unit/test_tasks.py

# Run specific test class
uv run pytest tests/unit/test_tasks.py::TestTaskCreation

# Run specific test method
uv run pytest tests/unit/test_tasks.py::TestTaskCreation::test_create_task_with_title_only
```

### Code Quality

```bash
# Run linter
uv run ruff check src tests

# Run linter with auto-fix
uv run ruff check --fix src tests

# Run type checker
uv run mypy src
```

## Features (Phase I)

1. **Add Task**: Create new tasks with title and optional description
2. **View All Tasks**: View all tasks with status filtering
3. **Update Task**: Modify task title and description
4. **Mark Task Complete**: Mark tasks as complete with timestamp
5. **Delete Task**: Remove tasks from the system
6. **View Task Details**: See detailed task information including timestamps

## Technology Stack

- **Language**: Python 3.12+
- **Package Manager**: UV
- **Validation**: Pydantic v2
- **Console UI**: Rich
- **Logging**: structlog (JSON format)
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Linting**: Ruff
- **Type Checking**: mypy (strict mode)

## Project Structure

```
hackathon-todo/
├── src/
│   ├── __init__.py          # Package metadata
│   ├── app.py               # Main application entry point
│   ├── agents/              # Agent implementations
│   │   ├── base.py          # BaseAgent ABC
│   │   ├── orchestrator.py  # Central coordinator
│   │   ├── task_manager.py  # Task business logic
│   │   ├── storage_handler.py # Persistence operations
│   │   └── ui_controller.py # UI operations
│   ├── models/              # Pydantic models
│   │   ├── messages.py      # AgentMessage, AgentResponse, AgentInfo
│   │   ├── tasks.py         # Task model
│   │   └── exceptions.py    # Exception hierarchy
│   ├── backends/            # Storage backends
│   │   ├── base.py          # StorageBackend protocol
│   │   └── memory.py        # InMemoryBackend
│   └── adapters/            # UI adapters
│       └── console.py       # Rich console adapter
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── contract/           # Contract tests
├── specs/                  # Feature specifications
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Development

### Adding a New Agent

1. Create a new file in `src/agents/`
2. Extend `BaseAgent` and implement `handle_message()`
3. Register action handlers in `__init__`
4. Register the agent with the orchestrator

### Adding a New Storage Backend

1. Create a new file in `src/backends/`
2. Implement the `StorageBackend` protocol
3. All methods are async and return/accept `Task` models

## API Reference

### Task Actions
- `task_add`: `{"title": str, "description": str?}`
- `task_list`: `{"status": "pending"|"completed"?}`
- `task_complete`: `{"task_id": str}`
- `task_delete`: `{"task_id": str}`
- `task_get`: `{"task_id": str}`
- `task_update`: `{"task_id": str, "title": str?, "description": str?}`

### System Actions
- `system_status`: Get orchestrator and agent status
- `system_agents`: List all registered agents
- `system_shutdown`: Stop the orchestrator

## License

MIT

---
Built with Spec-Driven Development (SDD) and Claude Code
