# Research: Multi-Agent Architecture System

**Feature**: 001-multi-agent-architecture
**Date**: 2025-12-26
**Status**: Complete

## Technology Decisions

### 1. Python Version

**Decision**: Python 3.12+

**Rationale**:
- Constitution mandates Python 3.12+ (3.13+ preferred)
- Python 3.12 provides improved error messages, faster startup
- Type hints fully supported for Pydantic v2 compatibility
- UV package manager requires Python 3.8+, so 3.12 is well-supported

**Alternatives Considered**:
- Python 3.11: Rejected - doesn't meet constitution requirement
- Python 3.13: Preferred but 3.12 is more stable baseline

### 2. Async vs Sync Communication

**Decision**: Synchronous communication for Phase I with async-ready design

**Rationale**:
- Spec assumption #2: "Phase I uses synchronous agent communication"
- Simpler to implement and debug in Phase I console app
- Design uses async signatures to enable future evolution
- Phase II/III can transition to full async without interface changes

**Alternatives Considered**:
- Full async from start: Rejected - unnecessary complexity for single-user console app
- Thread-based: Rejected - Python GIL limits, async is better path forward

### 3. Message Passing Implementation

**Decision**: Direct method calls with typed message/response objects (no queues in Phase I)

**Rationale**:
- Phase I is single-user, single-process, synchronous
- asyncio.Queue adds complexity without benefit until Phase II+
- AgentMessage/AgentResponse Pydantic models provide type safety
- Easy to add queue layer later without changing agent contracts

**Alternatives Considered**:
- asyncio.Queue from start: Rejected - over-engineering for Phase I
- Redis queues: Rejected - external dependency not needed until Phase III+

### 4. Dependency Injection Pattern

**Decision**: Constructor injection with Protocol/ABC interfaces

**Rationale**:
- Constitution requires agents be independently testable
- Constructor injection makes dependencies explicit
- Protocol/ABC allows mocking in tests
- No DI framework needed - simple constructor parameters suffice

**Alternatives Considered**:
- Service locator pattern: Rejected - hidden dependencies, harder to test
- Dependency injection framework (inject, dependency-injector): Rejected - overkill for Phase I

### 5. Console UI Library

**Decision**: Rich library

**Rationale**:
- Beautiful console output with minimal code
- Tables, panels, progress bars, syntax highlighting
- Cross-platform compatibility (Windows, macOS, Linux)
- No terminal escape code issues
- Active maintenance and community support

**Alternatives Considered**:
- Click prompts: Limited formatting, basic output
- Typer: Built on Click, same limitations for output
- Textual (TUI): Full TUI is over-engineering for menu-based app
- Plain print(): Ugly, no formatting

### 6. Structured Logging Library

**Decision**: structlog

**Rationale**:
- Constitution requires structured logging (JSON in production)
- Integrates cleanly with standard logging
- Context binding (correlation_id, agent_name) built-in
- Human-readable dev mode, JSON production mode
- Type-safe processors

**Alternatives Considered**:
- Python logging + JSON formatter: More manual setup, less ergonomic
- loguru: Good but less structured by default
- Custom solution: Not worth reinventing

### 7. Data Validation Library

**Decision**: Pydantic v2

**Rationale**:
- Constitution mandates Pydantic for agent contracts
- V2 is significantly faster than v1
- Native TypedDict support
- Model serialization/deserialization built-in
- Excellent error messages for validation failures

**Alternatives Considered**:
- Pydantic v1: Rejected - v2 is current, faster
- dataclasses + validators: More code, less validation features
- attrs + cattrs: Good but Pydantic is standard for Python APIs

### 8. Testing Framework

**Decision**: pytest with pytest-asyncio

**Rationale**:
- pytest is Python testing standard
- pytest-asyncio enables async test support for future phases
- Excellent fixture system for dependency injection testing
- pytest-cov for coverage reporting
- Rich plugin ecosystem

**Alternatives Considered**:
- unittest: Verbose, less ergonomic fixtures
- nose2: Less active development than pytest

### 9. Code Quality Tools

**Decision**: Ruff (linting + formatting) + mypy (type checking)

**Rationale**:
- Ruff is extremely fast (10-100x faster than flake8)
- Ruff replaces multiple tools (flake8, isort, pyupgrade, black)
- mypy strict mode catches type errors early
- Both integrate well with pre-commit hooks

**Alternatives Considered**:
- Black + flake8 + isort: Multiple tools, slower, more config
- pylint: Slower, more opinionated than ruff
- pyright: Good but mypy has broader adoption

### 10. Project/Package Manager

**Decision**: UV

**Rationale**:
- Constitution mandates UV (not pip)
- Extremely fast dependency resolution
- Handles venv creation and management
- Compatible with pyproject.toml
- Cross-platform support

**Alternatives Considered**:
- pip + venv: Constitution explicitly forbids
- Poetry: Slower than UV, more complex
- Conda: Overkill for pure Python project

## Architecture Patterns

### Agent Base Class Design

**Decision**: Abstract Base Class (ABC) with default implementations

```python
class BaseAgent(ABC):
    """Abstract base for all agents."""

    def __init__(self, name: str, logger: StructLogger | None = None):
        self.name = name
        self._logger = logger or structlog.get_logger().bind(agent=name)
        self._running = False

    @abstractmethod
    def handle_message(self, message: AgentMessage) -> AgentResponse:
        """Process incoming message - must be implemented by subclasses."""
        pass

    def start(self) -> None:
        """Start agent - can be overridden."""
        self._running = True
        self._logger.info("agent_started")

    def shutdown(self) -> None:
        """Shutdown agent - can be overridden."""
        self._running = False
        self._logger.info("agent_shutdown")
```

**Rationale**:
- Abstract method for handle_message enforces contract
- Default start/shutdown reduces boilerplate
- Logger injection enables testing without side effects

### Routing Strategy

**Decision**: Action prefix-based routing in Orchestrator

| Prefix | Agent |
|--------|-------|
| `task_*` | Task Manager Agent |
| `storage_*` | Storage Agent |
| `ui_*` | UI Controller Agent |

**Rationale**:
- Simple, predictable routing rules
- No complex registration or discovery
- Easy to test and debug
- Extensible for new agents (add new prefix)

### Error Handling Strategy

**Decision**: Typed exception hierarchy with Result pattern in responses

```python
# Exception hierarchy
class AgentError(Exception): pass
class ValidationError(AgentError): pass
class NotFoundError(AgentError): pass
class StorageError(AgentError): pass

# Response always returns, never raises to caller
def handle_message(self, msg: AgentMessage) -> AgentResponse:
    try:
        result = self._process(msg)
        return AgentResponse(status="success", result=result, ...)
    except AgentError as e:
        self._logger.error("agent_error", error=str(e))
        return AgentResponse(status="error", error=str(e), ...)
```

**Rationale**:
- Agents never crash - they return error responses
- Typed exceptions enable specific handling
- Correlation ID in response enables tracing
- Orchestrator transforms errors for user display

## Open Questions Resolved

### Q1: Should agents use async/await in Phase I?

**Resolution**: Use sync methods with async-compatible signatures.

Phase I implementation uses synchronous code, but method signatures use `async def` to enable seamless transition to async in Phase II. This means:
- Phase I: `await agent.handle_message(msg)` works, just runs synchronously
- Phase II+: Same code, truly async execution

### Q2: How to handle Storage Agent backend swapping?

**Resolution**: Protocol-based backend interface.

Storage Agent accepts a `StorageBackend` protocol:
```python
class StorageBackend(Protocol):
    def save(self, key: str, data: dict) -> None: ...
    def get(self, key: str) -> dict | None: ...
    def delete(self, key: str) -> bool: ...
    def list(self) -> list[dict]: ...
```

Phase I implements `InMemoryBackend`, Phase II implements `PostgresBackend`.
Storage Agent code unchanged between phases.

### Q3: Message format for multi-agent coordination?

**Resolution**: Single message, single response for Phase I.

Phase I commands require at most two agents (e.g., TaskManager → Storage).
Complex multi-agent coordination (fan-out, aggregation) deferred to Phase II+.
Message format already supports correlation_id for future tracing.

## Dependencies Summary

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | ^2.5 | Data validation, message contracts |
| rich | ^13.0 | Console UI formatting |
| structlog | ^24.0 | Structured logging |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ^8.0 | Testing framework |
| pytest-asyncio | ^0.23 | Async test support |
| pytest-cov | ^4.1 | Coverage reporting |
| ruff | ^0.1 | Linting and formatting |
| mypy | ^1.8 | Type checking |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Sync-to-async transition breaks code | Low | Medium | Use async-compatible signatures from start |
| Rich library not available on all systems | Low | Low | Graceful fallback to plain text |
| Pydantic validation overhead | Low | Low | V2 is fast enough; cache validators if needed |
| Storage backend swap breaks data | Medium | High | Comprehensive integration tests, migration scripts |

## References

- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [structlog Documentation](https://www.structlog.org/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Python ABC Documentation](https://docs.python.org/3/library/abc.html)
