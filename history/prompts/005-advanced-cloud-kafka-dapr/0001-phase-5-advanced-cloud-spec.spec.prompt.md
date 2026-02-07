---
id: 0001
title: phase-5-advanced-cloud-spec
stage: spec
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-advanced-cloud-kafka-dapr
branch: 005-advanced-cloud-kafka-dapr
user: ps_qasim
command: /sp.specify
labels: ["phase-5", "cloud-deployment", "kafka", "dapr", "oracle-oke", "advanced-features", "event-driven"]
links:
  spec: specs/005-advanced-cloud-kafka-dapr/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-advanced-cloud-kafka-dapr/spec.md
  - specs/005-advanced-cloud-kafka-dapr/checklists/requirements.md
tests:
  - Specification quality validation (passed all checks)
---

## Prompt

Phase 5: Advanced Cloud Deployment with Kafka, Dapr, and Oracle Cloud

## Project Context
This is Phase 5 of TaskFlow hackathon project. Phases 1-4 are complete (console app, web app, AI chatbot, local K8s). Now we add advanced features and deploy to cloud with event-driven architecture. also read @Hackathon II - Todo Spec-Driven Development.md in phase 5 specs

## What We're Building

### Part A: Advanced Features (Intermediate + Advanced Level)

1. **Recurring Tasks**
   - Users can set tasks to repeat: daily, weekly, monthly
   - When recurring task marked complete, auto-create next occurrence
   - Store recurrence_pattern field (none, daily, weekly, monthly)

2. **Due Dates & Time Reminders**
   - Add due_date field (datetime) to tasks
   - Show overdue tasks highlighted in red
   - Browser notification 1 hour before due (via Kafka events)

3. **Priority Levels**
   - Add priority field: low, medium, high, urgent
   - Color coding: low=gray, medium=blue, high=orange, urgent=red
   - Sort by priority

4. **Tags/Categories**
   - Add tags field (array of strings, max 10)
   - Filter tasks by tag
   - Tag input with autocomplete from existing tags

5. **Search**
   - Real-time search across title and description
   - Debounced input (300ms)

6. **Filter & Sort**
   - Filter by: status (all/pending/completed), priority, due date range, tags
   - Sort by: due date, priority, created date, title (A-Z)

### Part B: Event-Driven Architecture on Minikube

1. **Kafka Integration (via Strimzi)**
   - Install Strimzi operator on Minikube
   - Create Kafka cluster (1 broker for dev)
   - Topics:
     - task-events: All task CRUD operations
     - reminders: Scheduled reminder triggers
     - task-updates: Real-time sync

2. **Dapr Integration**
   - Install Dapr on Minikube
   - Components:
     - pubsub.kafka: Kafka abstraction
     - state.postgresql: Conversation state (existing Neon DB)
     - bindings.cron: Check reminders every 5 minutes
     - secretstores.kubernetes: API keys

3. **New Microservices**
   - Notification Service: Subscribes to "reminders" topic, logs notifications
   - Recurring Task Service: Subscribes to "task-events", creates next occurrence when recurring task completed

### Part C: Cloud Deployment (Oracle OKE)

1. **Oracle Cloud Setup**
   - Create free tier OKE cluster (4 OCPUs, 24GB RAM - always free!)
   - Configure kubectl to connect

2. **Deploy Stack**
   - Deploy Strimzi Kafka
   - Deploy Dapr
   - Deploy all TaskFlow services via Helm
   - Connect to existing Neon PostgreSQL (external)

3. **Monitoring**
   - Basic health endpoints
   - Kubernetes dashboard

## User Stories

US-5.1: As a user, I can set a task to repeat daily/weekly/monthly so I don't forget recurring responsibilities
US-5.2: As a user, I can set due dates on tasks so I know when things are due
US-5.3: As a user, I can set priority levels so I focus on important tasks first
US-5.4: As a user, I can add tags to organize my tasks by category
US-5.5: As a user, I can search my tasks to quickly find what I need
US-5.6: As a user, I can filter and sort tasks to see them organized my way
US-5.7: As a user, my completed recurring tasks automatically create the next occurrence
US-5.8: As a developer, task events flow through Kafka for scalable event processing
US-5.9: As a developer, Dapr abstracts infrastructure so code stays clean
US-5.10: As a user, the app works on cloud (Oracle) just like locally

## Technology Stack
- Existing: FastAPI, Next.js 16, Neon PostgreSQL, Docker, Minikube, Helm
- New: Apache Kafka (Strimzi), Dapr 1.13+, Oracle OKE

## Acceptance Criteria
- [ ] All Phase 1-4 features still work
- [ ] Tasks can have due dates, priorities, tags, recurrence
- [ ] Search, filter, sort work in UI
- [ ] Kafka topics receive events when tasks change
- [ ] Dapr sidecars run alongside backend
- [ ] Notification service logs when reminder due
- [ ] Recurring task service creates next occurrence
- [ ] Full stack deployed on Oracle OKE
- [ ] Demo video shows cloud deployment working

## Reference Skills
Use these skills I created for implementation guidance:
- .claude/skills/kafka-event-driven (Kafka patterns)
- .claude/skills/dapr-microservices (Dapr integration)
- .claude/skills/multi-cloud-kubernetes-operator (Oracle OKE)

## Constraints
- No manual coding - all via Claude Code
- Follow Spec-Driven Development
- Use existing project structure patterns from Phase 1-4
- Keep backward compatibility with existing features

## Response snapshot

Created comprehensive Phase 5 specification following spec-driven development workflow:

**Branch Created**: `005-advanced-cloud-kafka-dapr`

**Specification Structure**:
1. **10 Prioritized User Stories** (P1-P3):
   - P1: Due Dates & Reminders, Kafka Architecture, Backward Compatibility
   - P2: Recurring Tasks, Priorities, Dapr Integration, Minikube Deployment
   - P3: Tags, Search/Filter, Oracle OKE Deployment

2. **32 Functional Requirements** across 4 categories:
   - Advanced Task Features (FR-001 to FR-009)
   - Search and Filter (FR-010 to FR-016)
   - Event-Driven Architecture (FR-017 to FR-023)
   - Dapr Integration & Deployment (FR-024 to FR-032)

3. **10 Measurable Success Criteria**:
   - User performance: Task creation <30s, Search <500ms
   - System performance: 95% reminders delivered, 1000 events/sec
   - Infrastructure: Minikube deploy <5min, p95 latency <2s, 100% backward compat

4. **12 Documented Assumptions** covering timezone handling, reminder delivery, tag storage, Kafka retention, search scope, deployment limits, backward compatible defaults

5. **39 Acceptance Scenarios** (3-4 per user story) using Given/When/Then format

6. **8 Edge Cases** for error scenarios and boundary conditions

**Quality Validation**: ✅ PASSED all checklist items
- No implementation details leaked
- User value focused
- Technology-agnostic success criteria
- All requirements testable and unambiguous
- Zero [NEEDS CLARIFICATION] markers (resolved via assumptions)

**Key Design Decisions**:
- Event-driven architecture with Kafka enables horizontal scaling
- Dapr abstracts infrastructure for portability
- Oracle OKE free tier for cost-effective cloud deployment
- Backward compatibility with Phase 1-4 as P1 requirement
- Browser notifications when tab open (no email/SMS in Phase 5)

## Outcome

- ✅ Impact: Feature branch created with complete, validated specification ready for planning phase. Enables systematic implementation of advanced features and cloud-native event-driven architecture.
- 🧪 Tests: Specification quality validation passed all checks (content quality, requirement completeness, feature readiness)
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: `/sp.plan` to generate technical architecture and implementation strategy, or `/sp.clarify` if user needs to refine requirements
- 🧠 Reflection: Comprehensive spec balances user-facing features (due dates, priorities, tags, search) with infrastructure requirements (Kafka, Dapr, cloud deployment). Prioritization ensures P1 items (backward compat, due dates, Kafka) are foundational. 12 assumptions resolved ambiguities without blocking, enabling immediate planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification workflow executed successfully with zero clarification markers needed
- Graders run and results (PASS/FAIL): PASS - Quality checklist validated: no implementation details, measurable outcomes, technology-agnostic success criteria, testable requirements
- Prompt variant (if applicable): Standard `/sp.specify` workflow with comprehensive user input from Hackathon II documentation
- Next experiment (smallest change to try): Proceed to `/sp.plan` to design technical architecture for event-driven system with Kafka/Dapr integration
