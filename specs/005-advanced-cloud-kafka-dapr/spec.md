# Feature Specification: Phase 5 - Advanced Cloud Deployment with Kafka and Dapr

**Feature Branch**: `005-advanced-cloud-kafka-dapr`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "Phase 5: Advanced Cloud Deployment with Kafka, Dapr, and Oracle Cloud - implementing advanced features (recurring tasks, due dates, priorities, tags, search, filter) and event-driven architecture with Kafka and Dapr deployed to Oracle OKE"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Due Dates and Reminders (Priority: P1)

As a user, I can set due dates on tasks and receive reminders before they're due so I stay on top of time-sensitive responsibilities.

**Why this priority**: Core time management feature that transforms the app from a simple list to a proactive productivity tool. Most requested feature in productivity apps.

**Independent Test**: Can be fully tested by creating a task with a due date, waiting for the due time to approach, and verifying the reminder notification is received 1 hour before. Delivers immediate value by preventing missed deadlines.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I set a due date of "Tomorrow 3:00 PM", **Then** the task is saved with due_date field and a reminder event is scheduled for "Tomorrow 2:00 PM"
2. **Given** I have a task due in 50 minutes, **When** the system checks for upcoming reminders, **Then** I receive a browser notification with the task title and due time
3. **Given** I view my task list, **When** I see tasks with due dates, **Then** overdue tasks are highlighted in red
4. **Given** I complete a task that has a reminder scheduled, **When** the task is marked complete, **Then** the reminder is cancelled

---

### User Story 2 - Recurring Tasks (Priority: P2)

As a user, I can set tasks to repeat daily, weekly, or monthly so I don't have to manually recreate routine tasks.

**Why this priority**: Automates repetitive task creation, essential for routines like "Daily standup" or "Weekly report". High value-to-implementation ratio.

**Independent Test**: Can be fully tested by creating a recurring task with pattern "daily", marking it complete, and verifying a new instance is automatically created for tomorrow. Works standalone without other Phase 5 features.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set recurrence_pattern to "daily", **Then** the task is saved with the daily recurrence setting
2. **Given** I have a recurring task (pattern: weekly), **When** I mark it as complete, **Then** a Kafka event "task.completed" is published with the task data
3. **Given** the Recurring Task Service receives a "task.completed" event for a weekly task, **When** it processes the event, **Then** a new task instance is created with due_date set to next week
4. **Given** I have a monthly recurring task, **When** I view it in the task list, **Then** it displays a recurrence indicator icon

---

### User Story 3 - Task Priorities (Priority: P2)

As a user, I can assign priority levels (low, medium, high, urgent) to tasks so I can focus on what's most important first.

**Why this priority**: Enables users to triage and prioritize work effectively. Visual color coding provides at-a-glance status awareness.

**Independent Test**: Can be fully tested by creating tasks with different priority levels, sorting by priority, and verifying visual color coding (low=gray, medium=blue, high=orange, urgent=red). Delivers value independently.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I select priority "high", **Then** the task is saved with priority field set to "high"
2. **Given** I view my task list, **When** I see tasks with priorities, **Then** urgent tasks appear with red color, high with orange, medium with blue, low with gray
3. **Given** I have tasks with mixed priorities, **When** I sort by priority, **Then** tasks are ordered: urgent → high → medium → low
4. **Given** I update an existing task, **When** I change priority from "low" to "urgent", **Then** the task's visual indicator updates immediately

---

### User Story 4 - Task Tags and Categories (Priority: P3)

As a user, I can add tags to organize my tasks by category (e.g., work, personal, urgent) so I can filter and group related tasks.

**Why this priority**: Organizational feature that scales well for users with many tasks. Less critical than time management (P1) but highly valuable for power users.

**Independent Test**: Can be fully tested by adding tags to tasks, filtering by a specific tag, and verifying only tasks with that tag appear. Works independently of other features.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I add tags ["work", "urgent"], **Then** the task is saved with tags field containing both tags
2. **Given** I am adding tags to a task, **When** I type "w", **Then** an autocomplete dropdown shows existing tags starting with "w" (e.g., "work", "weekend")
3. **Given** I have tasks with various tags, **When** I filter by tag "personal", **Then** only tasks tagged "personal" are displayed
4. **Given** I try to add 11 tags to a task, **When** I save, **Then** the system limits to maximum 10 tags

---

### User Story 5 - Real-Time Search and Filter (Priority: P3)

As a user, I can search tasks by keyword and filter by status, priority, due date range, and tags so I can quickly find what I need.

**Why this priority**: Improves usability as task count grows. Search is essential for power users but not critical for MVP.

**Independent Test**: Can be fully tested by creating tasks with various attributes, searching for a keyword, and verifying matching tasks appear. Input is debounced 300ms to reduce server load.

**Acceptance Scenarios**:

1. **Given** I have tasks with titles containing "meeting" and "report", **When** I search for "meeting", **Then** only tasks with "meeting" in title or description appear
2. **Given** I am typing in the search box, **When** I pause typing for 300ms, **Then** the search executes (debounced to avoid excessive requests)
3. **Given** I have tasks with various statuses, **When** I filter by "completed", **Then** only completed tasks are shown
4. **Given** I have tasks with due dates, **When** I filter by due date range "Jan 1 - Jan 31", **Then** only tasks due within that range appear

---

### User Story 6 - Event-Driven Architecture with Kafka (Priority: P1)

As a developer, I need task operations to flow through Kafka so the system can scale horizontally and new services can subscribe to task events without coupling.

**Why this priority**: Architectural foundation for Phase 5. Enables all event-driven features (reminders, recurring tasks, audit logs). Must be P1 as it's infrastructure for other features.

**Independent Test**: Can be fully tested by creating/updating/deleting a task, then verifying "task-events" Kafka topic contains the corresponding event with correct payload. Works without UI changes.

**Acceptance Scenarios**:

1. **Given** I create a task via the API, **When** the task is saved to the database, **Then** a "task.created" event is published to Kafka topic "task-events"
2. **Given** I mark a task as complete, **When** the update succeeds, **Then** a "task.completed" event is published with the full task data
3. **Given** the Notification Service is running, **When** a "reminder.due" event is published to "reminders" topic, **Then** the service consumes it and logs the reminder
4. **Given** the Recurring Task Service is running, **When** a "task.completed" event for a recurring task is published, **Then** the service creates the next occurrence

---

### User Story 7 - Dapr Integration for Infrastructure Abstraction (Priority: P2)

As a developer, I need Dapr sidecars to abstract Kafka, PostgreSQL, and secrets so the code stays clean and infrastructure can be swapped without code changes.

**Why this priority**: Improves maintainability and portability. Priority P2 because we could implement directly with Kafka/Postgres libraries, but Dapr provides significant long-term value.

**Independent Test**: Can be fully tested by publishing an event via Dapr Pub/Sub API and verifying it reaches Kafka, then reading state via Dapr State API and verifying it queries PostgreSQL. Code doesn't import kafka-python or psycopg2.

**Acceptance Scenarios**:

1. **Given** the backend publishes an event via Dapr HTTP API, **When** calling POST to Dapr sidecar, **Then** the event appears in the Kafka topic
2. **Given** the backend saves conversation state via Dapr State API, **When** calling POST to Dapr sidecar, **Then** the data is persisted to Neon PostgreSQL
3. **Given** the backend needs an API key, **When** calling Dapr Secrets API, **Then** the secret is retrieved from Kubernetes secrets
4. **Given** we want to check for reminders, **When** a Dapr Jobs API trigger fires, **Then** the backend receives a callback at the scheduled time

---

### User Story 8 - Local Minikube Deployment (Priority: P2)

As a developer, I can deploy the full stack (Kafka, Dapr, all services) on Minikube locally so I can develop and test the event-driven architecture without cloud costs.

**Why this priority**: Essential for development iteration speed. Must work locally before cloud deployment. Priority P2 because it's development infrastructure, not user-facing.

**Independent Test**: Can be fully tested by running deployment scripts, verifying all pods are running, and executing a task operation that triggers a Kafka event and reminder. Works independently to validate architecture.

**Acceptance Scenarios**:

1. **Given** Minikube is running, **When** I deploy Strimzi Kafka operator, **Then** a single-broker Kafka cluster starts successfully
2. **Given** Kafka is running in Minikube, **When** I deploy Dapr, **Then** all Dapr components (pubsub.kafka, state.postgresql, scheduler) are healthy
3. **Given** Dapr is running, **When** I deploy the backend and frontend services, **Then** all services start with Dapr sidecars injected
4. **Given** all services are running locally, **When** I create a task with a due date, **Then** the full event flow (API → Kafka → Notification Service) works end-to-end

---

### User Story 9 - Oracle OKE Cloud Deployment (Priority: P3)

As a user, I can access the application deployed on Oracle OKE (always-free tier) so I have a production-grade, cloud-native deployment without ongoing costs.

**Why this priority**: Final deployment target. Priority P3 because local deployment must work first, and Oracle's free tier removes urgency (no time pressure from trial expiration).

**Independent Test**: Can be fully tested by deploying to OKE, accessing the public frontend URL, and verifying task operations work with Kafka events flowing through the cloud cluster. Delivers production-ready experience.

**Acceptance Scenarios**:

1. **Given** Oracle OKE cluster is provisioned (4 OCPUs, 24GB RAM - free tier), **When** I configure kubectl, **Then** I can connect to the cluster and see nodes
2. **Given** OKE cluster is ready, **When** I deploy Strimzi, Dapr, and application services via Helm, **Then** all pods start successfully
3. **Given** services are deployed on OKE, **When** I access the frontend URL, **Then** the web app loads and connects to the cloud backend
4. **Given** the app is running on OKE, **When** I create a task with recurrence, **Then** Kafka events flow, the recurring task service processes them, and the system auto-creates the next occurrence

---

### User Story 10 - Backward Compatibility with Phases 1-4 (Priority: P1)

As a user from Phases 1-4, all my existing features (basic CRUD, web app, AI chatbot, K8s deployment) continue to work without breaking when Phase 5 is deployed.

**Why this priority**: Non-negotiable. Cannot break existing functionality. Priority P1 because regression would lose all previous work value.

**Independent Test**: Can be fully tested by running Phase 1-4 test suites after Phase 5 deployment and verifying 100% pass rate. Existing users experience zero disruption.

**Acceptance Scenarios**:

1. **Given** Phase 5 database migrations add new columns (due_date, priority, tags, recurrence_pattern), **When** existing tasks are loaded, **Then** they display correctly with new fields defaulted (due_date=null, priority=medium, tags=[], recurrence_pattern=none)
2. **Given** I use the Phase 3 AI chatbot, **When** I say "Add a task to buy groceries", **Then** it works exactly as before (basic CRUD via MCP tools)
3. **Given** I access the Phase 2 web app, **When** I view my task list, **Then** all existing tasks appear (new optional fields don't break display)
4. **Given** the Phase 4 Kubernetes deployment is running, **When** Phase 5 services are added alongside, **Then** existing services continue operating normally

---

### Edge Cases

- **What happens when a user sets a due date in the past?** System accepts it but immediately marks it as overdue (red highlight), and no reminder is scheduled.
- **How does the system handle recurring tasks when the next occurrence would overlap with an incomplete previous occurrence?** System still creates the next occurrence; users can have multiple instances of the same recurring task simultaneously.
- **What if a Kafka broker goes down during an event publish?** Dapr Pub/Sub retries automatically with exponential backoff (configured in component YAML).
- **How are reminders handled across timezones?** Due dates are stored in UTC; frontend displays in user's local timezone (browser timezone detection).
- **What happens when the Notification Service is down and misses reminder events?** Events remain in Kafka topic (retention period: 7 days); when service restarts, it can catch up on missed reminders.
- **What if a user creates 1000 tags over time?** Autocomplete only shows top 20 most-used tags to avoid UI clutter.
- **How does filtering work when a task has multiple tags?** Filter shows tasks matching ANY of the selected tags (OR logic, not AND).
- **What happens when a recurring task is deleted?** Only the current instance is deleted; no future occurrences are created (recurrence stops).

## Requirements *(mandatory)*

### Functional Requirements

#### Advanced Task Features

- **FR-001**: System MUST allow users to set an optional due_date (datetime) on tasks
- **FR-002**: System MUST display overdue tasks (due_date < current time) highlighted in red
- **FR-003**: System MUST schedule a reminder event 1 hour before a task's due_date when due_date is set
- **FR-004**: System MUST allow users to select priority from enum values: low, medium, high, urgent (default: medium)
- **FR-005**: System MUST display tasks with color coding based on priority: low=gray (#6B7280), medium=blue (#3B82F6), high=orange (#F97316), urgent=red (#EF4444)
- **FR-006**: System MUST allow users to add up to 10 tags per task (array of strings)
- **FR-007**: System MUST provide autocomplete suggestions for tags based on existing tags across all user's tasks
- **FR-008**: System MUST allow users to set recurrence_pattern from enum values: none, daily, weekly, monthly (default: none)
- **FR-009**: System MUST automatically create the next occurrence of a recurring task when marked complete (next occurrence due_date calculated based on pattern)

#### Search and Filter

- **FR-010**: System MUST provide real-time search across task title and description fields
- **FR-011**: Search input MUST be debounced with 300ms delay to reduce server load
- **FR-012**: System MUST support filtering tasks by status (all, pending, completed)
- **FR-013**: System MUST support filtering tasks by priority (multiple selection allowed)
- **FR-014**: System MUST support filtering tasks by due date range (start date and end date)
- **FR-015**: System MUST support filtering tasks by tags (multiple tags, OR logic)
- **FR-016**: System MUST support sorting tasks by: due_date, priority, created_at, title (ascending or descending)

#### Event-Driven Architecture

- **FR-017**: System MUST publish a "task.created" event to Kafka topic "task-events" when a task is created
- **FR-018**: System MUST publish a "task.updated" event to Kafka topic "task-events" when a task is updated
- **FR-019**: System MUST publish a "task.completed" event to Kafka topic "task-events" when a task is marked complete
- **FR-020**: System MUST publish a "task.deleted" event to Kafka topic "task-events" when a task is deleted
- **FR-021**: System MUST publish a "reminder.due" event to Kafka topic "reminders" 1 hour before a task's due_date
- **FR-022**: Notification Service MUST consume "reminder.due" events and log notification details (user_id, task_id, title)
- **FR-023**: Recurring Task Service MUST consume "task.completed" events, check if task has recurrence_pattern != "none", and create next occurrence

#### Dapr Integration

- **FR-024**: Backend services MUST publish events via Dapr Pub/Sub HTTP API (not direct Kafka client libraries)
- **FR-025**: Backend services MUST save conversation state via Dapr State API (abstraction over PostgreSQL)
- **FR-026**: System MUST use Dapr Jobs API for scheduling reminder checks (not polling via cron bindings)
- **FR-027**: Backend services MUST retrieve secrets (API keys, DB credentials) via Dapr Secrets API

#### Infrastructure and Deployment

- **FR-028**: System MUST deploy Kafka via Strimzi operator on Kubernetes (1 broker for dev, 3 brokers for prod)
- **FR-029**: System MUST deploy Dapr on Kubernetes with components: pubsub.kafka, state.postgresql, scheduler, secretstores.kubernetes
- **FR-030**: System MUST be deployable on Minikube for local development
- **FR-031**: System MUST be deployable on Oracle OKE free tier (4 OCPUs, 24GB RAM)
- **FR-032**: All Phase 1-4 features MUST continue functioning after Phase 5 deployment (backward compatibility)

### Key Entities

- **Task** (extended from Phase 2):
  - Existing fields: id, user_id, title, description, completed, created_at, updated_at
  - New fields:
    - due_date (datetime, nullable): When the task is due
    - priority (enum: low, medium, high, urgent, default: medium): Task importance level
    - tags (array of strings, max 10): Organizational labels
    - recurrence_pattern (enum: none, daily, weekly, monthly, default: none): Repetition frequency

- **TaskEvent** (new):
  - event_type (string): "created", "updated", "completed", "deleted"
  - task_id (integer): Reference to the task
  - task_data (JSON): Full task object snapshot at event time
  - user_id (string): User who performed the action
  - timestamp (datetime): When the event occurred

- **ReminderEvent** (new):
  - task_id (integer): Reference to the task
  - title (string): Task title for notification display
  - due_at (datetime): When the task is due
  - remind_at (datetime): When to send the reminder (due_at - 1 hour)
  - user_id (string): User to notify

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with due date, priority, and tags in under 30 seconds (includes UI interaction time)
- **SC-002**: Search results appear within 500ms of the last keystroke (300ms debounce + 200ms query execution)
- **SC-003**: 95% of reminder notifications are delivered within 60 seconds of the scheduled time (1 hour before due)
- **SC-004**: Recurring task next occurrence is created within 10 seconds of marking previous occurrence as complete
- **SC-005**: Kafka cluster handles 1000 task events per second without message loss (measured via Kafka metrics)
- **SC-006**: All services deployed on Minikube start successfully within 5 minutes of running deployment scripts
- **SC-007**: Oracle OKE deployment serves user requests with p95 latency under 2 seconds (frontend to backend to database)
- **SC-008**: 100% of Phase 1-4 automated tests pass after Phase 5 deployment (backward compatibility verified)
- **SC-009**: Dapr sidecar adds less than 50ms latency overhead per request (measured at 50th percentile)
- **SC-010**: System remains operational when any single service replica fails (high availability via Kubernetes)

## Assumptions

1. **User Timezone Handling**: Due dates are stored in UTC in the database; frontend converts to user's browser timezone for display. No explicit timezone selection UI.

2. **Reminder Delivery Method**: Browser notifications are delivered when user has the app open in a browser tab. If tab is closed, reminders are stored and shown on next login. No email/SMS notifications in Phase 5.

3. **Tag Storage**: Tags are stored as a PostgreSQL array column (text[]) on the tasks table. No separate tags table or tag management UI beyond autocomplete.

4. **Kafka Retention**: Kafka topics retain events for 7 days (configurable in Strimzi). Missed events older than 7 days are lost if a service is down.

5. **Recurring Task Next Occurrence**: "Daily" means next day same time, "Weekly" means next week same day/time, "Monthly" means same day of next month (if day doesn't exist, last day of month).

6. **Notification Service Scope**: In Phase 5, Notification Service only logs reminders to stdout (no actual push notifications). Demonstrates event flow; real notifications are bonus.

7. **Search Scope**: Search is case-insensitive substring match on title and description. No fuzzy matching or advanced search operators in Phase 5.

8. **Filter Persistence**: Filters and sort settings are client-side only (not saved to database). Reset on page refresh.

9. **Oracle OKE Free Tier Limits**: Always-free tier provides 4 OCPUs and 24GB RAM total. Deployment must fit within these limits (1 broker Kafka, minimal replicas).

10. **Dapr State vs Direct DB**: Conversation state uses Dapr State API; tasks continue using direct SQLModel/PostgreSQL for transactional consistency. Dapr State is for chat history only.

11. **Existing Phase 3 Chatbot**: AI chatbot continues using existing MCP tools (add_task, list_tasks, etc.). New fields (due_date, priority, tags) are optional parameters the AI can extract from natural language.

12. **Backward Compatible Defaults**: Existing tasks (Phase 1-4) automatically get: due_date=null, priority=medium, tags=[], recurrence_pattern=none when schema is migrated.
