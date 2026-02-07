# Implementation Plan: Phase 5 - Advanced Cloud Deployment with Kafka and Dapr

**Branch**: `005-advanced-cloud-kafka-dapr` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-advanced-cloud-kafka-dapr/spec.md`

## Summary

Phase 5 transforms the TaskFlow application into a cloud-native, event-driven system by:
1. **Adding minimal missing features**: Sort dropdown, recurring task automation, and reminder notifications
2. **Implementing event-driven architecture**: Kafka (via Strimzi) for task events and reminders with Dapr pub/sub abstraction
3. **Deploying to cloud**: Oracle OKE free tier with full Kafka + Dapr stack

**Key Context from User**: Most Phase 5 features are ALREADY IMPLEMENTED (search, priority, due date, tags, filters, AI chatbot, K8s/Helm). This plan focuses on the 3 missing features + event architecture + cloud deployment.

**Technical Approach**:
- Use existing Task model (already has priority, due_date, tags, is_recurring, recurrence_pattern)
- Add sort parameter to API endpoints
- Publish task events to Kafka via Dapr HTTP API (no direct Kafka client)
- Create Notification Service and Recurring Task Service as new microservices
- Deploy Strimzi Kafka and Dapr to Minikube first, then Oracle OKE

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend - Next.js 16)
**Primary Dependencies**:
- Backend: FastAPI 0.115+, SQLModel 0.0.16+, httpx 0.27+ (for Dapr HTTP API)
- Frontend: Next.js 16, React 19, Tailwind CSS
- Event: Apache Kafka via Strimzi 0.43+, Dapr 1.13+
- Database: Neon PostgreSQL (external, already configured)

**Storage**: Neon PostgreSQL with SQLModel ORM (Phase 2-5), Kafka for event streaming
**Testing**: pytest for backend (80%+ coverage), Jest/React Testing Library for frontend
**Target Platform**:
- Local: Minikube 1.33+ with Docker Desktop
- Cloud: Oracle OKE free tier (4 OCPUs, 24GB RAM)

**Project Type**: Web application (monorepo structure: /src for backend, /frontend for Next.js)
**Performance Goals**:
- Search results: <500ms (300ms debounce + 200ms query)
- Kafka throughput: 1000 events/sec
- Reminder delivery: 95% within 60s of scheduled time
- p95 latency on OKE: <2s end-to-end

**Constraints**:
- Oracle free tier: 4 OCPUs, 24GB RAM total (1-broker Kafka, minimal replicas)
- Backward compatibility: 100% of Phase 1-4 tests must pass
- No direct Kafka libraries: Use Dapr HTTP API for pub/sub
- Reminder delivery: Browser notifications only (no email/SMS in Phase 5)

**Scale/Scope**:
- Multi-user application (already supports user_id isolation)
- 3 new features + 2 new microservices + Kafka/Dapr infrastructure
- 10 user stories, 32 functional requirements (from spec)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Agent Architecture Patterns
- **Orchestrator Agent**: Existing Main Orchestrator coordinates all subagents ✅
- **Subagent Design**: Task Manager, Storage Handler, UI Controller agents already exist ✅
- **New Agents**: Notification Service and Recurring Task Service will follow subagent pattern
- **Agent Communication**: Uses typed Pydantic models ✅
- **Verdict**: PASS - New services integrate into existing multi-agent architecture

### ✅ Skill Reusability Standards
- **Technology Agnosticism**: Task operations work across console/web/chatbot ✅
- **Skill Contracts**: Pydantic models for Task, TaskPriority, RecurrencePattern already defined ✅
- **Skill Testability**: Existing 80%+ coverage; new features will maintain this ✅
- **Verdict**: PASS - New features extend existing skill contracts without breaking existing skills

### ✅ Separation of Concerns
- **UI Layer**: Next.js frontend (Phase 2) + ChatKit (Phase 3) ✅
- **Business Logic Layer**: Task Manager Agent owns business rules ✅
- **Data Layer**: Storage Handler Agent with PostgreSQL backend ✅
- **New Event Layer**: Dapr pub/sub abstraction cleanly separates event infrastructure
- **Verdict**: PASS - Event layer adds new concern without violating existing separation

### ✅ Evolution Strategy
- **Phase I-IV Complete**: Console app → Web app → Chatbot → Local K8s ✅
- **Phase V Additions**: Event-driven architecture with Kafka/Dapr
- **Non-Breaking**: Existing APIs remain unchanged; events are additive
- **Migration**: Database schema adds columns with defaults (due_date=null, priority=medium)
- **Verdict**: PASS - Phase 5 builds on Phase 4 without breaking existing functionality

### ✅ Testing Standards
- **Test Hierarchy**: Unit, integration, e2e tests already in place ✅
- **Coverage Requirements**: Current 80%+ overall, 90%+ for skills ✅
- **TDD Workflow**: Red-Green-Refactor enforced ✅
- **New Tests Required**:
  - Unit tests for sort logic, recurring task creation, reminder scheduling
  - Integration tests for Dapr pub/sub, Kafka message flow
  - Contract tests for new Notification Service and Recurring Task Service APIs
- **Verdict**: PASS - TDD workflow continues; new features require new test coverage

### ✅ Code Quality Requirements
- **Python Standards**: Python 3.13+, type hints, docstrings, PEP 8 ✅
- **Dependency Management**: UV for packages, dependencies pinned ✅
- **Code Organization**: DRY, Single Responsibility, max 50 lines/function ✅
- **Naming Conventions**: snake_case, PascalCase, SCREAMING_SNAKE_CASE ✅
- **Verdict**: PASS - Existing codebase meets all quality standards

### ✅ Error Handling
- **Error Principles**: Graceful handling, no crashes, clear messages ✅
- **Error Types**: ValidationError, NotFoundError, AuthorizationError defined ✅
- **Error Propagation**: Result types, correlation IDs ✅
- **New Error Types Required**:
  - `EventPublishError`: Dapr pub/sub failures
  - `KafkaConnectionError`: Kafka cluster unavailable
- **Verdict**: PASS - Error handling infrastructure ready for event errors

### ✅ Spec-Driven Development
- **Specification First**: spec.md complete with 10 user stories ✅
- **Agent Documentation**: All agents documented ✅
- **Skill Documentation**: Pydantic models with docstrings ✅
- **Implementation Fidelity**: This plan follows spec exactly ✅
- **Verdict**: PASS - Spec-driven workflow followed

**GATE RESULT**: ✅ ALL GATES PASS - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/005-advanced-cloud-kafka-dapr/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── checklists/          # Quality validation (already created)
│   └── requirements.md
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── kafka-events.yaml
│   ├── dapr-components.yaml
│   └── notification-api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Current Structure** (already exists):
```text
hackathon-todo/
├── src/                      # Backend source (Python FastAPI)
│   ├── agents/              # Orchestrator, TaskManager, StorageHandler, UIController ✅
│   ├── adapters/            # Console adapter ✅
│   ├── auth/                # JWT authentication ✅
│   ├── backends/            # Memory, PostgreSQL backends ✅
│   ├── interfaces/          # API endpoints ✅
│   ├── mcp_server/          # MCP server for AI chatbot (Phase 3) ✅
│   ├── models/              # Pydantic models (Task, User, etc.) ✅
│   ├── app.py               # FastAPI application entry ✅
│   └── db.py                # Database session management ✅
├── frontend/                 # Next.js frontend ✅
│   ├── app/                 # Next.js App Router pages ✅
│   ├── components/          # React components ✅
│   ├── lib/                 # Utilities and API client ✅
│   └── middleware.ts        # Better Auth middleware ✅
├── tests/                    # Test suite ✅
│   ├── unit/
│   ├── integration/
│   └── contract/
├── k8s/                      # Kubernetes manifests (Phase 4) ✅
│   └── base/
├── helm/                     # Helm charts (Phase 4) ✅
│   └── taskflow/
└── scripts/                  # Deployment scripts ✅
```

**New Structure** (to be added in Phase 5):
```text
hackathon-todo/
├── src/
│   ├── services/                  # NEW: Microservices directory
│   │   ├── notification/          # NEW: Notification Service
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # FastAPI app subscribing to reminders
│   │   │   ├── models.py         # ReminderEvent Pydantic model
│   │   │   ├── config.py         # Service configuration
│   │   │   ├── Dockerfile        # Container image
│   │   │   └── requirements.txt  # Python dependencies
│   │   └── recurring_task/        # NEW: Recurring Task Service
│   │       ├── __init__.py
│   │       ├── main.py           # FastAPI app subscribing to task-events
│   │       ├── models.py         # TaskEvent Pydantic model
│   │       ├── logic.py          # Next occurrence calculation
│   │       ├── config.py
│   │       ├── Dockerfile
│   │       └── requirements.txt
│   └── events/                    # NEW: Event publishing logic
│       ├── __init__.py
│       ├── publisher.py          # Dapr HTTP pub/sub client
│       └── models.py             # Event schemas (TaskEvent, ReminderEvent)
├── k8s/
│   ├── kafka/                     # NEW: Kafka manifests
│   │   ├── namespace.yaml        # kafka namespace
│   │   ├── strimzi-operator.yaml # Strimzi operator deployment
│   │   ├── kafka-cluster.yaml    # Kafka cluster (1 broker for dev, 3 for prod)
│   │   └── topics.yaml           # task-events, reminders topics
│   └── dapr/                      # NEW: Dapr components
│       ├── pubsub-kafka.yaml     # Dapr Kafka pub/sub component
│       ├── state-postgresql.yaml # Dapr State component (Neon DB)
│       ├── cron-binding.yaml     # Dapr cron binding (reminder checks)
│       └── secretstores-k8s.yaml # Dapr Kubernetes secrets
├── helm/taskflow/templates/
│   ├── notification-deployment.yaml  # NEW: Notification Service K8s deployment
│   ├── recurring-deployment.yaml     # NEW: Recurring Task Service deployment
│   └── dapr-components.yaml          # NEW: Dapr component configs
└── docs/
    └── phase-5/                   # NEW: Phase 5 documentation
        ├── kafka-setup.md        # Strimzi installation guide
        ├── dapr-setup.md         # Dapr installation guide
        ├── oracle-oke-setup.md   # Oracle Cloud setup guide
        └── event-flow.md         # Event architecture diagrams
```

**Structure Decision**: Extending existing monorepo structure with new `/src/services/` directory for microservices and `/k8s/kafka`, `/k8s/dapr` for infrastructure. This maintains backward compatibility while cleanly organizing event-driven components. Frontend and backend remain at root level (established in Phase 2).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations | All constitution gates passed |

## Phase 0: Research & Discovery

**Objective**: Resolve unknowns from Technical Context and establish best practices for Kafka, Dapr, and Oracle OKE deployment.

### Research Tasks

#### R1: Dapr Pub/Sub HTTP API Patterns
**Question**: How to publish events to Kafka via Dapr HTTP API without direct kafka-python library?
**Research Areas**:
- Dapr pub/sub HTTP endpoint format: `POST http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}`
- Request body structure for event publishing
- Error handling and retry logic for failed publishes
- Performance characteristics (latency overhead)

**Decision Criteria**:
- API call simplicity (prefer httpx over requests for async support)
- Error visibility (structured error responses)
- Backward compatibility (can add Dapr without breaking existing code)

#### R2: Strimzi Kafka Configuration for Resource-Constrained Environments
**Question**: Optimal Kafka cluster configuration for Oracle OKE free tier (4 OCPUs, 24GB RAM)?
**Research Areas**:
- Single-broker vs. multi-broker for dev/prod
- Memory allocation per broker (JVM heap size)
- Topic replication factor (1 for dev, 3 for prod)
- Retention policy (7 days default, configurable)
- Resource requests/limits for K8s pods

**Decision Criteria**:
- Fits within Oracle free tier (dev profile: 1 broker, 2GB RAM)
- Production-ready patterns for future scaling (prod profile: 3 brokers, 4GB RAM each)
- Balances reliability (replication) with resource efficiency

#### R3: Dapr Jobs API vs. Cron Bindings for Reminder Scheduling
**Question**: Should reminders use Dapr Jobs API (exact time triggers) or Cron Bindings (polling)?
**Research Areas**:
- Dapr Jobs API: Schedule job at exact datetime, callback on trigger
- Cron Bindings: Periodic polling (e.g., every 5 minutes), check DB for due reminders
- Latency: Jobs API (0-5s delay) vs. Cron (up to 5min delay)
- Complexity: Jobs API (schedule per task) vs. Cron (single poller)

**Decision Criteria**:
- Reminder delivery precision (1 hour before due date ± acceptable latency)
- System simplicity (prefer simpler solution if latency acceptable)
- Scalability (thousands of scheduled reminders)

**Preliminary Decision** (from spec context): Use Dapr Jobs API for exact-time triggers (FR-026 in spec)

#### R4: Oracle OKE Free Tier Provisioning and kubectl Configuration
**Question**: Steps to create OKE cluster and configure local kubectl access?
**Research Areas**:
- Oracle Cloud free tier sign-up process
- OKE cluster creation via Oracle Cloud Console
- Always-free tier limits (4 OCPUs, 24GB RAM, 2 worker nodes)
- kubectl config download and context setup (`oci ce cluster create-kubeconfig`)
- OCI CLI installation and authentication

**Decision Criteria**:
- Simplicity of provisioning (prefer UI over CLI if easier)
- kubectl integration (must support standard kubectl commands)
- Cost validation (ensure no charges on free tier)

#### R5: Recurring Task Next Occurrence Calculation Logic
**Question**: How to calculate next occurrence for daily/weekly/monthly recurrence patterns?
**Research Areas**:
- Daily: Add 1 day to current due_date
- Weekly: Add 7 days to current due_date
- Monthly: Add 1 month (handle month-end edge cases: Jan 31 → Feb 28/29)
- Timezone handling: Store due_date in UTC, calculate in UTC
- Edge case: Task completed after next occurrence already passed

**Decision Criteria**:
- Simplicity (use datetime.timedelta for daily/weekly, dateutil.relativedelta for monthly)
- Correctness (handle February 29, months with 30/31 days)
- User expectations (next occurrence is always in the future)

#### R6: Browser Notification API Integration Patterns
**Question**: How to trigger browser notifications from Notification Service?
**Research Areas**:
- Browser Notification API (`Notification.requestPermission()`, `new Notification()`)
- Push API for background notifications (requires service worker)
- Phase 5 scope: Notification Service logs to stdout (FR-022), frontend polls or uses WebSocket
- WebSocket integration: Server-Sent Events (SSE) vs. WebSocket for real-time push

**Decision Criteria**:
- Phase 5 simplicity: Stdout logging sufficient for MVP
- Future extensibility: Design service to support real push notifications later
- User experience: Acceptable if notifications shown on next page load (stored in DB)

**Preliminary Decision** (from spec Assumption #2): Phase 5 only logs reminders; real notifications are future enhancement

### Research Outputs

**Format**: `research.md` document with:
```markdown
# Phase 5 Research Findings

## R1: Dapr Pub/Sub HTTP API Patterns
**Decision**: Use httpx for async HTTP calls to Dapr sidecar
**Rationale**: [findings]
**Implementation**: POST http://localhost:3500/v1.0/publish/taskflow-pubsub/task-events

## R2: Strimzi Kafka Configuration
**Decision**: [dev vs. prod profiles]
**Rationale**: [resource analysis]
**Implementation**: [YAML config snippets]

[...R3-R6...]
```

**Output**: `specs/005-advanced-cloud-kafka-dapr/research.md`

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all research tasks resolved

### 1.1 Data Model Design

**Objective**: Document data model changes and new entities for Phase 5.

**Existing Entities** (from `src/models/tasks.py`):
```python
class Task(BaseModel):
    id: str
    title: str
    description: str | None
    status: Literal["pending", "completed"]
    priority: TaskPriority  # ✅ Already exists (low, medium, high, urgent)
    due_date: datetime | None  # ✅ Already exists
    tags: list[str]  # ✅ Already exists
    is_recurring: bool  # ✅ Already exists
    recurrence_pattern: RecurrencePattern | None  # ✅ Already exists (daily, weekly, monthly)
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
```

**Database Schema** (SQLModel `TaskDB`):
- ✅ All Phase 5 fields already exist in database schema
- ✅ Migration not required (fields added in earlier phases)

**New Entities** (to be defined in Phase 1):

```python
# src/events/models.py
class TaskEvent(BaseModel):
    """Event published to Kafka when task operations occur."""
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_id: str
    user_id: str
    task_data: dict  # Full task JSON snapshot
    timestamp: datetime

class ReminderEvent(BaseModel):
    """Event published to Kafka for scheduled reminders."""
    task_id: str
    user_id: str
    title: str
    due_at: datetime
    remind_at: datetime  # due_at - 1 hour
```

**Output**: `specs/005-advanced-cloud-kafka-dapr/data-model.md`

### 1.2 API Contract Design

**Objective**: Define new API endpoints and event schemas.

#### Modified Endpoints (add sort parameter):

```yaml
# GET /api/{user_id}/tasks
parameters:
  - name: status
    in: query
    schema:
      type: string
      enum: [all, pending, completed]
  - name: sort_by  # NEW
    in: query
    schema:
      type: string
      enum: [due_date, priority, created_at, title]
      default: created_at
  - name: sort_order  # NEW
    in: query
    schema:
      type: string
      enum: [asc, desc]
      default: desc
```

#### Kafka Event Schemas:

```yaml
# contracts/kafka-events.yaml
topics:
  task-events:
    schema:
      event_type: string  # created, updated, completed, deleted
      task_id: string
      user_id: string
      task_data: object
      timestamp: datetime
    retention: 7 days
    partitions: 3
    replication: 1 (dev), 3 (prod)

  reminders:
    schema:
      task_id: string
      user_id: string
      title: string
      due_at: datetime
      remind_at: datetime
    retention: 7 days
    partitions: 3
    replication: 1 (dev), 3 (prod)
```

#### Dapr Component Contracts:

```yaml
# contracts/dapr-components.yaml
pubsub.kafka:
  name: taskflow-pubsub
  type: pubsub.kafka
  metadata:
    brokers: "taskflow-kafka-bootstrap:9092"
    consumerGroup: "taskflow-backend"

state.postgresql:
  name: taskflow-statestore
  type: state.postgresql
  metadata:
    connectionString: "{env:DATABASE_URL}"

jobs.scheduler:
  name: taskflow-jobs
  type: jobs.scheduler

secretstores.kubernetes:
  name: taskflow-secrets
  type: secretstores.kubernetes
```

#### Notification Service API:

```yaml
# contracts/notification-api.yaml
POST /api/notifications/callback  # Dapr calls this on reminder trigger
request:
  job_data:
    task_id: string
    user_id: string
    title: string
response:
  status: "SUCCESS" | "RETRY" | "DROP"
```

**Output**:
- `specs/005-advanced-cloud-kafka-dapr/contracts/kafka-events.yaml`
- `specs/005-advanced-cloud-kafka-dapr/contracts/dapr-components.yaml`
- `specs/005-advanced-cloud-kafka-dapr/contracts/notification-api.yaml`

### 1.3 Quickstart Guide

**Objective**: Create step-by-step guide for developers to run Phase 5 locally.

**Contents**:
1. Prerequisites (Minikube, Docker Desktop, kubectl, Helm)
2. Install Strimzi Kafka operator
3. Deploy Kafka cluster
4. Install Dapr on Minikube
5. Deploy Dapr components
6. Deploy TaskFlow services
7. Verify event flow (create task → check Kafka topic → see reminder log)
8. Troubleshooting common issues

**Output**: `specs/005-advanced-cloud-kafka-dapr/quickstart.md`

### 1.4 Agent Context Update

**Objective**: Update Claude Code context with new technologies from this plan.

**Command**: `.specify/scripts/bash/update-agent-context.sh claude`

**Updates to CLAUDE.md**:
- Add Kafka/Strimzi to technology stack
- Add Dapr pub/sub patterns
- Add event-driven architecture concepts
- Add Oracle OKE deployment instructions
- Preserve existing Phase 1-4 context

**Output**: Updated `/CLAUDE.md` file

## Phase 2: Task Breakdown (Future Step)

**Note**: Task breakdown happens in `/sp.tasks` command, NOT in `/sp.plan`.

This plan provides the foundation for task generation. Tasks will reference:
- Data models from `data-model.md`
- API contracts from `contracts/`
- Architecture decisions from `research.md`
- Implementation order from this plan

## Implementation Order

**Sequence**: Part A → Part B → Part C (as specified by user)

### Part A: Missing Features (Implement First, Works Without Kafka)

**Priority**: Implement these features to work WITHOUT Kafka initially, then add event publishing.

1. **Sort Dropdown** (US-5.5 partial)
   - Backend: Add `sort_by` and `sort_order` query parameters to `GET /api/{user_id}/tasks`
   - Frontend: Add sort dropdown component to task list header
   - Implementation: Simple SQL ORDER BY clause in PostgreSQL query

2. **Recurring Tasks** (US-5.2)
   - Backend: When task marked complete, check `is_recurring` field
   - If true, create next occurrence with calculated `due_date`
   - Frontend: Add recurrence selector to task creation/edit form (already exists in Task model)

3. **Reminder Notifications** (US-5.1)
   - Backend: When task created/updated with `due_date`, calculate `remind_at = due_date - 1 hour`
   - Store reminder trigger (table or in-memory scheduler)
   - Frontend: Request browser notification permission on first load
   - Notification: Simple browser notification when reminder due (polling approach first)

### Part B: Event-Driven Architecture on Minikube (Add Kafka + Dapr)

**Priority**: Local development and testing before cloud deployment.

4. **Install Strimzi Kafka** (US-5.6)
   - Create `kafka` namespace
   - Apply Strimzi operator YAML
   - Create Kafka cluster (1 broker, ephemeral storage for dev)
   - Create topics: `task-events`, `reminders`

5. **Install Dapr** (US-5.7)
   - Run `dapr init -k` to install Dapr control plane
   - Create Dapr components: `pubsub.kafka`, `state.postgresql`, `jobs.scheduler`, `secretstores.kubernetes`

6. **Update Backend to Publish Events** (US-5.6)
   - Create `src/events/publisher.py` with Dapr HTTP pub/sub client
   - Update Task Manager Agent: Publish `task.created`, `task.updated`, `task.completed`, `task.deleted` events
   - Update reminder scheduler: Publish `reminder.due` events

7. **Create Notification Service** (US-5.1, US-5.6)
   - New FastAPI service in `src/services/notification/`
   - Subscribe to `reminders` topic via Dapr
   - Log notification details to stdout (Phase 5 scope)
   - Dockerfile and K8s deployment manifest

8. **Create Recurring Task Service** (US-5.2, US-5.6)
   - New FastAPI service in `src/services/recurring_task/`
   - Subscribe to `task-events` topic via Dapr
   - On `task.completed` event, check `is_recurring` and create next occurrence
   - Dockerfile and K8s deployment manifest

9. **Deploy to Minikube** (US-5.8)
   - Update Helm chart with new services
   - Deploy full stack: Kafka, Dapr, Backend, Frontend, Notification, Recurring Task
   - Verify end-to-end event flow

### Part C: Oracle Cloud Deployment (OKE)

**Priority**: Production deployment after Minikube validation.

10. **Oracle Cloud Setup** (US-5.9)
    - Sign up for Oracle Cloud free tier
    - Create OKE cluster (4 OCPUs, 24GB RAM, always-free tier)
    - Configure `oci` CLI and generate `kubectl` config
    - Verify cluster connectivity

11. **Deploy to OKE** (US-5.9)
    - Deploy Strimzi Kafka to OKE (update resource limits for free tier)
    - Deploy Dapr to OKE
    - Deploy TaskFlow services via Helm (update values.yaml for OKE)
    - Configure LoadBalancer or Ingress for frontend access

12. **Verification & Testing** (US-5.10)
    - Run Phase 1-4 test suites (100% must pass for backward compatibility)
    - Test event flow: Create task → Kafka event → Notification log
    - Test recurring tasks: Mark recurring task complete → Next occurrence created
    - Performance testing: Verify p95 latency <2s

## Key Design Decisions

### Decision 1: Dapr HTTP API (No Direct Kafka Client)
**Rationale**: Keeps code clean and infrastructure-agnostic. Can swap Kafka for RabbitMQ by changing Dapr component YAML, no code changes.
**Trade-off**: +10-50ms latency per request (Dapr sidecar overhead), acceptable per success criteria (SC-009: <50ms).

### Decision 2: Notification Service Logs Only (No Real Push)
**Rationale**: Phase 5 focuses on event architecture. Real browser push notifications require WebSocket/SSE infrastructure, deferred to future.
**Trade-off**: Reminders shown on next page load, not real-time. Acceptable for MVP (Assumption #2 in spec).

### Decision 3: Single-Broker Kafka for Dev, 3-Broker for Prod
**Rationale**: Dev (Minikube): 1 broker saves resources. Prod (OKE): 3 brokers for high availability and replication.
**Trade-off**: Dev has no fault tolerance (broker failure = downtime), acceptable for local testing.

### Decision 4: Recurring Task Service Subscribes to task-events (Not Direct DB)
**Rationale**: Event-driven pattern: Service reacts to events, not DB polling. Scales better (horizontal scaling by adding consumers).
**Trade-off**: Eventual consistency (delay between task.completed and next occurrence created), acceptable per SC-004 (<10s).

### Decision 5: Oracle OKE Over Azure AKS / Google GKE
**Rationale**: Oracle free tier is permanent (no expiration), while Azure/GCP credits expire after 30-90 days. Better for learning/demo.
**Trade-off**: Oracle CLI less mature than Azure/GCP, acceptable for free tier value.

## Risk Mitigation

### Risk 1: Kafka Cluster Resource Exhaustion on Oracle Free Tier
**Mitigation**:
- Dev profile: 1 broker, 2GB RAM, ephemeral storage
- Prod profile: 3 brokers, 4GB RAM each (total 12GB), leaves 12GB for app services
- Monitor Kafka metrics (JMX exporter + Prometheus)
- Retention policy: 7 days (auto-delete old events)

### Risk 2: Dapr Sidecar Latency Impact on API Performance
**Mitigation**:
- Measure baseline latency before Dapr (current p95)
- Add Dapr latency monitoring (Dapr metrics)
- Target: SC-009 (<50ms overhead at p50)
- Fallback: If latency unacceptable, use direct Kafka client

### Risk 3: Backward Compatibility Breakage (Phase 1-4 Features)
**Mitigation**:
- Run full Phase 1-4 test suite after every change
- Database migration with default values (due_date=null, priority=medium)
- Feature flags for event publishing (can disable if breaks)
- Rollback plan: Revert to Phase 4 Helm chart

### Risk 4: Oracle OKE Free Tier Limits Insufficient
**Mitigation**:
- Test on Minikube first (validates architecture)
- Monitor OKE resource usage (kubectl top nodes/pods)
- Scale down replicas if needed (1 replica per service)
- Fallback: Use Azure AKS trial or keep on Minikube

### Risk 5: Notification Service Delivery Failures
**Mitigation**:
- Kafka retention (7 days) allows replay of missed reminders
- Service health checks in K8s (liveness/readiness probes)
- Dead Letter Queue pattern (if reminder fails 3 times, move to DLQ topic)
- Monitoring: Track reminder delivery success rate (target 95% per SC-003)

## Success Metrics

From spec Success Criteria (SC-001 to SC-010):

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Task creation time | <30s | Frontend timer: button click → response received |
| Search results latency | <500ms | Backend log: query start → response sent |
| Reminder delivery | 95% within 60s | Notification Service metric: scheduled time vs. actual delivery |
| Recurring task creation | <10s | Recurring Task Service metric: task.completed event → new task created |
| Kafka throughput | 1000 events/sec | Kafka metrics: messages/sec on task-events topic |
| Minikube deploy time | <5min | Helm deployment script timer |
| OKE p95 latency | <2s | Frontend → Backend → Database round-trip at 95th percentile |
| Backward compatibility | 100% tests pass | CI/CD pipeline: Phase 1-4 test suite execution |
| Dapr latency overhead | <50ms at p50 | Backend metric: request latency with/without Dapr sidecar |
| High availability | 1 replica failure tolerated | K8s experiment: Kill 1 pod, verify service continues |

## Next Steps

After this plan is approved:

1. **Execute Phase 0**: Generate `research.md` with research findings for R1-R6
2. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md`, update CLAUDE.md
3. **Run `/sp.tasks`**: Break this plan into actionable tasks with test cases
4. **Implement Part A**: Add sort dropdown, recurring task logic, reminder scheduling (without Kafka)
5. **Implement Part B**: Deploy Kafka + Dapr on Minikube, add event publishing, create microservices
6. **Implement Part C**: Deploy to Oracle OKE, verify production deployment
7. **Verify Backward Compatibility**: Run Phase 1-4 test suites, ensure 100% pass rate

**Estimated Timeline** (for reference, not a constraint):
- Phase 0-1 (Planning): 2-3 hours
- Part A (Features): 4-6 hours
- Part B (Event Architecture): 8-12 hours
- Part C (Cloud Deployment): 4-6 hours
- Total: 18-27 hours of development + testing

**Ready for**: `/sp.tasks` command to generate task breakdown
