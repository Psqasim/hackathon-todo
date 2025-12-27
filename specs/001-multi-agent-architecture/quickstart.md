# Quickstart Guide: Multi-Agent Architecture System

**Feature**: 001-multi-agent-architecture
**Date**: 2025-12-26

## Prerequisites

- Python 3.12+ installed
- UV package manager installed
- Git (for version control)

### Install UV (if not installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd hackathon-todo
git checkout 001-multi-agent-architecture
```

### 2. Create Virtual Environment

```bash
uv venv
```

### 3. Activate Virtual Environment

```bash
# macOS/Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\activate

# Windows (CMD)
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
# Install all dependencies including dev
uv pip install -e ".[dev]"
```

## Project Structure

After setup, your project structure should look like:

```
hackathon-todo/
├── .venv/                    # Virtual environment
├── pyproject.toml           # Project configuration
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py          # BaseAgent ABC
│   │   ├── orchestrator.py  # Main Orchestrator
│   │   ├── task_manager.py  # Task Manager Agent
│   │   ├── storage.py       # Storage Agent
│   │   └── ui_controller.py # UI Controller Agent
│   ├── models/
│   │   ├── __init__.py
│   │   ├── messages.py      # AgentMessage, AgentResponse
│   │   ├── tasks.py         # Task model
│   │   └── exceptions.py    # Custom exceptions
│   └── skills/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_messages.py
│   │   ├── test_task_manager.py
│   │   └── test_storage.py
│   └── integration/
│       ├── __init__.py
│       └── test_orchestrator.py
└── specs/                    # Feature specifications
```

## Running the Application

### Start the Todo App

```bash
python -m src.main
```

You should see the Rich-formatted menu:

```
╔══════════════════════════════════╗
║       TODO APP - MAIN MENU       ║
╠══════════════════════════════════╣
║  1. Add Task                     ║
║  2. View All Tasks               ║
║  3. Update Task                  ║
║  4. Delete Task                  ║
║  5. Mark Task Complete           ║
║  6. Exit                         ║
╚══════════════════════════════════╝
Select option [1-6]:
```

### Basic Operations

**Add a Task:**
```
Select option: 1
Task title: Buy groceries
Description (optional): Milk, eggs, bread

✓ Task created with ID: 1
```

**View Tasks:**
```
Select option: 2

┌────┬────────────────┬──────────┬─────────────────────┐
│ ID │ Title          │ Complete │ Created             │
├────┼────────────────┼──────────┼─────────────────────┤
│  1 │ Buy groceries  │ ❌       │ 2025-01-03 10:30:00 │
└────┴────────────────┴──────────┴─────────────────────┘
```

**Mark Complete:**
```
Select option: 5
Task ID: 1

✓ Task 1 marked as complete
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=src --cov-report=html
```

View coverage report at `htmlcov/index.html`

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_task_manager.py -v
```

## Code Quality

### Run Linter

```bash
ruff check src/ tests/
```

### Auto-fix Lint Issues

```bash
ruff check src/ tests/ --fix
```

### Format Code

```bash
ruff format src/ tests/
```

### Run Type Checker

```bash
mypy src/
```

### Run All Quality Checks

```bash
ruff check src/ tests/ && ruff format src/ tests/ --check && mypy src/
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Write Tests First (TDD)

```python
# tests/unit/test_new_feature.py
def test_new_feature_does_something():
    # Arrange
    agent = TaskManagerAgent(storage=MockStorage())

    # Act
    result = agent.handle_message(message)

    # Assert
    assert result.status == "success"
```

### 3. Run Tests (Should Fail)

```bash
pytest tests/unit/test_new_feature.py -v
```

### 4. Implement Feature

```python
# src/agents/task_manager.py
def handle_new_action(self, payload: dict) -> AgentResponse:
    # Implementation
    ...
```

### 5. Run Tests (Should Pass)

```bash
pytest tests/unit/test_new_feature.py -v
```

### 6. Check Quality

```bash
ruff check src/ && mypy src/
```

### 7. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `uv venv` | Create virtual environment |
| `source .venv/bin/activate` | Activate venv (macOS/Linux) |
| `.\.venv\Scripts\activate` | Activate venv (Windows) |
| `uv pip install -e ".[dev]"` | Install all dependencies |
| `python -m src.main` | Run application |
| `pytest tests/ -v` | Run all tests |
| `pytest tests/ --cov=src` | Run tests with coverage |
| `ruff check src/` | Check code style |
| `ruff format src/` | Format code |
| `mypy src/` | Type check code |

## Troubleshooting

### UV Command Not Found

Ensure UV is in your PATH:
```bash
export PATH="$HOME/.cargo/bin:$PATH"  # macOS/Linux
```

### Module Import Errors

Ensure you installed in editable mode:
```bash
uv pip install -e ".[dev]"
```

### Rich Display Issues

If Rich output looks wrong, try:
```bash
export TERM=xterm-256color  # macOS/Linux
```

### Tests Can't Find Modules

Run pytest from project root:
```bash
cd hackathon-todo
pytest tests/ -v
```

## Next Steps

After completing this quickstart:

1. Review the agent contracts in `specs/001-multi-agent-architecture/contracts/`
2. Explore the data model in `specs/001-multi-agent-architecture/data-model.md`
3. Add new functionality by following the TDD workflow
4. Run `/sp.tasks` to generate implementation tasks
