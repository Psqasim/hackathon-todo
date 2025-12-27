# Implementation Plan: Multi-Agent Architecture System

**Branch**: `001-multi-agent-architecture` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-agent-architecture/spec.md`

## Summary

Implement a foundational multi-agent architecture system for the Todo application that will evolve through 5 hackathon phases. The system uses a Main Orchestrator Agent that coordinates three subagents (Task Manager, Storage, UI Controller) communicating via typed Pydantic message contracts. Phase I focuses on in-memory storage with a Rich console interface.

## Technical Context

**Language/Version**: Python 3.12+ (3.13+ preferred per hackathon spec)
**Primary Dependencies**: pydantic v2, rich, structlog
**Storage**: In-memory dictionary (Phase I); PostgreSQL via SQLModel (Phase II+)
**Testing**: pytest with pytest-asyncio, pytest-cov
**Target Platform**: Local development (macOS, Linux, Windows)
**Project Type**: Single project (src/ layout)
**Performance Goals**: Command response <500ms; System startup <2 seconds
**Constraints**: Single-user Phase I; synchronous communication with async-ready design
**Scale/Scope**: ~20 source files, ~1000 LOC, 4 agents, 5 core actions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Agent Architecture | ✅ PASS | Orchestrator + 3 focused subagents with typed contracts |
| II. Skill Reusability | ✅ PASS | Skills are stateless, technology-agnostic (deferred to later features) |
| III. Separation of Concerns | ✅ PASS | UI → Business Logic → Data layers strictly separated |
| IV. Evolution Strategy | ✅ PASS | Phase I scope; interfaces designed for Phase II+ evolution |
| V. Testing Standards | ✅ PASS | TDD, 80%+ coverage target, unit + integration tests |
| VI. Code Quality | ✅ PASS | Python 3.12+, UV, type hints, ruff, mypy |
| VII. Error Handling | ✅ PASS | Typed exceptions, Result pattern, correlation IDs |
| VIII. Spec-Driven Development | ✅ PASS | Spec → Plan → Tasks workflow followed |

**Gate Result**: PASS - All constitution principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-agent-architecture/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 technology decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Developer setup guide
├── contracts/           # Agent interface contracts
│   └── agent-contracts.md
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py                    # Application entry point
├── agents/
│   ├── __init__.py
│   ├── base.py                # BaseAgent ABC
│   ├── orchestrator.py        # Main Orchestrator Agent
│   ├── task_manager.py        # Task Manager Agent
│   ├── storage.py             # Storage Agent
│   └── ui_controller.py       # UI Controller Agent
├── models/
│   ├── __init__.py
│   ├── messages.py            # AgentMessage, AgentResponse
│   ├── tasks.py               # Task domain model
│   └── exceptions.py          # AgentError hierarchy
├── backends/
│   ├── __init__.py
│   └── memory.py              # InMemoryBackend
└── adapters/
    ├── __init__.py
    └── console.py             # Rich console adapter

tests/
├── __init__.py
├── conftest.py                # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_messages.py
│   ├── test_tasks.py
│   ├── test_exceptions.py
│   ├── test_task_manager.py
│   ├── test_storage.py
│   └── test_ui_controller.py
├── integration/
│   ├── __init__.py
│   ├── test_orchestrator.py
│   └── test_workflows.py
└── contract/
    └── __init__.py
```

**Structure Decision**: Single project layout (src/) selected because Phase I is a standalone console application. The structure supports clean migration to backend/frontend split in Phase II.

## Implementation Components

### Component 1: Project Foundation

**Files**: `pyproject.toml`, `src/__init__.py`, `.python-version`

**Description**:
- Configure UV project with Python 3.12+
- Define production dependencies: pydantic>=2.5, rich>=13.0, structlog>=24.0
- Define dev dependencies: pytest>=8.0, pytest-asyncio>=0.23, pytest-cov>=4.1, ruff>=0.1, mypy>=1.8
- Configure ruff (extends = "pyproject.toml"), mypy (strict = true)
- Create src package __init__.py with version

**Ref**: Constitution VI (Code Quality), research.md

### Component 2: Message Models

**Files**: `src/models/messages.py`

**Description**:
- `AgentMessage`: Pydantic model with request_id, sender, recipient, action, payload, timestamp, correlation_id
- `AgentResponse`: Pydantic model with request_id, sender, status, result, error, timestamp
- `AgentInfo`: Pydantic model for agent registration
- UUID4 default factories for request_id
- Validators for non-empty strings, valid status enum

**Ref**: spec.md FR-025 to FR-029, data-model.md

### Component 3: Task Model

**Files**: `src/models/tasks.py`

**Description**:
- `Task`: Pydantic model with id, title, description, completed, created_at, updated_at
- Title validator: 1-200 characters, required
- Description validator: max 1000 characters, optional
- Factory methods: `create()`, `complete()`, `update()`
- Serialization to dict for storage

**Ref**: spec.md Key Entities, data-model.md

### Component 4: Exception Hierarchy

**Files**: `src/models/exceptions.py`

**Description**:
- `AgentError(Exception)`: Base exception
- `ValidationError(AgentError)`: Invalid input
- `NotFoundError(AgentError)`: Entity not found
- `StorageError(AgentError)`: Persistence failure
- `RoutingError(AgentError)`: Unknown action/agent
- `AgentInitError(AgentError)`: Startup failure
- All include correlation_id attribute

**Ref**: Constitution VII (Error Handling), data-model.md

### Component 5: Base Agent

**Files**: `src/agents/base.py`

**Description**:
- `BaseAgent(ABC)`: Abstract base class
- Constructor: name, logger (structlog)
- Abstract method: `handle_message(message: AgentMessage) -> AgentResponse`
- Default methods: `start()`, `shutdown()`, `is_running`
- Protected: `_create_response()` helper for consistent responses

**Ref**: spec.md FR-001 to FR-007, contracts/agent-contracts.md

### Component 6: Storage Backend Protocol

**Files**: `src/backends/__init__.py`, `src/backends/memory.py`

**Description**:
- `StorageBackend(Protocol)`: Interface for persistence
- Methods: `save()`, `get()`, `delete()`, `list()`, `query()`
- `InMemoryBackend`: Dict-based implementation
- Auto-incrementing ID counter
- Thread-safe with asyncio.Lock placeholder

**Ref**: spec.md FR-014 to FR-019, research.md

### Component 7: Storage Agent

**Files**: `src/agents/storage.py`

**Description**:
- `StorageAgent(BaseAgent)`: Persistence operations
- Constructor accepts `StorageBackend` (dependency injection)
- Actions: storage_save, storage_get, storage_delete, storage_list, storage_query
- Delegates all operations to backend
- Returns structured responses

**Ref**: spec.md FR-014 to FR-019, contracts/agent-contracts.md

### Component 8: Task Manager Agent

**Files**: `src/agents/task_manager.py`

**Description**:
- `TaskManagerAgent(BaseAgent)`: Business logic
- Constructor accepts `StorageAgent` (dependency injection)
- Actions: task_add, task_delete, task_update, task_list, task_get, task_complete
- Validates task data before storage
- Enforces business rules (title required, etc.)

**Ref**: spec.md FR-008 to FR-013, contracts/agent-contracts.md

### Component 9: UI Adapter Protocol

**Files**: `src/adapters/__init__.py`, `src/adapters/console.py`

**Description**:
- `UIAdapter(Protocol)`: Interface for UI implementations
- Methods: `display()`, `prompt()`, `confirm()`, `menu()`
- `ConsoleAdapter`: Rich-based implementation
- Rich Panel for menus
- Rich Table for task lists
- Rich Prompt for input

**Ref**: spec.md FR-020 to FR-024, research.md

### Component 10: UI Controller Agent

**Files**: `src/agents/ui_controller.py`

**Description**:
- `UIControllerAgent(BaseAgent)`: User interaction
- Constructor accepts `UIAdapter` (dependency injection)
- Actions: ui_show_menu, ui_show_tasks, ui_get_input, ui_show_message, ui_confirm
- Formats errors for user display
- Delegates rendering to adapter

**Ref**: spec.md FR-020 to FR-024, contracts/agent-contracts.md

### Component 11: Main Orchestrator

**Files**: `src/agents/orchestrator.py`

**Description**:
- `OrchestratorAgent(BaseAgent)`: Master coordinator
- Agent registry: `Dict[str, BaseAgent]`
- Methods: `register_agent()`, `get_agent()`, `list_agents()`
- Routing logic: action prefix → agent name mapping
- Error handling: catches all agent errors, returns structured response
- System actions: system_status, system_shutdown

**Ref**: spec.md FR-001 to FR-007, contracts/agent-contracts.md

### Component 12: Application Entry Point

**Files**: `src/main.py`

**Description**:
- Configure structlog (dev-friendly console output)
- Startup sequence: Storage → TaskManager → UIController → Orchestrator
- Register all agents with Orchestrator
- Main loop: menu → input → message → route → response → display
- Graceful shutdown on exit or Ctrl+C
- Entry point: `if __name__ == "__main__"`

**Ref**: spec.md FR-030 to FR-033, quickstart.md

### Component 13: Test Fixtures

**Files**: `tests/conftest.py`

**Description**:
- `@pytest.fixture mock_storage_backend`: InMemoryBackend instance
- `@pytest.fixture mock_storage_agent`: StorageAgent with mock backend
- `@pytest.fixture mock_ui_adapter`: UIAdapter mock (no output)
- `@pytest.fixture task_manager`: TaskManagerAgent with mock storage
- `@pytest.fixture orchestrator`: Full agent setup for integration tests
- `@pytest.fixture sample_task`: Pre-created Task for testing

**Ref**: Constitution V (Testing Standards)

### Component 14: Unit Tests - Models

**Files**: `tests/unit/test_messages.py`, `tests/unit/test_tasks.py`, `tests/unit/test_exceptions.py`

**Description**:
- Test AgentMessage creation and validation
- Test AgentResponse success and error states
- Test Task creation, validation, serialization
- Test exception hierarchy and correlation_id
- Test edge cases: empty title, long description, invalid status

**Ref**: Constitution V (Testing Standards)

### Component 15: Unit Tests - Agents

**Files**: `tests/unit/test_task_manager.py`, `tests/unit/test_storage.py`, `tests/unit/test_ui_controller.py`

**Description**:
- Test each agent action independently
- Mock dependencies using fixtures
- Test success paths and error paths
- Test input validation
- Test response format compliance

**Ref**: Constitution V (Testing Standards)

### Component 16: Integration Tests

**Files**: `tests/integration/test_orchestrator.py`, `tests/integration/test_workflows.py`

**Description**:
- Test agent registration and routing
- Test complete workflows: add task → list → complete → delete
- Test error propagation through orchestrator
- Test startup and shutdown sequences
- Test unknown action handling

**Ref**: Constitution V (Testing Standards), spec.md User Stories

## Dependency Graph

```
Component 1 (Foundation)
    │
    ├──▶ Component 2 (Messages)
    │        │
    ├──▶ Component 3 (Task Model)
    │        │
    └──▶ Component 4 (Exceptions)
             │
             ▼
Component 5 (Base Agent) ◀── depends on 2, 4
    │
    ├──▶ Component 6 (Storage Backend)
    │        │
    │        ▼
    ├──▶ Component 7 (Storage Agent) ◀── depends on 5, 6
    │        │
    │        ▼
    ├──▶ Component 8 (Task Manager) ◀── depends on 5, 7, 3
    │
    ├──▶ Component 9 (UI Adapter)
    │        │
    │        ▼
    ├──▶ Component 10 (UI Controller) ◀── depends on 5, 9
    │
    └──▶ Component 11 (Orchestrator) ◀── depends on 5, 7, 8, 10
             │
             ▼
Component 12 (Entry Point) ◀── depends on 11, all agents

Component 13-16 (Tests) ◀── depends on all source components
```

## Testing Strategy

### Unit Tests

| Component | Test Count (Est.) | Coverage Target |
|-----------|------------------|-----------------|
| Messages | 8 | 95% |
| Task Model | 6 | 95% |
| Exceptions | 4 | 100% |
| Base Agent | 3 | 90% |
| Storage Backend | 6 | 95% |
| Storage Agent | 8 | 90% |
| Task Manager | 12 | 95% |
| UI Controller | 6 | 85% |
| Orchestrator | 10 | 90% |

### Integration Tests

| Workflow | Test Count (Est.) |
|----------|------------------|
| Full task lifecycle | 4 |
| Error propagation | 4 |
| Startup/shutdown | 3 |
| Unknown action handling | 2 |

### Coverage Goals

- Overall: 80%+
- Critical paths (task operations, routing): 95%+
- Models: 95%+

## Error Handling Strategy

```
User Input
    │
    ▼
UI Controller
    │ catches UI errors
    │ returns validation message
    ▼
Orchestrator
    │ catches routing errors
    │ catches agent errors
    │ adds correlation_id
    ▼
Task Manager
    │ catches validation errors
    │ catches storage errors
    │ returns structured response
    ▼
Storage Agent
    │ catches backend errors
    │ wraps in StorageError
    ▼
Storage Backend
    │ raises raw exceptions
```

All errors:
1. Logged with structlog (correlation_id, agent_name, action)
2. Transformed to AgentResponse with status="error"
3. Displayed to user via UI Controller
4. System remains operational

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Sync-to-async breaks code | Use async-compatible signatures from start |
| Storage swap breaks data | Comprehensive integration tests |
| Rich not available | Graceful fallback to plain text |
| Circular imports | Protocols/ABCs defined in separate modules |

## Phase II Evolution Notes

When transitioning to Phase II:

1. **Storage Agent**: Replace InMemoryBackend with PostgresBackend
   - Same interface, new implementation
   - Migration script for existing data

2. **UI Controller**: Add WebAdapter
   - Same UIAdapter protocol
   - Orchestrator unchanged

3. **New Agent**: AuthenticationAgent
   - Register with Orchestrator
   - Add auth_* action prefix

4. **API Layer**: FastAPI wrapper
   - Receives HTTP requests
   - Creates AgentMessage
   - Routes through Orchestrator

## Complexity Tracking

> No complexity violations - architecture aligns with constitution.

| Principle | Actual | Limit | Status |
|-----------|--------|-------|--------|
| Agents | 4 | N/A | OK |
| Actions per agent | 5-6 | 10 | OK |
| Dependencies per agent | 1-2 | 3 | OK |
| File length | <200 LOC | 300 | OK |
| Function length | <25 LOC | 50 | OK |
