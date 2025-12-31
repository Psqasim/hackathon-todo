# Tasks: AI Chatbot with MCP Integration

**Input**: Design documents from `/specs/003-ai-chatbot-mcp/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/mcp_server/` for MCP server code
- **Frontend**: `frontend/app/` for pages, `frontend/components/` for components
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **Models**: `src/models/` for Pydantic models

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and MCP server structure

- [x] T001 Install MCP server dependencies: `uv add fastmcp openai dateparser httpx`
- [x] T002 Create MCP server package structure at `src/mcp_server/__init__.py`
- [x] T003 [P] Add environment variables to `.env.example`: OPENAI_API_KEY, MCP_SERVER_PORT, MCP_BACKEND_URL
- [x] T004 [P] Add NEXT_PUBLIC_MCP_URL to `frontend/.env.local.example`
- [x] T005 [P] Create empty module files: `src/mcp_server/server.py`, `tools.py`, `agent.py`, `nlp.py`, `auth.py`, `memory.py`, `prompts.py`, `backend_client.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### A. MCP Server Foundation

- [ ] T006 [Found] Create FastMCP server entry point in `src/mcp_server/server.py` with CORS middleware (FR-001)
- [ ] T007 [Found] Implement HTTP client for FastAPI backend in `src/mcp_server/backend_client.py` with httpx async client
- [ ] T008 [Found] Implement JWT token validation and extraction in `src/mcp_server/auth.py` (FR-009, FR-028)
- [ ] T009 [Found] Add health check endpoint `/health` in `src/mcp_server/server.py` returning OpenAI and backend status
- [ ] T010 [Found] Create system prompt constants in `src/mcp_server/prompts.py` (FR-018)

### B. Chat Models

- [ ] T011 [P] [Found] Create Pydantic models for chat in `src/models/chat.py`: ChatRequest, ChatResponse, ConversationSummary (FR-030)
- [ ] T012 [P] [Found] Create database models in `src/models/chat.py`: ConversationDB, MessageDB with SQLModel (FR-030)
- [ ] T013 [Found] Add conversation tables to `src/db.py` create_tables function (FR-030)

### C. NLP Utilities

- [ ] T014 [Found] Implement natural language date parsing in `src/mcp_server/nlp.py` using dateparser (FR-015)
- [ ] T015 [Found] Implement priority extraction in `src/mcp_server/nlp.py` from keywords (FR-016)
- [ ] T016 [Found] Write unit tests for NLP parsing in `tests/unit/test_nlp.py`

### D. OpenAI Agent Core

- [ ] T017 [Found] Create TaskAgent class in `src/mcp_server/agent.py` with OpenAI client initialization (FR-011, FR-012)
- [ ] T018 [Found] Implement function calling tools list in `src/mcp_server/agent.py` mapping to MCP tools (FR-012)
- [ ] T019 [Found] Implement conversation history management in `src/mcp_server/memory.py` (FR-014)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1)

**Goal**: Users can create tasks by describing them in natural language
**Independent Test**: Say "Add task to buy groceries tomorrow with high priority" and verify task appears

### Implementation for User Story 1

- [ ] T020 [US1] Implement `add_task` MCP tool in `src/mcp_server/tools.py` (FR-002)
  - Accept: title (required), description, priority, due_date, tags
  - Parse natural language dates via nlp.py
  - Call backend POST `/api/users/{user_id}/tasks`
  - Return created task with confirmation message

- [ ] T021 [US1] Add add_task function definition to OpenAI tools in `src/mcp_server/agent.py`
  - Include parameter descriptions for natural language hints
  - Set title as required, others optional

- [ ] T022 [US1] Implement tool execution handler in `src/mcp_server/agent.py` for add_task
  - Extract parameters from function call
  - Execute MCP tool with user context
  - Format result for natural language response

- [ ] T023 [US1] Add system prompt guidance for task creation in `src/mcp_server/prompts.py`
  - Instruct agent to extract title, priority, due date from natural language
  - Guide agent to ask for missing required fields (title)

- [ ] T024 [US1] Write unit tests for add_task tool in `tests/unit/test_mcp_tools.py`
  - Test successful creation with all fields
  - Test creation with only title
  - Test natural language date parsing integration
  - Test priority keyword extraction

- [ ] T025 [US1] Write integration test for task creation flow in `tests/integration/test_chat_api.py`
  - Test "Add task to buy groceries tomorrow" produces correct task

**Checkpoint**: User Story 1 should be fully functional - users can create tasks via chat

---

## Phase 4: User Story 2 - Conversational Task Listing (Priority: P1)

**Goal**: Users can view their tasks by asking in natural language
**Independent Test**: Ask "Show my tasks" and verify response lists all tasks

### Implementation for User Story 2

- [ ] T026 [US2] Implement `list_tasks` MCP tool in `src/mcp_server/tools.py` (FR-003)
  - Accept: status filter (all, pending, completed), priority filter, limit
  - Call backend GET `/api/users/{user_id}/tasks` with query params
  - Return formatted task list with count

- [ ] T027 [US2] Implement `get_task` MCP tool in `src/mcp_server/tools.py` (FR-004)
  - Accept: task_id
  - Call backend GET `/api/users/{user_id}/tasks/{task_id}`
  - Return single task details

- [ ] T028 [US2] Add list_tasks and get_task function definitions to OpenAI tools in `src/mcp_server/agent.py`
  - Include natural language hints for status filtering
  - Add examples: "pending tasks", "completed items"

- [ ] T029 [US2] Implement tool execution handlers for list_tasks and get_task in `src/mcp_server/agent.py`

- [ ] T030 [US2] Add system prompt guidance for listing in `src/mcp_server/prompts.py`
  - Instruct agent to format task lists in readable manner
  - Guide response when no tasks exist

- [ ] T031 [US2] Write unit tests for list_tasks and get_task in `tests/unit/test_mcp_tools.py`
  - Test listing with no filter
  - Test listing with status filter
  - Test empty task list response
  - Test get single task

- [ ] T032 [US2] Write integration test for task listing flow in `tests/integration/test_chat_api.py`

**Checkpoint**: User Stories 1 AND 2 work - users can create and view tasks via chat

---

## Phase 5: User Story 3 - Task Updates via Chat (Priority: P2)

**Goal**: Users can modify existing tasks through natural language
**Independent Test**: Say "Change grocery task priority to urgent" and verify update

### Implementation for User Story 3

- [ ] T033 [US3] Implement `update_task` MCP tool in `src/mcp_server/tools.py` (FR-005)
  - Accept: task_id, optional title, description, priority, due_date
  - Call backend PATCH `/api/users/{user_id}/tasks/{task_id}`
  - Return updated task with confirmation

- [ ] T034 [US3] Implement `search_tasks` MCP tool in `src/mcp_server/tools.py` (FR-008)
  - Accept: query string for keyword search
  - Call backend GET `/api/users/{user_id}/tasks` with search param
  - Return matching tasks for disambiguation

- [ ] T035 [US3] Add update_task and search_tasks function definitions to OpenAI tools in `src/mcp_server/agent.py`
  - Include guidance for identifying tasks by keyword

- [ ] T036 [US3] Implement tool execution handlers for update_task and search_tasks in `src/mcp_server/agent.py`

- [ ] T037 [US3] Add system prompt guidance for updates in `src/mcp_server/prompts.py`
  - Instruct agent to search for task first if task_id unknown
  - Guide agent to ask for clarification when multiple matches

- [ ] T038 [US3] Write unit tests for update_task and search_tasks in `tests/unit/test_mcp_tools.py`
  - Test update with single field
  - Test update with multiple fields
  - Test search with matching results
  - Test search with no results

- [ ] T039 [US3] Write integration test for task update flow in `tests/integration/test_chat_api.py`

**Checkpoint**: User Story 3 works - users can update tasks via chat

---

## Phase 6: User Story 4 - Task Completion via Chat (Priority: P2)

**Goal**: Users can mark tasks complete through natural language
**Independent Test**: Say "Mark grocery task as done" and verify status changes

### Implementation for User Story 4

- [ ] T040 [US4] Implement `complete_task` MCP tool in `src/mcp_server/tools.py` (FR-007)
  - Accept: task_id, completed (boolean, default true)
  - Call backend PATCH `/api/users/{user_id}/tasks/{task_id}` with status change
  - Return updated task with completion confirmation

- [ ] T041 [US4] Add complete_task function definition to OpenAI tools in `src/mcp_server/agent.py`
  - Include natural language hints: "done", "finished", "complete", "unmark"

- [ ] T042 [US4] Implement tool execution handler for complete_task in `src/mcp_server/agent.py`

- [ ] T043 [US4] Add system prompt guidance for completion in `src/mcp_server/prompts.py`
  - Instruct agent to search for task first if needed
  - Guide celebratory responses on completion

- [ ] T044 [US4] Write unit tests for complete_task in `tests/unit/test_mcp_tools.py`
  - Test marking task complete
  - Test unmarking completed task
  - Test with non-existent task

- [ ] T045 [US4] Write integration test for task completion flow in `tests/integration/test_chat_api.py`

**Checkpoint**: User Story 4 works - users can complete tasks via chat

---

## Phase 7: User Story 5 - Task Deletion via Chat (Priority: P3)

**Goal**: Users can delete tasks with confirmation
**Independent Test**: Say "Delete the grocery task" and verify removal

### Implementation for User Story 5

- [ ] T046 [US5] Implement `delete_task` MCP tool in `src/mcp_server/tools.py` (FR-006)
  - Accept: task_id
  - Call backend DELETE `/api/users/{user_id}/tasks/{task_id}`
  - Return deletion confirmation with deleted task id

- [ ] T047 [US5] Add delete_task function definition to OpenAI tools in `src/mcp_server/agent.py`
  - Include warning about destructive action

- [ ] T048 [US5] Implement tool execution handler for delete_task in `src/mcp_server/agent.py`

- [ ] T049 [US5] Add system prompt guidance for deletion in `src/mcp_server/prompts.py` (FR-017)
  - MUST instruct agent to confirm before deletion
  - Guide agent to state which task will be deleted

- [ ] T050 [US5] Write unit tests for delete_task in `tests/unit/test_mcp_tools.py`
  - Test successful deletion
  - Test deletion of non-existent task

- [ ] T051 [US5] Write integration test for task deletion flow in `tests/integration/test_chat_api.py`

**Checkpoint**: User Story 5 works - users can delete tasks via chat with confirmation

---

## Phase 8: User Story 6 - Advanced Queries (Priority: P3)

**Goal**: Users can filter tasks with multiple criteria
**Independent Test**: Say "Show urgent tasks due this week" and verify filtered results

### Implementation for User Story 6

- [ ] T052 [US6] Implement `filter_tasks` MCP tool in `src/mcp_server/tools.py`
  - Accept: priority, status, due_date_from, due_date_to, has_due_date
  - Call backend with combined query parameters
  - Return filtered results with filter summary

- [ ] T053 [US6] Add filter_tasks function definition to OpenAI tools in `src/mcp_server/agent.py`
  - Include natural language date range hints

- [ ] T054 [US6] Implement tool execution handler for filter_tasks in `src/mcp_server/agent.py`

- [ ] T055 [US6] Add system prompt guidance for filtering in `src/mcp_server/prompts.py`
  - Instruct agent to parse "this week", "overdue", "upcoming"
  - Guide response formatting for filtered lists

- [ ] T056 [US6] Write unit tests for filter_tasks in `tests/unit/test_mcp_tools.py`
  - Test single filter
  - Test combined filters
  - Test date range parsing

- [ ] T057 [US6] Write integration test for advanced queries in `tests/integration/test_chat_api.py`

**Checkpoint**: User Story 6 works - users can filter tasks with complex queries

---

## Phase 9: User Story 7 - Context Awareness (Priority: P4)

**Goal**: Agent maintains conversation context for follow-ups
**Independent Test**: Create task, then say "Make that high priority" and verify update

### Implementation for User Story 7

- [ ] T058 [US7] Implement context tracking in `src/mcp_server/memory.py`
  - Track last mentioned task_id(s)
  - Track last operation type
  - Store in conversation history metadata

- [ ] T059 [US7] Update tool execution in `src/mcp_server/agent.py` to store context
  - After add_task, store created task_id as context
  - After list_tasks, store returned task_ids
  - After any task operation, update context

- [ ] T060 [US7] Add context resolution in `src/mcp_server/agent.py`
  - Resolve "that", "it", "those" to context task(s)
  - Fall back to search if context unclear

- [ ] T061 [US7] Add system prompt guidance for context in `src/mcp_server/prompts.py`
  - Instruct agent to use context for ambiguous references
  - Guide agent to ask for clarification when context is stale

- [ ] T062 [US7] Write unit tests for context tracking in `tests/unit/test_memory.py`
  - Test context storage after operations
  - Test context retrieval
  - Test context expiry/reset

- [ ] T063 [US7] Write integration test for context-aware flow in `tests/integration/test_chat_api.py`

**Checkpoint**: User Story 7 works - agent maintains conversation context

---

## Phase 10: Chat API Endpoints

**Purpose**: REST endpoints for frontend to communicate with agent

- [ ] T064 Add POST `/api/chat` endpoint in `src/mcp_server/server.py` (FR-027)
  - Accept ChatRequest (message, optional conversation_id)
  - Validate JWT token from Authorization header
  - Return SSE streaming response

- [ ] T065 Implement SSE streaming response handler in `src/mcp_server/server.py` (FR-013)
  - Stream: message_start, content_delta, tool_call, tool_result, message_end events
  - Handle errors gracefully with error event

- [ ] T066 Add GET `/api/conversations` endpoint in `src/mcp_server/server.py` (FR-031)
  - Return user's conversation list with pagination
  - Include message count and timestamps

- [ ] T067 Add GET `/api/conversations/{id}` endpoint in `src/mcp_server/server.py`
  - Return conversation with full message history
  - Validate user ownership (FR-029)

- [ ] T068 Add DELETE `/api/conversations/{id}` endpoint in `src/mcp_server/server.py`
  - Delete conversation and all messages
  - Validate user ownership

- [ ] T069 Implement conversation persistence in `src/mcp_server/memory.py` (FR-030, FR-032)
  - Save messages to database after each exchange
  - Load conversation history on resume

- [ ] T070 Write integration tests for chat API in `tests/integration/test_chat_api.py`
  - Test chat endpoint with valid JWT
  - Test chat endpoint without JWT (401)
  - Test conversation CRUD operations

---

## Phase 11: Frontend Chat UI

**Purpose**: Beautiful, mobile-responsive chat interface

### Chat Page & Layout

- [ ] T071 [P] Create chat page at `frontend/app/chat/page.tsx` (FR-019)
  - Server Component with auth check (FR-020)
  - Redirect to login if unauthenticated
  - Import ChatInterface client component

- [ ] T072 [P] Add Chat link to navigation in `frontend/components/navigation.tsx`
  - Add "Chat" link to main navigation
  - Highlight when on /chat route

### Chat Components

- [ ] T073 Create ChatInterface component in `frontend/components/chat-interface.tsx` (FR-021)
  - 'use client' directive
  - State: messages[], loading, error
  - Refs: messagesEndRef for auto-scroll

- [ ] T074 Create MessageBubble component in `frontend/components/chat/message-bubble.tsx`
  - Props: message (role, content, timestamp)
  - User messages: right-aligned, primary color
  - Assistant messages: left-aligned, secondary color
  - Show timestamp on hover

- [ ] T075 Create ChatInput component in `frontend/components/chat/chat-input.tsx`
  - Textarea with auto-resize
  - Send button with loading state
  - Enter to send, Shift+Enter for newline
  - Disable when loading

- [ ] T076 Create SuggestedPrompts component in `frontend/components/chat/suggested-prompts.tsx` (FR-026)
  - Show when conversation is empty
  - Prompts: "Add a task", "Show my tasks", "What's due today?"
  - Click to send prompt

- [ ] T077 Create TypingIndicator component in `frontend/components/chat/typing-indicator.tsx` (FR-023)
  - Animated dots while agent is processing
  - Show during loading state

- [ ] T078 Create ErrorDisplay component in `frontend/components/chat/error-display.tsx` (FR-024)
  - User-friendly error messages
  - Retry button for transient errors
  - Different styles for different error types

### API Client & SSE

- [ ] T079 Create chat API client in `frontend/lib/chat-api.ts`
  - sendMessage(message, conversationId?) function
  - Handle SSE streaming with EventSource or fetch
  - Parse stream events and yield to caller

- [ ] T080 Implement SSE stream handling in `frontend/components/chat-interface.tsx`
  - Handle message_start: create new assistant message
  - Handle content_delta: append to message
  - Handle tool_call: show tool indicator
  - Handle message_end: finalize message
  - Handle error: display error

- [ ] T081 Implement auto-scroll in `frontend/components/chat-interface.tsx` (FR-022)
  - Scroll to bottom on new message
  - Scroll during streaming
  - Don't interrupt user scroll-up

### Mobile-First Responsive Design

- [ ] T082 [P] Add mobile-first styles to ChatInterface (FR-025)
  - Full-height layout with fixed input
  - Touch-friendly tap targets (44px minimum)
  - Safe area insets for notched devices

- [ ] T083 [P] Add responsive styles to MessageBubble
  - Max-width: 85% on mobile, 70% on desktop
  - Readable font sizes (16px minimum)
  - Proper spacing between messages

- [ ] T084 [P] Add responsive styles to ChatInput
  - Full-width input on mobile
  - Larger touch target for send button
  - Keyboard-aware positioning

- [ ] T085 Add responsive styles to SuggestedPrompts
  - Stack vertically on mobile
  - Side-by-side on desktop
  - Touch-friendly buttons

### Conversation Management UI

- [ ] T086 Add conversation list sidebar in `frontend/components/chat/conversation-list.tsx`
  - List user's conversations
  - Show title and last message preview
  - Click to resume conversation

- [ ] T087 Add new conversation button
  - Clear current conversation
  - Reset to initial state with suggested prompts

- [ ] T088 Add delete conversation functionality
  - Confirmation dialog before delete
  - Remove from list after deletion

---

## Phase 12: Database Persistence

**Purpose**: Store conversation history in PostgreSQL

- [ ] T089 Create database migration for conversation tables
  - Add Conversation table: id, user_id, title, created_at, updated_at
  - Add Message table: id, conversation_id, role, content, tool_calls (JSON), created_at
  - Add indexes on user_id and conversation_id

- [ ] T090 Implement conversation CRUD in `src/mcp_server/memory.py`
  - create_conversation(user_id) -> conversation_id
  - get_conversation(conversation_id) -> Conversation with messages
  - update_conversation(conversation_id, title)
  - delete_conversation(conversation_id)

- [ ] T091 Implement message persistence in `src/mcp_server/memory.py`
  - add_message(conversation_id, role, content, tool_calls?)
  - get_messages(conversation_id, limit=10) -> list[Message]

- [ ] T092 Integrate persistence with chat flow
  - Create conversation on first message if no conversation_id
  - Save user message immediately
  - Save assistant message after completion
  - Auto-generate conversation title from first message

- [ ] T093 Write integration tests for persistence in `tests/integration/test_chat_persistence.py`
  - Test conversation creation
  - Test message persistence
  - Test conversation resume
  - Test user isolation (FR-029)

---

## Phase 13: Polish & Deployment

**Purpose**: Error handling, deployment config, documentation

### Error Handling

- [ ] T094 [P] Implement OpenAI rate limit handling in `src/mcp_server/agent.py`
  - Catch rate limit errors
  - Return user-friendly message with retry suggestion
  - Log for monitoring

- [ ] T095 [P] Implement backend connection error handling in `src/mcp_server/backend_client.py`
  - Catch connection errors
  - Return service unavailable message
  - Implement retry with exponential backoff

- [ ] T096 [P] Implement graceful degradation in `frontend/components/chat-interface.tsx`
  - Show offline indicator on network errors
  - Queue messages for retry (optional)
  - Clear error state on successful message

### Deployment Configuration

- [ ] T097 Add MCP server to `Procfile` for Railway deployment
  - Add worker process for MCP server on port 8001
  - Configure environment variables

- [ ] T098 Update `frontend/.env.production` with production MCP URL
  - Set NEXT_PUBLIC_MCP_URL to production endpoint

- [ ] T099 Add Railway configuration for MCP server port
  - Configure PORT environment variable
  - Add health check path

### Documentation

- [ ] T100 Update README.md with Phase III instructions
  - Add MCP server setup steps
  - Document environment variables
  - Add chat feature description

- [ ] T101 [P] Update `.env.example` with all Phase III variables
  - OPENAI_API_KEY
  - MCP_SERVER_PORT
  - MCP_BACKEND_URL

### End-to-End Testing

- [ ] T102 Write E2E test for complete chat flow in `tests/e2e/test_chat_flow.py`
  - Login user
  - Navigate to /chat
  - Send "Add task test" message
  - Verify task appears in response
  - Navigate to tasks page
  - Verify task exists

- [ ] T103 Write E2E test for mobile responsive in `tests/e2e/test_mobile_chat.py`
  - Test at 320px width
  - Verify all elements visible
  - Verify input is usable

- [ ] T104 Run quickstart.md validation
  - Follow all steps in quickstart.md
  - Verify MCP server starts
  - Verify chat endpoint responds

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-9 (User Stories)**: All depend on Phase 2 completion
  - US1 and US2 can run in parallel (both P1)
  - US3 and US4 can run in parallel after US1/US2 (both P2)
  - US5 and US6 can run in parallel (both P3)
  - US7 depends on previous stories for context testing
- **Phase 10 (Chat API)**: Depends on Phase 2, can run in parallel with user stories
- **Phase 11 (Frontend UI)**: Depends on Phase 10 (Chat API)
- **Phase 12 (Persistence)**: Depends on Phase 2 (models), can run in parallel with Phases 3-9
- **Phase 13 (Polish)**: Depends on all previous phases

### User Story Dependencies

```
Phase 2 (Foundation)
    |
    +---> US1 (P1) Create ----+
    |                         |
    +---> US2 (P1) List ------+---> US3 (P2) Update
    |                         |         |
    |                         +---> US4 (P2) Complete
    |                         |
    |                         +---> US5 (P3) Delete
    |                         |
    |                         +---> US6 (P3) Filter
    |                                   |
    +---> US7 (P4) Context <------------+
```

### Within Each User Story

- MCP tool implementation before OpenAI function definition
- System prompt updates after tool implementation
- Unit tests alongside implementation
- Integration tests after feature complete

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- US1 and US2 can run in parallel (different tools, no dependencies)
- US3 and US4 can run in parallel
- US5 and US6 can run in parallel
- All frontend components marked [P] can run in parallel
- All mobile styling tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 (Task Creation)
4. Complete Phase 4: US2 (Task Listing)
5. Complete Phase 10: Chat API (minimal)
6. Complete Phase 11: Frontend UI (minimal)
7. **STOP and VALIDATE**: Test full chat flow end-to-end
8. Deploy MVP if ready

### Incremental Delivery

1. Setup + Foundation → Core infrastructure ready
2. US1 + US2 + Chat API + UI → Basic chat MVP
3. Add US3 + US4 → Update and complete via chat
4. Add US5 + US6 → Full CRUD via chat
5. Add US7 → Context awareness
6. Add Persistence → Conversation history
7. Polish → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- [Found] = Foundational task required before any user story
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Test each MCP tool in isolation before integration testing
