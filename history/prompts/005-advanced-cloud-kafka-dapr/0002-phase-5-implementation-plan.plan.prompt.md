---
id: 0002
title: phase-5-implementation-plan
stage: plan
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-advanced-cloud-kafka-dapr
branch: 005-advanced-cloud-kafka-dapr
user: ps_qasim
command: /sp.plan
labels: ["phase-5", "event-driven", "kafka", "dapr", "oracle-oke", "architecture", "microservices"]
links:
  spec: specs/005-advanced-cloud-kafka-dapr/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-advanced-cloud-kafka-dapr/plan.md
tests:
  - Constitution Check: All 8 gates passed
---

## Prompt

Create the technical implementation plan for Phase 5: Advanced Cloud Deployment with Kafka and Dapr.

[User provided comprehensive context about current state and requirements - see full prompt in plan.md]

Key context from user:
- Most Phase 5 features ALREADY IMPLEMENTED (search, priority, due date, tags, filters)
- Only 3 features missing: Sort dropdown, recurring task automation, reminder notifications
- Task model already has all required fields (priority, due_date, tags, is_recurring, recurrence_pattern)
- Focus on: Missing features + Event architecture (Kafka/Dapr) + Cloud deployment (Oracle OKE)

## Response snapshot

Created comprehensive technical implementation plan with:

**Plan Structure**:
1. **Summary**: Phase 5 transforms app to cloud-native event-driven system (3 missing features + Kafka + Dapr + OKE)
2. **Technical Context**: Python 3.13+, FastAPI, Next.js 16, Kafka (Strimzi), Dapr 1.13+, Oracle OKE free tier
3. **Constitution Check**: ✅ ALL 8 GATES PASSED
   - Agent Architecture: New microservices integrate into existing multi-agent pattern
   - Skill Reusability: Extends existing Pydantic models without breaking
   - Separation of Concerns: Event layer adds new concern cleanly
   - Evolution Strategy: Phase 5 builds on Phase 4 without breaking
   - Testing, Code Quality, Error Handling, SDD: All existing standards maintained

4. **Project Structure**:
   - Current structure documented (src/, frontend/, k8s/, helm/ already exist)
   - New structure: src/services/{notification,recurring_task}/, k8s/{kafka,dapr}/, contracts/

5. **Complexity Tracking**: No violations (all gates passed)

6. **Phase 0 Research** (6 tasks):
   - R1: Dapr Pub/Sub HTTP API patterns
   - R2: Strimzi Kafka configuration for Oracle free tier
   - R3: Dapr Jobs API vs. Cron Bindings
   - R4: Oracle OKE provisioning
   - R5: Recurring task next occurrence logic
   - R6: Browser notification API integration

7. **Phase 1 Design & Contracts**:
   - Data model: Existing Task model already complete, new TaskEvent and ReminderEvent entities
   - API contracts: Modified /api/{user_id}/tasks with sort parameters, Kafka event schemas, Dapr components
   - Outputs: data-model.md, contracts/*.yaml, quickstart.md, updated CLAUDE.md

8. **Implementation Order** (Part A → B → C):
   - Part A (Features first, no Kafka): Sort dropdown, Recurring tasks, Reminders
   - Part B (Minikube): Strimzi Kafka, Dapr, Event publishing, Notification Service, Recurring Task Service
   - Part C (Cloud): Oracle OKE setup, Deploy stack, Verification

9. **Key Design Decisions** (5 major choices documented with rationale/trade-offs)
10. **Risk Mitigation** (5 risks with mitigation strategies)
11. **Success Metrics** (10 measurable targets from spec SC-001 to SC-010)

**Critical Insights**:
- Leveraged user context: Most features already exist in Task model (priority, due_date, tags, recurring fields)
- Focused plan on 3 missing pieces: Sort UI, Recurring automation, Reminder notifications
- Event architecture via Dapr HTTP API (not direct Kafka) keeps code clean and swappable
- Single-broker Kafka for dev (Minikube), 3-broker for prod (OKE) balances resources
- Oracle OKE chosen over Azure/GCP: Permanent free tier (no expiration) for learning/demo

**Architecture Highlights**:
- Dapr sidecars abstract Kafka pub/sub (POST http://localhost:3500/v1.0/publish/...)
- Notification Service subscribes to "reminders" topic, logs to stdout (no real push in Phase 5)
- Recurring Task Service subscribes to "task-events" topic, creates next occurrence on task.completed
- Oracle free tier: 4 OCPUs, 24GB RAM (1 broker Kafka + minimal replicas)

## Outcome

- ✅ Impact: Comprehensive implementation plan ready for task breakdown. Provides clear path from current state (Phase 4) to cloud-native event-driven architecture (Phase 5) while maintaining 100% backward compatibility.
- 🧪 Tests: Constitution Check passed all 8 gates. Plan includes test requirements for each phase (unit, integration, contract tests).
- 📁 Files: 1 file created (plan.md with 400+ lines covering technical context, constitution check, research tasks, design contracts, implementation order, risks, metrics)
- 🔁 Next prompts: Execute Phase 0 research (create research.md), Execute Phase 1 design (create data-model.md, contracts/, quickstart.md), Run `/sp.tasks` to break plan into actionable tasks
- 🧠 Reflection: User-provided context (existing features in Task model) saved significant planning effort. Plan correctly prioritizes Part A (features without Kafka) before Part B (event architecture) to enable incremental validation. Oracle OKE free tier selection provides permanent cloud environment without expiration pressure.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow executed successfully with all gates passed
- Graders run and results (PASS/FAIL): PASS - Constitution Check validated: no violations, all 8 principles upheld, complexity justified as zero
- Prompt variant (if applicable): Standard `/sp.plan` workflow with detailed user context about existing implementation state
- Next experiment (smallest change to try): Execute Phase 0 research to resolve 6 research tasks (R1-R6), generate research.md document
