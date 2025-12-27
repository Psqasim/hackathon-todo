<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change: 0.0.0 → 1.0.0 (MAJOR: Initial constitution creation)
Ratified: 2025-12-26
Last Amended: 2025-12-26

Modified principles:
  - N/A (Initial creation)

Added sections:
  - 8 Core Principles (Agent Architecture, Skill Reusability, Separation of Concerns,
    Evolution Strategy, Testing Standards, Code Quality, Error Handling, Spec-Driven Development)
  - Phase Evolution Roadmap
  - Technology Stack Standards
  - Governance Rules

Removed sections:
  - N/A (Initial creation)

Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (User stories/acceptance criteria aligned)
  - .specify/templates/tasks-template.md: ✅ Compatible (Phase-based structure matches evolution)

Follow-up TODOs:
  - None (All placeholders resolved)
================================================================================
-->

# TaskFlow Todo Application Constitution

A comprehensive governance document for the multi-agent Todo application evolving through 5 phases: Console App → Web App → AI Chatbot → Local K8s → Cloud Deployment.

## Core Principles

### I. Agent Architecture Patterns

The application MUST follow a multi-agent architecture with clear hierarchy and responsibilities:

**Orchestrator Agent**
- The Main Orchestrator Agent coordinates all subagents and manages workflow
- Orchestrator receives user intent and delegates to appropriate specialized agents
- Orchestrator handles cross-agent communication and conflict resolution

**Subagent Design**
- Each subagent MUST have a single, focused responsibility
- Core subagents: Task Manager Agent, Storage Handler Agent, UI Controller Agent
- Subagents communicate via well-defined interfaces (not direct method calls)
- Agent contracts MUST be versioned using semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes to agent contracts require MAJOR version bump and migration plan

**Agent Communication**
- Agents communicate through typed message protocols
- All agent inputs and outputs MUST have Pydantic model contracts
- Agent errors propagate to orchestrator with structured error types
- Agents MUST NOT share mutable state directly

### II. Skill Reusability Standards

Skills are the atomic units of functionality that agents use to accomplish tasks:

**Technology Agnosticism**
- Skills MUST work across console, web, and chatbot interfaces without modification
- Skills accept typed inputs and return typed outputs (no UI-specific code)
- Skills MUST NOT import interface-specific libraries (no Click, FastAPI, etc. in skill code)

**Skill Contracts**
- Every skill MUST have a documented input/output contract using Pydantic models
- Skill contracts include: input schema, output schema, error types, side effects
- Skills MUST be stateless; state lives in Storage Agent

**Skill Testability**
- Each skill MUST have unit tests that run independently (no agent context required)
- Skills MUST achieve minimum 90% code coverage
- Skill tests MUST NOT require external services (use fixtures/mocks)

**Skill Evolution**
- Skill contracts use semantic versioning
- New skill versions MUST maintain backward compatibility within MINOR versions
- Deprecated skill methods MUST remain functional for one MINOR version cycle

### III. Separation of Concerns

The architecture enforces strict layer separation across all phases:

**UI Layer**
- Phase I: Console interface (Click/Typer CLI)
- Phase II: Web frontend (Next.js App Router)
- Phase III: Chatbot interface (OpenAI ChatKit)
- UI components MUST NOT contain business logic
- UI MUST communicate only with agents, never directly with storage

**Business Logic Layer**
- Task Manager Agent owns ALL task-related business logic
- Business rules MUST be testable without UI or storage
- Domain validation happens in the business layer, not UI or storage
- Business logic MUST NOT know about storage implementation details

**Data Layer**
- Storage Handler Agent manages ALL persistence operations
- Phase I: In-memory storage (dict-based)
- Phase II: Neon PostgreSQL via SQLModel
- Phase III-V: Same as Phase II with conversation history
- Storage implementation MUST be swappable without changing business logic

### IV. Evolution Strategy

Each phase builds on the previous without breaking existing functionality:

**Phase I: Console App (In-Memory)**
- Basic CRUD operations (Add, Delete, Update, View, Mark Complete)
- In-memory storage using Python dictionaries
- CLI interface using Click or Typer
- All skills defined and tested at this phase

**Phase II: Web App (Database)**
- RESTful API endpoints via FastAPI
- Neon PostgreSQL database with SQLModel ORM
- Next.js frontend with App Router
- Better Auth for authentication with JWT
- Storage Agent switches to database; business logic unchanged

**Phase III: AI Chatbot (MCP Integration)**
- OpenAI Agents SDK for conversational AI
- MCP Server exposing task operations as tools
- ChatKit frontend for conversation UI
- Stateless chat endpoint with database-persisted conversation
- Business logic remains unchanged; new chat agent added

**Phase IV: Local Kubernetes**
- Docker containerization of all services
- Minikube local deployment
- Helm charts for orchestration
- Gordon (Docker AI) for container operations
- kubectl-ai and Kagent for K8s operations

**Phase V: Cloud Deployment**
- Event-driven architecture with Kafka
- Dapr for distributed runtime (Pub/Sub, State, Bindings, Secrets)
- Azure AKS, Google GKE, or Oracle OKE deployment
- CI/CD pipeline via GitHub Actions
- Recurring tasks and reminder services

**Non-Breaking Evolution Rules**
- New phases add new agents/interfaces; existing agents remain unchanged
- Storage interface changes require migration scripts
- All phase transitions MUST pass existing test suites
- Feature flags for progressive rollout when needed

### V. Testing Standards

Testing is NON-NEGOTIABLE and follows Test-Driven Development (TDD):

**Test Hierarchy**
- Unit tests: Individual skills and utility functions
- Integration tests: Agent interactions and message passing
- End-to-end tests: Complete user workflows through UI
- Contract tests: API and agent interface validation

**Coverage Requirements**
- Minimum 80% overall code coverage
- Critical paths (task CRUD, authentication) MUST have 95%+ coverage
- Skills MUST have 90%+ coverage
- UI components require snapshot and interaction tests

**TDD Workflow**
- Tests written FIRST, then implementation
- Red-Green-Refactor cycle strictly enforced
- Tests MUST fail before implementation is written
- No PR merges with failing tests

**Test Organization**
```
tests/
├── unit/           # Skill and utility tests
├── integration/    # Agent interaction tests
├── contract/       # API contract tests
└── e2e/            # End-to-end workflow tests
```

### VI. Code Quality Requirements

All code MUST meet the following quality standards:

**Python Standards**
- Python 3.12+ required (3.13+ preferred per hackathon spec)
- Type hints on ALL functions, methods, and class attributes
- No `Any` types except when truly unavoidable (document why)
- Docstrings required for all classes, functions, and modules
- PEP 8 style guide strictly enforced (via Ruff or Black)

**Dependency Management**
- UV for package and environment management
- All dependencies pinned to specific versions in pyproject.toml
- No development dependencies in production
- Regular security audits of dependencies

**Code Organization**
- DRY principle: No code duplication; extract shared logic
- Single Responsibility: Each module/class has one purpose
- Maximum function length: 50 lines (prefer < 25)
- Maximum file length: 300 lines (prefer < 200)
- Maximum cyclomatic complexity: 10 per function

**Naming Conventions**
- snake_case for functions, variables, modules
- PascalCase for classes and type aliases
- SCREAMING_SNAKE_CASE for constants
- Descriptive names; no single-letter variables except iterators

### VII. Error Handling

Robust error handling ensures application resilience:

**Error Principles**
- Agents handle errors gracefully with clear, actionable messages
- Failed operations MUST NOT crash the application
- All errors are logged with full context (traceback, input data, timestamp)
- User-facing errors are friendly and suggest next steps

**Error Types**
- `ValidationError`: Invalid input data (return 400)
- `NotFoundError`: Resource not found (return 404)
- `AuthorizationError`: Permission denied (return 403)
- `ConflictError`: State conflict (return 409)
- `InternalError`: Unexpected errors (return 500, log full details)

**Error Propagation**
- Skills raise typed exceptions; agents catch and transform
- Agents return Result types (success or error) to orchestrator
- Orchestrator transforms errors to user-appropriate messages
- All errors include correlation ID for debugging

**Logging Requirements**
- Structured logging (JSON format in production)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include context: user_id, task_id, agent_name, timestamp
- Sensitive data (passwords, tokens) MUST NOT be logged

### VIII. Spec-Driven Development

All development follows the Spec-Driven Development (SDD) workflow:

**Specification First**
- Every feature starts with a specification document
- Specs live in `specs/<feature-name>/spec.md`
- No implementation without approved specification
- Spec includes user stories, acceptance criteria, and requirements

**Agent Documentation**
- Every agent has a documented purpose and interface
- Agent contracts defined before implementation
- Interface changes require spec update and approval

**Skill Documentation**
- Every skill has usage examples in docstrings
- Skill contracts include input/output schemas
- Skills reference their spec section

**Implementation Fidelity**
- Implementation follows the plan exactly
- Deviations require spec amendment and approval
- Code comments reference spec sections (e.g., `# Ref: spec.md §3.2`)
- PRs include spec compliance checklist

## Phase Evolution Roadmap

| Phase | Primary Goal | Key Technologies | Storage | Interface |
|-------|-------------|------------------|---------|-----------|
| I | Basic CRUD | Python 3.13+, UV, Click/Typer | In-memory (dict) | Console CLI |
| II | Web Platform | FastAPI, Next.js 16+, SQLModel | Neon PostgreSQL | Web UI |
| III | AI Chatbot | OpenAI Agents SDK, MCP SDK, ChatKit | PostgreSQL + Conversations | Chat UI |
| IV | Containerization | Docker, Minikube, Helm, kubectl-ai | PostgreSQL | K8s Deployed |
| V | Cloud Native | Kafka, Dapr, AKS/GKE, GitHub Actions | PostgreSQL + Events | Cloud Deployed |

## Technology Stack Standards

### Required Technologies
- **Language**: Python 3.12+ (3.13+ preferred)
- **Package Manager**: UV (not pip)
- **Type Checking**: mypy with strict mode
- **Linting**: Ruff
- **Formatting**: Black or Ruff format
- **Testing**: pytest with coverage

### Phase-Specific Technologies
- **Phase I**: Click or Typer for CLI
- **Phase II**: FastAPI (backend), Next.js 16+ (frontend), SQLModel (ORM), Neon (DB), Better Auth (auth)
- **Phase III**: OpenAI Agents SDK, MCP Python SDK, OpenAI ChatKit
- **Phase IV**: Docker, Minikube, Helm, Gordon, kubectl-ai, Kagent
- **Phase V**: Apache Kafka (or Redpanda), Dapr, Strimzi, AKS/GKE/OKE

## Project Structure

```
hackathon-todo/
├── .specify/                 # Spec-Kit configuration and templates
│   ├── memory/              # Project memory (constitution, etc.)
│   └── templates/           # Document templates
├── specs/                    # Feature specifications
│   ├── phase-1-console/
│   ├── phase-2-web/
│   ├── phase-3-chatbot/
│   ├── phase-4-k8s/
│   └── phase-5-cloud/
├── src/                      # Phase I: Source code
│   ├── agents/              # Agent implementations
│   ├── skills/              # Reusable skill modules
│   ├── models/              # Domain models (Pydantic)
│   └── cli/                 # CLI interface
├── backend/                  # Phase II+: FastAPI backend
│   ├── src/
│   │   ├── agents/
│   │   ├── skills/
│   │   ├── models/
│   │   ├── api/
│   │   └── mcp/            # Phase III: MCP tools
│   └── tests/
├── frontend/                 # Phase II+: Next.js frontend
│   ├── src/
│   └── tests/
├── k8s/                      # Phase IV+: Kubernetes manifests
│   ├── helm/
│   └── dapr/
├── tests/                    # Shared test utilities
├── history/                  # PHR and ADR records
│   ├── prompts/
│   └── adr/
├── CLAUDE.md                 # Claude Code instructions
└── README.md                 # Project documentation
```

## Governance

### Constitution Authority
- This constitution supersedes all other practices and preferences
- Constitution violations block PR merges
- All agents (Claude, Copilot, Gemini) MUST read and follow this document

### Amendment Process
1. Propose amendment via spec document
2. Document rationale and impact analysis
3. Obtain stakeholder approval
4. Update constitution with new version number
5. Update affected templates and documentation
6. Create ADR for significant architectural changes

### Versioning Policy
- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review
- All PRs MUST verify constitution compliance
- Complexity MUST be justified against simplicity principle
- Deviations require explicit exception documentation
- Weekly review of constitution adherence in active development

### Hierarchy of Authority
When conflicts arise: **Constitution > Specify > Plan > Tasks**

**Version**: 1.0.0 | **Ratified**: 2025-12-26 | **Last Amended**: 2025-12-26
