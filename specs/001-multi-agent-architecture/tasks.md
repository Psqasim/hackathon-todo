# Tasks: Multi-Agent Architecture System

**Input**: Design documents from `/specs/001-multi-agent-architecture/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/agent-contracts.md

**Tests**: Included per Constitution V (Testing Standards) - TDD approach with 80%+ coverage target.

**Organization**: Tasks organized by dependency layers as specified, with user story mapping for traceability.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1-US5 maps to User Stories from spec.md
- **Complexity**: (L)ow, (M)edium, (H)igh

## Path Conventions

- **Project Type**: Single project with `src/`, `tests/` at repository root
- **Structure**: As defined in plan.md Component 1

---

## Phase 1: Setup - Project Foundation (Layer 1)

**Purpose**: UV project initialization and basic structure
**Complexity**: Low | **Est. Tasks**: 5

- [ ] T001 Create pyproject.toml with UV configuration, Python 3.12+ requirement, production dependencies (pydantic>=2.5, rich>=13.0, structlog>=24.0), and dev dependencies (pytest>=8.0, pytest-asyncio>=0.23, pytest-cov>=4.1, ruff>=0.1, mypy>=1.8)

- [ ] T002 Create .python-version file specifying Python 3.12

- [ ] T003 [P] Create directory structure: src/, src/agents/, src/models/, src/backends/, src/adapters/, tests/, tests/unit/, tests/integration/, tests/contract/

- [ ] T004 [P] Create src/__init__.py with version="0.1.0" and package metadata

- [ ] T005 [P] Configure ruff.toml and mypy settings in pyproject.toml (strict=true, exclude tests from some strict checks)

**Checkpoint**: `uv sync` succeeds, `uv run python -c "import src"` works

---

## Phase 2: Foundational Models (Layer 2)

**Purpose**: Core Pydantic models that all agents depend on
**Complexity**: Medium | **Est. Tasks**: 9

### Message Models (Component 2)

- [ ] T006 [P] Create src/models/__init__.py with public exports

- [ ] T007 [P] Create src/models/messages.py with AgentMessage Pydantic model: request_id (UUID4 default), sender (str), recipient (str), action (str), payload (dict[str, Any]), timestamp (datetime default), correlation_id (str). Add validators for non-empty strings.

- [ ] T008 Create AgentResponse Pydantic model in src/models/messages.py: request_id (str), sender (str), status (Literal["success", "error"]), result (Any | None), error (str | None), timestamp (datetime default). Add validator ensuring result XOR error based on status.

- [ ] T009 Create AgentInfo Pydantic model in src/models/messages.py: name (str), status (Literal["active", "inactive", "error"]), version (str with semver pattern), supported_actions (list[str])

### Task Model (Component 3)

- [ ] T010 [P] Create src/models/tasks.py with Task Pydantic model: id (int | None), title (str 1-200 chars), description (str | None max 1000), completed (bool default False), created_at (datetime), updated_at (datetime). Add factory methods create(), complete(), update().

### Exception Hierarchy (Component 4)

- [ ] T011 [P] Create src/models/exceptions.py with AgentError(Exception) base class including correlation_id attribute

- [ ] T012 Create ValidationError(AgentError) for invalid input data in src/models/exceptions.py

- [ ] T013 Create NotFoundError(AgentError), StorageError(AgentError), RoutingError(AgentError), AgentInitError(AgentError) in src/models/exceptions.py

### Unit Tests for Models

- [ ] T014 [P] Create tests/__init__.py and tests/unit/__init__.py

- [ ] T015 [P] Create tests/unit/test_messages.py with tests for AgentMessage (creation, UUID generation, validation), AgentResponse (success/error states, XOR validation), AgentInfo (semver validation)

- [ ] T016 [P] Create tests/unit/test_tasks.py with tests for Task (creation, title validation, description max length, factory methods, serialization)

- [ ] T017 [P] Create tests/unit/test_exceptions.py with tests for exception hierarchy and correlation_id propagation

**Checkpoint**: `uv run pytest tests/unit/test_messages.py tests/unit/test_tasks.py tests/unit/test_exceptions.py` passes

---

## Phase 3: Base Agent & Storage Backend (Layer 3)

**Purpose**: BaseAgent ABC and StorageBackend Protocol
**Complexity**: Medium | **Est. Tasks**: 8

### Base Agent (Component 5)

- [ ] T018 Create src/agents/__init__.py with public exports

- [ ] T019 Create src/agents/base.py with BaseAgent(ABC): name property, version property, supported_actions list, abstract handle_message(message: AgentMessage) -> AgentResponse, start() method, shutdown() method, is_running property, protected _create_response() helper

- [ ] T020 [P] Create tests/unit/test_base_agent.py with tests for BaseAgent contract (cannot instantiate, subclass must implement handle_message)

### Storage Backend Protocol (Component 6)

- [ ] T021 [P] Create src/backends/__init__.py with StorageBackend Protocol defining: save(entity_type, data) -> dict, get(entity_type, entity_id) -> dict | None, delete(entity_type, entity_id) -> bool, list(entity_type) -> list[dict], query(entity_type, filters) -> list[dict]

- [ ] T022 Create src/backends/memory.py with InMemoryBackend implementing StorageBackend: Dict[str, Dict[int, dict]] storage, auto-increment ID counter per entity_type, asyncio.Lock for thread safety placeholder

- [ ] T023 [P] Create tests/unit/test_memory_backend.py with tests for InMemoryBackend: save generates ID, get returns entity, delete removes entity, list returns all, query filters correctly, ID auto-increment, non-existent ID handling

### Test Fixtures (Component 13)

- [ ] T024 Create tests/conftest.py with fixtures: mock_storage_backend (InMemoryBackend), sample_task (pre-created Task dict)

**Checkpoint**: `uv run pytest tests/unit/` passes with all Layer 2-3 tests

---

## Phase 4: User Story 1 - Command Routing and Execution (Priority: P1) 🎯 MVP

**Goal**: Main Orchestrator routes commands to correct subagents
**Independent Test**: Issue commands through test interface, verify correct agent handles them

**Complexity**: High | **Est. Tasks**: 18

### Storage Agent (Component 7)

- [ ] T025 [US1] Create src/agents/storage.py with StorageAgent(BaseAgent): accepts StorageBackend via dependency injection, name="storage_agent", version="1.0.0", supported_actions=["storage_save", "storage_get", "storage_delete", "storage_list", "storage_query"]

- [ ] T026 [US1] Implement handle_message() in StorageAgent that routes to internal methods: _handle_save, _handle_get, _handle_delete, _handle_list, _handle_query. Each returns AgentResponse with success/error status.

- [ ] T027 [P] [US1] Create tests/unit/test_storage_agent.py with tests for each action: storage_save persists and returns entity with ID, storage_get retrieves by ID, storage_delete removes entity, storage_list returns all, storage_query filters correctly, unknown action returns error

### Task Manager Agent (Component 8)

- [ ] T028 [US1] Create src/agents/task_manager.py with TaskManagerAgent(BaseAgent): accepts StorageAgent via dependency injection, name="task_manager", version="1.0.0", supported_actions=["task_add", "task_delete", "task_update", "task_list", "task_get", "task_complete"]

- [ ] T029 [US1] Implement task_add in TaskManagerAgent: validate title (1-200 chars, required), description (max 1000), create Task, delegate storage_save to StorageAgent, return task

- [ ] T030 [US1] Implement task_delete, task_get in TaskManagerAgent: validate task_id, delegate to StorageAgent, handle NotFoundError

- [ ] T031 [US1] Implement task_update in TaskManagerAgent: validate task_id and fields, merge updates, update updated_at, delegate storage_save

- [ ] T032 [US1] Implement task_list in TaskManagerAgent: accept optional filter (completed), delegate storage_list or storage_query, return tasks

- [ ] T033 [US1] Implement task_complete in TaskManagerAgent: get task, toggle completed, update updated_at, delegate storage_save, return updated task

- [ ] T034 [P] [US1] Create tests/unit/test_task_manager.py with tests for each action: task_add creates task, task_delete removes, task_update modifies, task_list returns all, task_get retrieves, task_complete toggles, validation errors for invalid input

- [ ] T035 [US1] Add fixture task_manager to tests/conftest.py: TaskManagerAgent with mock StorageAgent

### Main Orchestrator (Component 11)

- [ ] T036 [US1] Create src/agents/orchestrator.py with OrchestratorAgent(BaseAgent): agent registry Dict[str, BaseAgent], name="orchestrator", version="1.0.0"

- [ ] T037 [US1] Implement register_agent(agent: BaseAgent) in OrchestratorAgent: validate unique name, add to registry, log registration

- [ ] T038 [US1] Implement get_agent(name: str), list_agents() in OrchestratorAgent

- [ ] T039 [US1] Implement route_message(message: AgentMessage) -> AgentResponse: parse action prefix (task_, storage_, ui_, system_), lookup agent, forward message, catch errors, add correlation_id

- [ ] T040 [US1] Implement system_status action: return health of all agents, uptime

- [ ] T041 [US1] Implement system_shutdown action: initiate graceful shutdown sequence

- [ ] T042 [P] [US1] Create tests/integration/test_orchestrator.py with tests for: agent registration, routing task_* to task_manager, routing storage_* to storage_agent, unknown action returns RoutingError, system_status returns health

**Checkpoint**: `uv run pytest tests/unit/test_storage_agent.py tests/unit/test_task_manager.py tests/integration/test_orchestrator.py` passes - Command routing verified

---

## Phase 5: User Story 2 - Graceful Error Handling (Priority: P2)

**Goal**: System handles errors gracefully with clear messages and correlation IDs
**Independent Test**: Cause deliberate errors, verify helpful feedback and system stability

**Complexity**: Medium | **Est. Tasks**: 8

- [ ] T043 [US2] Enhance StorageAgent error handling: wrap backend exceptions in StorageError, include correlation_id from message

- [ ] T044 [US2] Enhance TaskManagerAgent error handling: catch ValidationError for bad input, catch StorageError from storage, catch NotFoundError, always return structured AgentResponse

- [ ] T045 [US2] Enhance OrchestratorAgent error handling: catch RoutingError for unknown actions, catch AgentError from subagents, catch unexpected exceptions, log all with correlation_id

- [ ] T046 [US2] Implement error message formatting: "[ErrorType]: Human readable message" format, include correlation_id in error responses

- [ ] T047 [P] [US2] Create tests/integration/test_error_handling.py with tests for: invalid task data returns ValidationError, non-existent task returns NotFoundError, storage failure returns StorageError, unknown action returns RoutingError, correlation_id present in all errors

- [ ] T048 [US2] Add structlog configuration to src/agents/base.py: bind agent_name, correlation_id to logger context

- [ ] T049 [US2] Ensure all agents log errors with structlog: level=error for failures, level=warning for validation, level=info for operations

- [ ] T050 [P] [US2] Test system stability after errors: verify system continues operating after any single agent error

**Checkpoint**: All error scenarios tested, system remains operational after errors

---

## Phase 6: User Story 3 - Agent Independence and Testability (Priority: P3)

**Goal**: Each agent independently testable with mock dependencies
**Independent Test**: Instantiate each agent in isolation, verify contract compliance

**Complexity**: Medium | **Est. Tasks**: 6

- [ ] T051 [US3] Ensure all agent dependencies use Protocol/ABC: StorageAgent accepts StorageBackend Protocol, TaskManagerAgent accepts storage agent via interface, UIControllerAgent accepts UIAdapter Protocol

- [ ] T052 [P] [US3] Create tests/contract/__init__.py

- [ ] T053 [P] [US3] Create tests/contract/test_agent_contracts.py with tests for each agent: can instantiate with mock dependencies, handle_message matches contract (returns AgentResponse), supported_actions list is complete

- [ ] T054 [US3] Verify backend swappability: create MockStorageBackend implementing StorageBackend Protocol, test TaskManagerAgent works with both InMemoryBackend and MockStorageBackend without modification

- [ ] T055 [US3] Document agent contracts in docstrings: input/output schemas per action, error conditions, dependencies

- [ ] T056 [P] [US3] Create tests verifying schema validation: send valid data matching schema → processed, send invalid data → ValidationError before processing

**Checkpoint**: Each agent passes contract tests in complete isolation

---

## Phase 7: User Story 4 - System Lifecycle Management (Priority: P4)

**Goal**: Application starts up and shuts down gracefully
**Independent Test**: Start system, perform operations, shutdown, verify no data loss

**Complexity**: Medium | **Est. Tasks**: 7

### UI Adapter and Controller (Components 9, 10)

- [ ] T057 [US4] Create src/adapters/__init__.py with UIAdapter Protocol: display(content, style), prompt(message, default), confirm(message), menu(title, options)

- [ ] T058 [US4] Create src/adapters/console.py with ConsoleAdapter implementing UIAdapter using Rich: Panel for menus, Table for task lists, Prompt for input, Confirm for yes/no

- [ ] T059 [US4] Create src/agents/ui_controller.py with UIControllerAgent(BaseAgent): accepts UIAdapter via dependency injection, supported_actions=["ui_show_menu", "ui_show_tasks", "ui_get_input", "ui_show_message", "ui_confirm"]

- [ ] T060 [US4] Implement all UIControllerAgent actions per contracts/agent-contracts.md

### Application Entry Point (Component 12)

- [ ] T061 [US4] Create src/main.py with main() function: configure structlog, startup sequence (create InMemoryBackend → StorageAgent → TaskManagerAgent → ConsoleAdapter → UIControllerAgent → OrchestratorAgent), register all agents

- [ ] T062 [US4] Implement main loop in src/main.py: show menu → get selection → create AgentMessage → route through orchestrator → display result → repeat until exit

- [ ] T063 [US4] Implement graceful shutdown: catch KeyboardInterrupt, call orchestrator.shutdown(), ensure all pending operations complete

- [ ] T064 [P] [US4] Create tests/integration/test_lifecycle.py with tests for: startup completes in <2 seconds, all agents registered after startup, shutdown completes pending operations, startup failure logged and prevented

**Checkpoint**: `uv run python -m src.main` starts, operates, and shuts down gracefully

---

## Phase 8: User Story 5 - Cross-Phase Evolution Support (Priority: P5)

**Goal**: Architecture supports Phase II+ evolution without rework
**Independent Test**: Simulate adding new interface/backend, verify no core changes needed

**Complexity**: Low | **Est. Tasks**: 5

- [ ] T065 [US5] Verify UIAdapter Protocol allows web adapter: document how to add WebAdapter without changing UIControllerAgent

- [ ] T066 [US5] Verify StorageBackend Protocol allows PostgreSQL: document how to add PostgresBackend without changing TaskManagerAgent

- [ ] T067 [P] [US5] Create tests/integration/test_evolution.py with tests for: adding mock WebAdapter works with same UIControllerAgent, adding mock PostgresBackend works with same StorageAgent

- [ ] T068 [US5] Document Phase II migration path in code comments: where to add AuthenticationAgent, where to add API layer

- [ ] T069 [US5] Verify orchestrator supports new agent registration at runtime: register new agent, verify it receives routed messages

**Checkpoint**: Evolution tests pass, migration path documented

---

## Phase 9: Polish & Integration (Layer 6)

**Purpose**: Full workflow tests, documentation, quality checks
**Complexity**: Medium | **Est. Tasks**: 8

- [ ] T070 Create tests/integration/test_workflows.py with full lifecycle tests: add task → list tasks → complete task → delete task, all through orchestrator

- [ ] T071 [P] Run full test suite with coverage: `uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80`

- [ ] T072 [P] Run ruff linting: `uv run ruff check src/ tests/`

- [ ] T073 [P] Run mypy type checking: `uv run mypy src/`

- [ ] T074 Fix any linting or type errors identified

- [ ] T075 [P] Add mock_ui_adapter fixture to tests/conftest.py for UIAdapter testing

- [ ] T076 [P] Create tests/unit/test_ui_controller.py with tests for ui_* actions using mock adapter

- [ ] T077 Validate against quickstart.md: verify all documented commands work

**Checkpoint**: All tests pass, 80%+ coverage, no lint/type errors

---

## Dependencies & Execution Order

### Layer Dependencies (As Specified)

```
Layer 1: Foundation (Setup)
    ↓
Layer 2: Models (Messages, Task, Exceptions)
    ↓
Layer 3: Base Agent & Storage Backend
    ↓
Layer 4: Business Logic Agents [PARALLEL]
    ├── Storage Agent
    ├── Task Manager Agent
    └── UI Controller Agent
    ↓
Layer 5: Orchestration (requires all Layer 4 agents)
    ↓
Layer 6: Quality & Documentation
```

### User Story Dependencies

- **US1 (P1)**: Requires Layer 2-3 complete → Core routing MVP
- **US2 (P2)**: Can parallel with US1 implementation → Error handling
- **US3 (P3)**: Requires US1 agents exist → Contract verification
- **US4 (P4)**: Requires US1 complete → Lifecycle management
- **US5 (P5)**: Requires US1-US4 complete → Evolution verification

### Parallel Opportunities by Phase

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel
**Phase 2 (Models)**: T006, T007, T010, T011, T014, T015, T016, T017 can run in parallel
**Phase 3 (Base)**: T020, T021, T023 can run in parallel
**Phase 4 (US1)**: T027, T034, T042 (tests) can run in parallel
**Phase 5 (US2)**: T047, T050 can run in parallel
**Phase 6 (US3)**: T052, T053, T056 can run in parallel
**Phase 7 (US4)**: T064 can parallel with other tests
**Phase 8 (US5)**: T067 can run in parallel
**Phase 9 (Polish)**: T071, T072, T073, T075, T076 can run in parallel

---

## Parallel Example: Layer 4 Agents

```bash
# After Layer 3 complete, launch agent implementations in parallel:

# Developer A: Storage Agent
Task: T025 "Create src/agents/storage.py with StorageAgent"
Task: T026 "Implement handle_message() in StorageAgent"
Task: T027 "Create tests/unit/test_storage_agent.py"

# Developer B: Task Manager Agent (can start once T025 complete for dependency)
Task: T028 "Create src/agents/task_manager.py with TaskManagerAgent"
Task: T029-T033 "Implement task_* actions"
Task: T034 "Create tests/unit/test_task_manager.py"

# Developer C: Orchestrator (can start once T025, T028 complete)
Task: T036-T041 "Orchestrator implementation"
Task: T042 "Create tests/integration/test_orchestrator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational Models
3. Complete Phase 3: Base Agent & Storage Backend
4. Complete Phase 4: User Story 1 (Command Routing)
5. **STOP and VALIDATE**: Run `uv run pytest` - all US1 tests pass
6. Run `uv run python -m src.main` - basic operation works

### Incremental Delivery

| Milestone | Phases | Deliverable |
|-----------|--------|-------------|
| Foundation Ready | 1-3 | Models, Base Agent, Storage Backend |
| MVP (US1) | 4 | Command routing works |
| Robust (US2) | 5 | Error handling complete |
| Testable (US3) | 6 | Contract tests pass |
| Production (US4) | 7 | Full lifecycle management |
| Evolvable (US5) | 8 | Phase II ready |
| Polished | 9 | 80%+ coverage, lint clean |

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 77 |
| **Setup Tasks** | 5 |
| **Foundational Tasks** | 12 |
| **US1 Tasks (P1)** | 18 |
| **US2 Tasks (P2)** | 8 |
| **US3 Tasks (P3)** | 6 |
| **US4 Tasks (P4)** | 8 |
| **US5 Tasks (P5)** | 5 |
| **Polish Tasks** | 8 |
| **Parallel Opportunities** | 35 tasks marked [P] |
| **Est. Source Files** | ~20 |
| **Est. Test Files** | ~12 |
| **Coverage Target** | 80%+ |

---

## Notes

- All tasks include exact file paths as specified
- [P] tasks can run in parallel (different files, no dependencies)
- [US#] labels map to User Stories from spec.md
- Tests written FIRST per TDD approach (Constitution V)
- Commit after each task or logical group
- Validate at each checkpoint before proceeding
