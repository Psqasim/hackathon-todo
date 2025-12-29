# Implementation Plan: Full-Stack Web Application (Phase II)

**Branch**: `002-fullstack-web-app` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web-app/spec.md`

## Summary

Transform the Phase I console Todo application into a full-stack web application with multi-user support. This involves:
1. Adding a Next.js 16 frontend with Better Auth authentication
2. Creating a FastAPI REST API exposing task operations
3. Implementing PostgreSQL persistence via Neon serverless database
4. Extending existing agents to support user-scoped operations

The existing multi-agent architecture (Orchestrator, TaskManager, StorageHandler) is reused with minimal modifications. The Phase I console application continues to function alongside the new web interface.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, Next.js 16
**Storage**: Neon Serverless PostgreSQL (production), In-memory (console fallback)
**Testing**: pytest (backend), Vitest (frontend - optional)
**Target Platform**: Web browsers (desktop/mobile), Linux server (API)
**Project Type**: Web application (monorepo with frontend + backend)
**Performance Goals**: API response <200ms p95, Dashboard load <3s
**Constraints**: JWT token expiration 7 days, Max 200 char titles, Max 1000 char descriptions
**Scale/Scope**: Single user to thousands of users, ~100 tasks per user typical

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Agent Architecture Patterns
- [x] **Orchestrator Agent coordinates subagents**: Existing orchestrator routes to TaskManager, StorageHandler
- [x] **Subagents have single responsibility**: TaskManager (business logic), StorageHandler (persistence)
- [x] **Agent communication via typed messages**: AgentMessage/AgentResponse contracts maintained
- [x] **No shared mutable state**: Agents communicate via message passing only

### II. Skill Reusability Standards
- [x] **Technology-agnostic skills**: Task validation, status transitions work across interfaces
- [x] **Documented contracts**: Pydantic models for all inputs/outputs
- [x] **Stateless skills**: State lives in StorageHandler, skills are pure functions

### III. Separation of Concerns
- [x] **UI Layer**: Console (Phase I) and Web (Phase II) are separate interfaces
- [x] **Business Logic Layer**: TaskManagerAgent owns all task logic
- [x] **Data Layer**: StorageHandler with pluggable backends (memory/postgres)
- [x] **No business logic in UI**: API endpoints delegate to agents

### IV. Evolution Strategy
- [x] **Phase II builds on Phase I**: Same agents, new interface added
- [x] **Non-breaking changes**: Console app continues working
- [x] **Storage interface unchanged**: PostgresBackend implements same protocol

### V. Testing Standards
- [x] **Minimum 80% coverage**: Target maintained (Phase I: 56.72%, adding API tests)
- [x] **TDD workflow**: Tests for new API endpoints before implementation
- [x] **Test hierarchy**: Unit + Integration + Contract tests

### VI. Code Quality Requirements
- [x] **Python 3.12+**: Required by constitution
- [x] **Type hints on all functions**: Enforced via mypy strict mode
- [x] **UV for dependencies**: Already in use

### VII. Error Handling
- [x] **Typed exceptions**: ValidationError, NotFoundError, AuthorizationError
- [x] **Structured logging**: JSON format with correlation IDs
- [x] **User-friendly messages**: API returns actionable error descriptions

### VIII. Spec-Driven Development
- [x] **Specification first**: This plan derived from spec.md
- [x] **Agent contracts defined**: TaskManager, StorageHandler interfaces documented
- [x] **PRs include spec compliance**: Checklist in each PR

**Gate Status**: PASS - All constitution requirements satisfied

---

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Technology decisions (complete)
├── data-model.md        # Entity definitions (complete)
├── quickstart.md        # Setup guide (complete)
├── contracts/           # API contracts
│   └── openapi.yaml     # OpenAPI 3.1 specification (complete)
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
hackathon-todo/
├── src/                          # Python backend
│   ├── agents/                   # Agent implementations (Phase I - reused)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── storage_handler.py
│   │   ├── task_manager.py       # MODIFY: Add user_id support
│   │   └── ui_controller.py
│   ├── backends/                 # Storage backends
│   │   ├── __init__.py
│   │   ├── base.py               # MODIFY: Add user_id filter
│   │   ├── memory.py             # Phase I (unchanged)
│   │   └── postgres.py           # NEW: PostgreSQL backend
│   ├── interfaces/               # User interfaces
│   │   ├── __init__.py
│   │   ├── console.py            # Phase I console (unchanged)
│   │   └── api.py                # NEW: FastAPI application
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── messages.py
│   │   ├── tasks.py              # MODIFY: Add TaskDB with user_id
│   │   └── user.py               # NEW: User model
│   └── app.py                    # Application factory
├── frontend/                     # NEW: Next.js application
│   ├── app/
│   │   ├── layout.tsx            # Root layout with providers
│   │   ├── page.tsx              # Landing page (public)
│   │   ├── signup/
│   │   │   └── page.tsx          # Registration page
│   │   ├── signin/
│   │   │   └── page.tsx          # Login page
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Task management (protected)
│   │   └── api/
│   │       └── auth/
│   │           └── [...all]/
│   │               └── route.ts  # Better Auth API routes
│   ├── components/
│   │   ├── header.tsx            # Navigation + user menu
│   │   ├── task-list.tsx         # Task list display
│   │   ├── task-card.tsx         # Individual task card
│   │   ├── task-form.tsx         # Add/edit task form
│   │   └── auth-form.tsx         # Signup/signin form
│   ├── lib/
│   │   ├── auth.ts               # Better Auth configuration
│   │   ├── auth-client.ts        # Client-side auth helpers
│   │   └── api-client.ts         # Backend API client
│   ├── middleware.ts             # Route protection
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
├── tests/
│   ├── unit/                     # Existing unit tests
│   ├── integration/
│   │   ├── test_agents.py        # Existing agent tests
│   │   └── api/                  # NEW: API integration tests
│   │       ├── test_auth.py
│   │       └── test_tasks.py
│   └── contract/                 # NEW: Contract tests
│       └── test_api_contract.py
├── .env                          # Backend environment
├── .env.example                  # Environment template
├── pyproject.toml                # Python dependencies (update)
└── README.md                     # Project documentation (update)
```

**Structure Decision**: Web application structure with Python backend in `src/` and Next.js frontend in `frontend/`. This maintains Phase I compatibility while adding web capabilities.

---

## Implementation Phases

### Phase A: Backend Foundation (Database + API)

**Goal**: Get FastAPI serving task endpoints with PostgreSQL storage

#### A1. Dependencies & Configuration
- Add FastAPI, SQLModel, psycopg2-binary, python-jose to pyproject.toml
- Create .env.example with required variables
- Add environment loading with python-dotenv

#### A2. Database Models
- Create `src/models/user.py` with UserDB SQLModel
- Update `src/models/tasks.py` with TaskDB (add user_id field)
- Add model conversion functions (Task ↔ TaskDB)

#### A3. PostgreSQL Backend
- Create `src/backends/postgres.py` implementing StorageBackend protocol
- Add user_id filtering to query methods
- Implement connection pooling with SQLAlchemy

#### A4. FastAPI Application
- Create `src/interfaces/api.py` with app initialization
- Add CORS middleware for frontend communication
- Add health check endpoints

#### A5. Authentication Middleware
- Implement JWT validation using python-jose
- Create `get_current_user` dependency
- Add Authorization header extraction

#### A6. Task API Endpoints
- Implement all endpoints from OpenAPI spec:
  - GET /api/users/{user_id}/tasks
  - POST /api/users/{user_id}/tasks
  - GET /api/users/{user_id}/tasks/{task_id}
  - PUT /api/users/{user_id}/tasks/{task_id}
  - DELETE /api/users/{user_id}/tasks/{task_id}
  - PATCH /api/users/{user_id}/tasks/{task_id}/complete
- Wire endpoints to existing agents via orchestrator

### Phase B: Agent Evolution

**Goal**: Update agents to support user-scoped operations

#### B1. StorageBackend Protocol Update
- Add optional `user_id` parameter to `query()` method
- Update protocol documentation

#### B2. InMemoryBackend Compatibility
- Update memory backend to accept (and ignore) user_id
- Ensures Phase I console continues working

#### B3. TaskManagerAgent Updates
- Add user_id to all action payloads
- Pass user_id through to storage operations
- Add ownership validation for update/delete

#### B4. Integration Testing
- Test agent message flow with user_id
- Verify user isolation (User A can't see User B's tasks)

### Phase C: Frontend Application

**Goal**: Build Next.js UI with authentication and task management

#### C1. Next.js Project Setup
- Initialize with create-next-app (App Router, TypeScript, Tailwind)
- Configure environment variables
- Set up project structure

#### C2. Better Auth Integration
- Configure Better Auth with email/password provider
- Set up auth API routes
- Create auth client for components

#### C3. Authentication Pages
- Build signup page with form validation
- Build signin page with form validation
- Add route protection middleware

#### C4. Dashboard & Task Components
- Create task list component with loading states
- Create task card with complete/edit/delete actions
- Create task form for add/edit
- Create header with user info and signout

#### C5. API Client
- Create typed API client for backend communication
- Handle JWT token attachment
- Handle error responses

### Phase D: Integration & Testing

**Goal**: Full end-to-end functionality with tests

#### D1. API Integration Tests
- Test all endpoints with TestClient
- Test authentication flows
- Test user isolation

#### D2. Frontend-Backend Integration
- Test full signup → signin → task CRUD flow
- Test error handling (network failures, validation)
- Test session expiration handling

#### D3. Console Compatibility Verification
- Verify `uv run todo` still works
- Test in-memory backend unchanged

#### D4. Documentation Updates
- Update README with Phase II setup
- Add API documentation
- Update CLAUDE.md with new patterns

---

## Key Technical Decisions

### 1. JWT Token Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────┐     ┌───────────────┐     ┌──────────┐     ┌──────────────┐  │
│  │  User    │────>│ Better Auth   │────>│  JWT     │────>│  Frontend    │  │
│  │  Login   │     │ (Next.js)     │     │  Token   │     │  Storage     │  │
│  └──────────┘     └───────────────┘     └──────────┘     └──────────────┘  │
│                                                                    │        │
│                                                                    ▼        │
│  ┌──────────┐     ┌───────────────┐     ┌──────────┐     ┌──────────────┐  │
│  │  Task    │<────│   FastAPI     │<────│  Verify  │<────│  API Request │  │
│  │  Data    │     │   Backend     │     │  JWT     │     │  + Bearer    │  │
│  └──────────┘     └───────────────┘     └──────────┘     └──────────────┘  │
│                                                                             │
│  Shared Secret: BETTER_AUTH_SECRET (identical in both apps)                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Storage Backend Swapping

```python
# Phase I: Console uses in-memory
storage_backend = InMemoryBackend()
storage_agent = StorageHandlerAgent(storage_backend)

# Phase II: API uses PostgreSQL
storage_backend = PostgresBackend(DATABASE_URL)
storage_agent = StorageHandlerAgent(storage_backend)

# Same StorageHandlerAgent, different backend!
```

### 3. User Isolation Pattern

```python
# API endpoint extracts user from JWT
@app.get("/api/users/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    # Authorization check
    if current_user != user_id:
        raise HTTPException(403, "Forbidden")

    # Pass user_id to agent
    response = await orchestrator.handle_message(
        AgentMessage(
            action="task_list",
            payload={"user_id": user_id}  # Filtered by storage
        )
    )
```

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Better Auth JWT format incompatibility | Medium | High | Research JWT structure early, test with manual token |
| Database connection issues (Neon cold start) | Low | Medium | Add connection retry logic, use connection pooling |
| CORS misconfiguration | Medium | Low | Test cross-origin early, document CORS settings |
| Breaking Phase I console | Low | High | Run console tests after every change |
| Token expiration UX issues | Medium | Medium | Implement refresh flow or clear redirect |

---

## Success Metrics

From spec.md Success Criteria:

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| SC-001 | Registration < 60 seconds | Manual timing test |
| SC-002 | Sign in to dashboard < 10 seconds | Manual timing test |
| SC-003 | Task operations < 2 seconds | API response time logging |
| SC-004 | Dashboard load < 3 seconds | Browser DevTools timing |
| SC-005 | 100% endpoints require auth | Contract tests |
| SC-006 | Zero data leakage between users | Integration tests |
| SC-007 | Validation errors < 500ms | Form interaction test |
| SC-008 | Usable on 320px+ screens | Responsive design test |
| SC-009 | Console still works | Existing test suite passes |
| SC-010 | All 5 features in web UI | E2E manual test |

---

## Complexity Tracking

> **No constitution violations require justification.**

The implementation adds a frontend project (necessary for web interface) and a new storage backend (necessary for persistence). Both are explicitly required by the hackathon spec and constitution Phase II guidelines.

---

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Execute tasks in dependency order
3. Commit after each task group
4. Create PR when Phase II is complete
