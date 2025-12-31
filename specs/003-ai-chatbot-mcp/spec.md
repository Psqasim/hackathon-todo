# Feature Specification: AI Chatbot with MCP Integration

**Feature Branch**: `003-ai-chatbot-mcp`
**Created**: 2025-12-30
**Status**: Draft
**Phase**: Phase III of TaskFlow Evolution
**Input**: User description: "Build an AI-powered chatbot interface using OpenAI Agent SDK (gpt-4o-mini) that allows users to manage tasks through natural language conversation, connected via MCP (Model Context Protocol) to the existing Phase II backend."

---

## Overview

Phase III extends the TaskFlow application with an AI-powered conversational interface. Users will manage their tasks through natural language commands in a chat interface, while the existing Phase II web application and database remain unchanged. The AI agent connects to the backend via a new MCP (Model Context Protocol) server that exposes task operations as tools.

### Architecture Summary

| Component | Description | Port |
|-----------|-------------|------|
| **Chat UI** | New `/chat` route in existing Next.js frontend | 3000 |
| **MCP Server** | New Python service exposing task tools | 8001 |
| **OpenAI Agent** | gpt-4o-mini with function calling | - |
| **FastAPI Backend** | Existing Phase II backend (NO CHANGES) | 8000 |
| **Database** | Existing Neon PostgreSQL (NO CHANGES) | - |

### Key Integration Points

- Chat UI authenticates users via existing Phase II JWT auth
- MCP Server receives JWT token and passes it to FastAPI backend
- All task operations go through existing REST API endpoints
- Conversation history stored in same PostgreSQL database

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

Users can create tasks by describing them in natural language. The AI agent extracts task details (title, description, priority, due date) and creates the task.

**Why this priority**: Task creation is the core functionality. Without it, the chatbot has no value. This story demonstrates the full MCP pipeline working end-to-end.

**Independent Test**: Can be fully tested by sending "Add task to buy groceries tomorrow with high priority" and verifying the task appears in the database and task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user in the chat interface, **When** user says "Add task to buy groceries", **Then** agent creates task with title "Buy groceries" and confirms creation with task details
2. **Given** an authenticated user, **When** user says "Remind me to call mom tomorrow at 2pm", **Then** agent creates task with title "Call mom", due date set to tomorrow, and confirms creation
3. **Given** an authenticated user, **When** user says "Add urgent task: finish report by Friday", **Then** agent creates task with title "Finish report", priority "urgent", due date as Friday, and confirms creation
4. **Given** an authenticated user, **When** user says "Add task" with no other details, **Then** agent asks for the task title before proceeding

---

### User Story 2 - Conversational Task Listing (Priority: P1)

Users can view their tasks by asking in natural language. The agent retrieves and displays tasks in a readable format.

**Why this priority**: Viewing tasks is essential for task management. Users need to see what they have before they can manage it.

**Independent Test**: Can be tested by asking "Show my tasks" and verifying the response lists all user's tasks with correct details.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 tasks, **When** user says "Show me all my tasks", **Then** agent displays all 3 tasks with titles, status, and due dates
2. **Given** an authenticated user with pending and completed tasks, **When** user says "What's pending?", **Then** agent displays only pending tasks
3. **Given** an authenticated user with no tasks, **When** user says "Show my tasks", **Then** agent responds that no tasks exist and suggests creating one
4. **Given** an authenticated user, **When** user says "What have I completed?", **Then** agent displays only completed tasks

---

### User Story 3 - Task Updates via Chat (Priority: P2)

Users can modify existing tasks through natural language commands. The agent identifies the task and applies changes.

**Why this priority**: Updating tasks is important but secondary to creating and viewing. Users need basic CRUD before modifications.

**Independent Test**: Can be tested by saying "Change the grocery task priority to urgent" and verifying the task's priority is updated.

**Acceptance Scenarios**:

1. **Given** a user with task titled "Buy groceries", **When** user says "Change grocery task priority to urgent", **Then** agent updates priority and confirms the change
2. **Given** a user with task "Call mom", **When** user says "Update call mom task description to 'Discuss birthday plans'", **Then** agent updates description and confirms
3. **Given** a user with multiple tasks containing "report", **When** user says "Update report task", **Then** agent asks for clarification on which task
4. **Given** a user with no matching task, **When** user says "Update the meeting task", **Then** agent responds that no matching task was found

---

### User Story 4 - Task Completion via Chat (Priority: P2)

Users can mark tasks as complete through natural language. The agent finds the matching task and toggles its completion status.

**Why this priority**: Completing tasks is the primary workflow outcome. It's essential but depends on tasks existing first.

**Independent Test**: Can be tested by saying "Mark grocery task as done" and verifying the task status changes to completed.

**Acceptance Scenarios**:

1. **Given** a pending task "Buy groceries", **When** user says "Mark grocery task as done", **Then** agent marks task complete and confirms
2. **Given** a completed task "Buy groceries", **When** user says "Unmark grocery task", **Then** agent marks task as pending and confirms
3. **Given** multiple tasks, **When** user says "I finished the report", **Then** agent finds report task and marks it complete
4. **Given** no matching task, **When** user says "Complete the meeting task", **Then** agent responds that no matching task was found

---

### User Story 5 - Task Deletion via Chat (Priority: P3)

Users can delete tasks through natural language commands. The agent confirms before deletion for safety.

**Why this priority**: Deletion is destructive and less common than other operations. Important but not critical for MVP.

**Independent Test**: Can be tested by saying "Delete the grocery task" and verifying the task is removed from the database.

**Acceptance Scenarios**:

1. **Given** a task "Buy groceries", **When** user says "Delete the grocery task", **Then** agent confirms which task and deletes upon confirmation
2. **Given** multiple similar tasks, **When** user says "Delete the task", **Then** agent asks for clarification on which task
3. **Given** a task "Old task", **When** user says "Remove old task", **Then** agent deletes task and confirms deletion
4. **Given** no matching task, **When** user says "Delete meeting task", **Then** agent responds that no matching task was found

---

### User Story 6 - Advanced Queries (Priority: P3)

Users can filter and search tasks using natural language queries with multiple criteria.

**Why this priority**: Advanced filtering enhances usability but is not essential for basic task management.

**Independent Test**: Can be tested by saying "Show urgent tasks due this week" and verifying filtered results.

**Acceptance Scenarios**:

1. **Given** tasks with various priorities, **When** user says "Show urgent tasks", **Then** agent displays only urgent priority tasks
2. **Given** tasks with due dates, **When** user says "What's due this week?", **Then** agent displays tasks due within current week
3. **Given** tasks with various statuses, **When** user says "Show pending high priority tasks", **Then** agent displays pending tasks with high priority
4. **Given** no matching tasks, **When** user says "Show urgent tasks", **Then** agent responds that no urgent tasks exist

---

### User Story 7 - Context Awareness (Priority: P4)

The agent maintains conversation context and handles follow-up questions referring to previous interactions.

**Why this priority**: Context awareness improves UX but the chatbot is fully functional without it. Enhancement feature.

**Independent Test**: Can be tested by creating a task, then saying "Change that to tomorrow" and verifying the last mentioned task is updated.

**Acceptance Scenarios**:

1. **Given** user just created task "Buy groceries", **When** user says "Make that high priority", **Then** agent updates the groceries task priority
2. **Given** user just viewed a single task, **When** user says "Mark it done", **Then** agent marks that task as complete
3. **Given** user asked about tasks due tomorrow, **When** user says "Delete them all", **Then** agent confirms which tasks and deletes upon confirmation
4. **Given** no recent context, **When** user says "Update that", **Then** agent asks for clarification on which task

---

### Edge Cases

- What happens when the OpenAI API rate limit is exceeded? (Display friendly message, suggest retry)
- How does system handle network disconnection during chat? (Show offline indicator, queue messages)
- What happens when MCP server is unavailable? (Display service unavailable message)
- How does system handle malformed natural language input? (Agent asks for clarification)
- What happens when user tries to access another user's tasks? (JWT validation prevents this)
- How does system handle very long conversation histories? (Trim to last 10 messages)
- What happens when task title contains ambiguous keywords? (Agent asks for clarification)
- How does system handle concurrent modifications? (Last write wins, consistent with Phase II)

---

## Requirements *(mandatory)*

### Functional Requirements

#### MCP Server Requirements

- **FR-001**: System MUST expose an MCP server on port 8001 with task management tools
- **FR-002**: MCP server MUST implement `add_task` tool accepting title (required), description, priority, due_date, and tags
- **FR-003**: MCP server MUST implement `list_tasks` tool with optional status filter (all, pending, completed)
- **FR-004**: MCP server MUST implement `get_task` tool accepting task_id
- **FR-005**: MCP server MUST implement `update_task` tool accepting task_id and optional title, description, priority, due_date
- **FR-006**: MCP server MUST implement `delete_task` tool accepting task_id
- **FR-007**: MCP server MUST implement `complete_task` tool accepting task_id to toggle completion
- **FR-008**: MCP server MUST implement `search_tasks` tool accepting query string for keyword search
- **FR-009**: MCP server MUST validate JWT token and pass user_id to all backend API calls
- **FR-010**: MCP server MUST call existing FastAPI endpoints (NO direct database access)

#### OpenAI Agent Requirements

- **FR-011**: System MUST use OpenAI gpt-4o-mini model for the chat agent
- **FR-012**: Agent MUST be configured with function calling enabled
- **FR-013**: Agent MUST use streaming responses for real-time UX
- **FR-014**: Agent MUST maintain conversation history (last 10 messages minimum)
- **FR-015**: Agent MUST parse natural language dates (tomorrow, next week, in 3 days, etc.)
- **FR-016**: Agent MUST extract priority keywords (urgent, important, low priority, etc.)
- **FR-017**: Agent MUST confirm all destructive actions (delete) before executing
- **FR-018**: Agent MUST provide friendly, conversational responses

#### Chat UI Requirements

- **FR-019**: System MUST add `/chat` route to existing Next.js frontend
- **FR-020**: Chat page MUST require user authentication (redirect to login if unauthenticated)
- **FR-021**: Chat UI MUST display message history with user/agent distinction
- **FR-022**: Chat UI MUST auto-scroll to latest message
- **FR-023**: Chat UI MUST show typing indicator during agent processing
- **FR-024**: Chat UI MUST display error messages in a user-friendly format
- **FR-025**: Chat UI MUST be responsive (mobile-first design, 320px minimum width)
- **FR-026**: Chat UI MUST provide suggested prompts for new users

#### Authentication Requirements

- **FR-027**: Chat endpoint MUST validate JWT token before processing
- **FR-028**: MCP server MUST reject requests without valid JWT token
- **FR-029**: Each user MUST only see and modify their own tasks

#### Conversation Persistence Requirements

- **FR-030**: System MUST store conversation history in PostgreSQL database
- **FR-031**: System MUST support resuming conversations after page refresh
- **FR-032**: System MUST associate conversations with authenticated user_id

### Key Entities

- **Conversation**: Represents a chat session. Attributes: id, user_id, created_at, updated_at
- **Message**: Represents a single chat message. Attributes: id, conversation_id, role (user/assistant), content, tool_calls (optional), created_at
- **Tool Call**: Represents an MCP tool invocation. Attributes: tool_name, parameters, result, timestamp

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete basic task operations (create, list, complete) through chat in under 30 seconds per operation
- **SC-002**: Agent correctly interprets natural language input at least 90% of the time for standard task commands
- **SC-003**: Chat interface loads and becomes interactive within 3 seconds on standard broadband connection
- **SC-004**: System maintains conversation context for at least 10 consecutive messages
- **SC-005**: All 5 basic task operations (create, read, update, delete, complete) work correctly via chat
- **SC-006**: Chat UI is fully usable on mobile devices (320px width minimum)
- **SC-007**: Error messages are displayed within 2 seconds of error occurrence
- **SC-008**: Same users, database, and tasks work across Phase I console, Phase II web, and Phase III chat interfaces
- **SC-009**: Natural language date parsing handles at least: "today", "tomorrow", "next week", "in N days", specific dates
- **SC-010**: Natural language priority parsing handles at least: "urgent", "high", "medium", "low", "asap", "critical"

---

## Assumptions

1. **OpenAI API Access**: User has valid OpenAI API key with access to gpt-4o-mini model
2. **Phase II Complete**: Phase II full-stack web application is deployed and functional
3. **Existing Auth**: Phase II JWT authentication is working and will be reused
4. **Database Schema**: Conversation and Message tables will be added to existing schema
5. **MCP Protocol**: Using FastMCP library for MCP server implementation
6. **Date Parsing**: Using dateparser library for natural language date parsing
7. **Streaming**: OpenAI streaming API is available and functional
8. **Same Codebase**: MCP server lives in same monorepo under `src/mcp_server/`

---

## Dependencies

- Phase II FastAPI backend (existing, no changes required)
- Phase II Next.js frontend (adding new /chat route)
- Phase II PostgreSQL database (adding conversation tables)
- OpenAI API (gpt-4o-mini model)
- FastMCP library (MCP server implementation)
- dateparser library (natural language date parsing)

---

## Out of Scope

- Voice input/output (future Phase or bonus)
- Multi-language support (future bonus feature)
- Real-time notifications/reminders
- File attachments to tasks
- Shared/collaborative tasks
- Offline mode for chat
- Chat export functionality
- Custom agent personalities

---

## Constraints

- MCP server MUST NOT access database directly (must use FastAPI endpoints)
- Chat UI MUST reuse existing Phase II authentication
- No changes to existing Phase II API endpoints
- Agent model fixed to gpt-4o-mini (cost optimization)
- Conversation history limited to last 10 messages (context window management)
