# Tasks: Full-Stack Web Application (Phase II)

**Branch**: `002-fullstack-web-app`
**Input**: Design documents from `/specs/002-fullstack-web-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Organization**: Tasks follow spec.md user story priorities with additional phases for backend foundation, agent evolution, and frontend infrastructure.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/` (extending Phase I Python code)
- **Frontend**: `frontend/` (new Next.js application)
- **Tests**: `tests/` (backend), `frontend/__tests__/` (frontend)

---

## Phase 1: Setup (Project Configuration)

**Purpose**: Environment setup and dependency installation

- [x] T001 Add Phase II backend dependencies to pyproject.toml (fastapi, uvicorn, sqlmodel, psycopg2-binary, python-jose, python-multipart)
- [x] T002 [P] Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_URL placeholders
- [x] T003 [P] Create src/config.py for environment variable loading with python-dotenv
- [x] T004 Initialize Next.js 16 project in frontend/ with App Router, TypeScript, Tailwind
- [x] T005 Install frontend dependencies (better-auth, zod) in frontend/package.json
- [x] T006 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL

---

## Phase 2: Backend Foundation (Database + API Infrastructure)

**Purpose**: Core backend infrastructure that MUST be complete before user stories

**Agent**: @storage-handler-agent (fastapi-skill, python-best-practices)

### Database Layer

- [x] T007 Create src/models/user.py with UserDB SQLModel (id, email, name, created_at)
- [x] T008 Update src/models/tasks.py with TaskDB SQLModel adding user_id foreign key field
- [x] T009 Create src/backends/postgres.py implementing StorageBackend protocol with SQLModel
- [x] T010 Add db_to_task and task_to_db conversion functions in src/models/tasks.py
- [x] T011 Create src/db.py with SQLModel engine initialization and session management

### API Infrastructure

- [x] T012 Create src/interfaces/api.py with FastAPI app, CORS middleware, health endpoints
- [x] T013 [P] Create src/auth/jwt.py with JWT token validation using python-jose
- [x] T014 Create src/auth/dependencies.py with get_current_user FastAPI dependency
- [x] T015 [P] Create src/models/requests.py with Pydantic request/response schemas per OpenAPI spec
- [x] T016 Create database tables initialization script in src/db.py create_tables function

**Checkpoint**: Backend infrastructure ready - API endpoints can now be implemented

---

## Phase 3: Agent Evolution (Multi-User Support)

**Purpose**: Update existing agents to support user_id filtering

**Agent**: @task-manager-agent (python-best-practices, testing-patterns)

### Protocol Updates

- [ ] T017 Update src/backends/base.py StorageBackend protocol adding optional user_id parameter to query()
- [ ] T018 Update src/backends/memory.py InMemoryBackend to accept (and ignore) user_id parameter
- [ ] T019 Implement user_id filtering in src/backends/postgres.py query method

### Agent Updates

- [ ] T020 Update src/agents/task_manager.py action handlers to accept user_id in payload
- [ ] T021 Add user_id validation in TaskManagerAgent for update/delete ownership checks
- [ ] T022 Update src/agents/storage_handler.py to pass user_id through to backend

### Console Compatibility

- [ ] T023 Verify src/interfaces/console.py works with updated agents (no user_id required)
- [ ] T024 Run existing Phase I tests to confirm backward compatibility

**Checkpoint**: Agents support multi-user operations - API endpoints can use agent layer

---

## Phase 4: User Story 1 - User Registration (Priority: P1)

**Goal**: New users can create accounts with email, name, and password

**Independent Test**: Submit registration form, verify account created, redirected to dashboard

**Agent**: @nextjs-expert-agent (nextjs-16-skill, ui-design-skill)

### Backend Endpoints (US1)

- [ ] T025 [US1] Implement POST /api/auth/signup endpoint in src/interfaces/api.py
- [ ] T026 [US1] Add password hashing with passlib in src/auth/password.py
- [ ] T027 [US1] Create user in database and return JWT token in signup response
- [ ] T028 [US1] Add email uniqueness validation with 409 Conflict response

### Frontend Pages (US1)

- [ ] T029 [US1] Create frontend/lib/auth.ts with Better Auth server configuration
- [ ] T030 [US1] Create frontend/lib/auth-client.ts with client-side auth helpers
- [ ] T031 [US1] Create frontend/app/api/auth/[...all]/route.ts for Better Auth API routes
- [ ] T032 [US1] Create frontend/components/auth-form.tsx with email/name/password fields
- [ ] T033 [US1] Create frontend/app/signup/page.tsx with registration form and validation
- [ ] T034 [US1] Add client-side validation for email format, password length (min 8)
- [ ] T035 [US1] Handle registration errors (409 email exists, 400 validation)

**Checkpoint**: Users can register - test by creating account and verifying redirect

---

## Phase 5: User Story 2 - User Authentication (Priority: P1)

**Goal**: Registered users can sign in and sign out

**Independent Test**: Sign in with valid credentials, verify dashboard access, sign out works

**Agent**: @nextjs-expert-agent (nextjs-16-skill)

### Backend Endpoints (US2)

- [ ] T036 [US2] Implement POST /api/auth/signin endpoint in src/interfaces/api.py
- [ ] T037 [US2] Verify password and return JWT token on successful signin
- [ ] T038 [US2] Implement POST /api/auth/signout endpoint (client-side token removal)
- [ ] T039 [US2] Implement GET /api/auth/me endpoint returning current user info

### Frontend Pages (US2)

- [ ] T040 [US2] Create frontend/app/signin/page.tsx with login form
- [ ] T041 [US2] Create frontend/middleware.ts for protected route redirection
- [ ] T042 [US2] Store JWT token in localStorage via auth-client.ts
- [ ] T043 [US2] Create frontend/components/header.tsx with user info and signout button
- [ ] T044 [US2] Handle signin errors (401 invalid credentials)
- [ ] T045 [US2] Implement session expiration detection and redirect to signin

**Checkpoint**: Users can sign in/out - test authentication flow end-to-end

---

## Phase 6: User Story 3 - View My Tasks (Priority: P2)

**Goal**: Authenticated users see their task list on dashboard

**Independent Test**: Sign in, verify task list displays (or empty state for new users)

**Agent**: @task-manager-agent, @nextjs-expert-agent

### Backend Endpoints (US3)

- [ ] T046 [US3] Implement GET /api/users/{user_id}/tasks endpoint in src/interfaces/api.py
- [ ] T047 [US3] Add authorization check (current_user == user_id) with 403 response
- [ ] T048 [US3] Wire endpoint to orchestrator with task_list action
- [ ] T049 [US3] Support status query parameter for filtering (all, pending, completed)

### Frontend Components (US3)

- [ ] T050 [US3] Create frontend/lib/api-client.ts with typed API client and JWT attachment
- [ ] T051 [US3] Create frontend/components/task-list.tsx displaying tasks
- [ ] T052 [US3] Create frontend/components/task-card.tsx for individual task display
- [ ] T053 [US3] Create frontend/app/dashboard/page.tsx as protected route
- [ ] T054 [US3] Add loading state component in frontend/components/loading.tsx
- [ ] T055 [US3] Add empty state when user has no tasks

**Checkpoint**: Dashboard shows tasks - test with empty state and populated list

---

## Phase 7: User Story 4 - Create a Task (Priority: P2)

**Goal**: Users can add new tasks with title and optional description

**Independent Test**: Fill task form, submit, verify task appears in list

**Agent**: @task-manager-agent, @nextjs-expert-agent

### Backend Endpoints (US4)

- [ ] T056 [US4] Implement POST /api/users/{user_id}/tasks endpoint in src/interfaces/api.py
- [ ] T057 [US4] Add request validation (title required, max 200 chars, description max 1000)
- [ ] T058 [US4] Wire endpoint to orchestrator with task_add action including user_id
- [ ] T059 [US4] Return 201 Created with created task in response

### Frontend Components (US4)

- [ ] T060 [US4] Create frontend/components/task-form.tsx with title and description fields
- [ ] T061 [US4] Add client-side validation matching backend constraints
- [ ] T062 [US4] Integrate task form into dashboard page
- [ ] T063 [US4] Update task list after successful creation (optimistic update or refetch)
- [ ] T064 [US4] Handle creation errors with user-friendly messages

**Checkpoint**: Users can add tasks - test by creating task and verifying it appears

---

## Phase 8: User Story 5 - Complete a Task (Priority: P3)

**Goal**: Users can toggle task completion status

**Independent Test**: Click complete button, verify visual change and persistence

**Agent**: @task-manager-agent, @nextjs-expert-agent

### Backend Endpoints (US5)

- [ ] T065 [US5] Implement PATCH /api/users/{user_id}/tasks/{task_id}/complete endpoint
- [ ] T066 [US5] Verify task ownership before status change
- [ ] T067 [US5] Wire endpoint to orchestrator with task_complete action
- [ ] T068 [US5] Update completed_at timestamp when marking complete

### Frontend Components (US5)

- [ ] T069 [US5] Add completion toggle button to task-card.tsx
- [ ] T070 [US5] Add visual styling for completed tasks (strikethrough, muted colors)
- [ ] T071 [US5] Update task list state after completion toggle
- [ ] T072 [US5] Handle completion errors gracefully

**Checkpoint**: Task completion works - test toggle and verify persistence on refresh

---

## Phase 9: User Story 6 - Update a Task (Priority: P3)

**Goal**: Users can edit task title and description

**Independent Test**: Edit task, save changes, verify updates persist

**Agent**: @task-manager-agent, @nextjs-expert-agent

### Backend Endpoints (US6)

- [ ] T073 [US6] Implement PUT /api/users/{user_id}/tasks/{task_id} endpoint
- [ ] T074 [US6] Verify task ownership and validate update payload
- [ ] T075 [US6] Wire endpoint to orchestrator with task_update action
- [ ] T076 [US6] Update updated_at timestamp on modification

### Frontend Components (US6)

- [ ] T077 [US6] Add edit mode to task-card.tsx with inline editing
- [ ] T078 [US6] Create frontend/components/edit-task-modal.tsx for modal editing
- [ ] T079 [US6] Add cancel/save buttons with validation
- [ ] T080 [US6] Update task list state after successful edit
- [ ] T081 [US6] Handle update errors with validation feedback

**Checkpoint**: Task editing works - test by modifying task and verifying changes

---

## Phase 10: User Story 7 - Delete a Task (Priority: P4)

**Goal**: Users can permanently remove tasks

**Independent Test**: Delete task with confirmation, verify removal from list

**Agent**: @task-manager-agent, @nextjs-expert-agent

### Backend Endpoints (US7)

- [ ] T082 [US7] Implement DELETE /api/users/{user_id}/tasks/{task_id} endpoint
- [ ] T083 [US7] Verify task ownership before deletion
- [ ] T084 [US7] Wire endpoint to orchestrator with task_delete action
- [ ] T085 [US7] Return 404 if task doesn't exist

### Frontend Components (US7)

- [ ] T086 [US7] Add delete button to task-card.tsx
- [ ] T087 [US7] Create frontend/components/confirm-dialog.tsx for deletion confirmation
- [ ] T088 [US7] Remove task from list after successful deletion
- [ ] T089 [US7] Handle deletion errors (404, 403)

**Checkpoint**: Task deletion works - test by deleting task and verifying removal

---

## Phase 11: Frontend Polish (UI/UX)

**Purpose**: Complete frontend with responsive design and error handling

**Agent**: @nextjs-expert-agent (ui-design-skill)

### Landing Page

- [ ] T090 [P] Create frontend/app/page.tsx public landing page with signup/signin links
- [ ] T091 [P] Add hero section describing the Todo application

### Responsive Design

- [ ] T092 Apply responsive Tailwind classes to all components (320px+ support)
- [ ] T093 [P] Create mobile-friendly navigation in header.tsx
- [ ] T094 Test dashboard layout on mobile viewport sizes

### Error Handling

- [ ] T095 Create frontend/components/error-boundary.tsx for React error boundaries
- [ ] T096 Add global error handling in frontend/app/error.tsx
- [ ] T097 [P] Add network error detection and retry prompts in api-client.ts

**Checkpoint**: Frontend complete with responsive design and error handling

---

## Phase 12: Integration & Testing

**Purpose**: End-to-end testing and documentation

**Agent**: @orchestrator-agent, @github-workflow-agent

### API Integration Tests

- [ ] T098 Create tests/integration/api/test_auth.py for signup/signin endpoints
- [ ] T099 Create tests/integration/api/test_tasks.py for CRUD operations
- [ ] T100 [P] Add user isolation tests (User A cannot see User B's tasks)

### Console Compatibility

- [ ] T101 Run uv run todo and verify Phase I console still functions
- [ ] T102 Run uv run pytest to verify existing tests pass

### Performance Validation

- [ ] T103 Test API response times against SC-003 (<2 seconds)
- [ ] T104 Test dashboard load time against SC-004 (<3 seconds)

### Documentation

- [ ] T105 Update README.md with Phase II setup instructions
- [ ] T106 [P] Update CLAUDE.md with new API patterns and endpoints
- [ ] T107 Validate setup using quickstart.md instructions

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Backend Foundation) ─────────┐
    ↓                                  │
Phase 3 (Agent Evolution) ────────────┤
    ↓                                  │
Phase 4 (US1: Registration) ◀─────────┘
    ↓
Phase 5 (US2: Authentication)
    ↓
Phase 6 (US3: View Tasks) ←──┬── Phase 7 (US4: Create Task)
    ↓                        │
Phase 8 (US5: Complete) ─────┴── Phase 9 (US6: Update)
    ↓
Phase 10 (US7: Delete)
    ↓
Phase 11 (Frontend Polish)
    ↓
Phase 12 (Integration & Testing)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|-------------------|
| US1 (Registration) | Phase 2, 3 | None |
| US2 (Authentication) | US1 | None |
| US3 (View Tasks) | US2 | US4 (after T050) |
| US4 (Create Task) | US2 | US3 (after T046) |
| US5 (Complete) | US3, US4 | US6 |
| US6 (Update) | US3, US4 | US5 |
| US7 (Delete) | US3 | None |

### Parallel Opportunities per Phase

**Phase 1 (Setup)**:
```
T002 (.env.example) ║ T003 (config.py) ║ T006 (frontend .env)
```

**Phase 2 (Backend Foundation)**:
```
T007 (UserDB) ║ T008 (TaskDB) ║ T013 (jwt.py) ║ T015 (requests.py)
```

**Phase 3 (Agent Evolution)**:
```
T018 (memory.py) ║ T019 (postgres.py query)
```

**Phase 11 (Polish)**:
```
T090 (landing) ║ T091 (hero) ║ T093 (mobile nav) ║ T097 (error handling)
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 + US4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Backend Foundation
3. Complete Phase 3: Agent Evolution
4. Complete Phase 4: US1 (Registration)
5. Complete Phase 5: US2 (Authentication)
6. Complete Phase 6: US3 (View Tasks)
7. Complete Phase 7: US4 (Create Task)
8. **STOP and VALIDATE**: Users can register, sign in, view tasks, add tasks
9. Deploy MVP if needed

### Incremental Delivery

| Milestone | Delivers | Test |
|-----------|----------|------|
| After Phase 5 | Auth flow complete | Can register and sign in |
| After Phase 7 | Core CRUD (add/view) | Can create and see tasks |
| After Phase 10 | Full CRUD | All 5 basic features work |
| After Phase 12 | Production ready | All tests pass, docs complete |

---

## Task Summary

| Phase | Task Count | Purpose |
|-------|------------|---------|
| 1: Setup | 6 | Project configuration |
| 2: Backend Foundation | 10 | Database + API infrastructure |
| 3: Agent Evolution | 8 | Multi-user support |
| 4: US1 Registration | 11 | Account creation |
| 5: US2 Authentication | 10 | Sign in/out |
| 6: US3 View Tasks | 10 | Dashboard display |
| 7: US4 Create Task | 9 | Task creation |
| 8: US5 Complete Task | 8 | Completion toggle |
| 9: US6 Update Task | 9 | Task editing |
| 10: US7 Delete Task | 8 | Task removal |
| 11: Frontend Polish | 8 | UI/UX completion |
| 12: Integration | 10 | Testing & docs |
| **Total** | **107** | |

---

## Notes

- [P] tasks can run in parallel if they modify different files
- [USn] labels track which user story a task belongs to
- Backend tasks (src/) use @task-manager-agent and @storage-handler-agent
- Frontend tasks (frontend/) use @nextjs-expert-agent
- Integration tasks use @orchestrator-agent
- Commit after each logical task group (not every single task)
- Run `uv run pytest` after completing each backend phase
- Test frontend components in browser after each UI task
