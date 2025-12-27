---
id: 003
title: Create Agent Communication Skill
stage: general
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: developer
command: skill creation
labels: ["skill", "agents", "communication", "messages", "routing", "tracing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/agent-communication/SKILL.md
  - .claude/skills/agent-communication/references/message-protocol.md
  - .claude/skills/agent-communication/references/routing-patterns.md
  - .claude/skills/agent-communication/references/error-handling.md
  - .claude/skills/agent-communication/references/async-messaging.md
  - .claude/skills/agent-communication/references/tracing-patterns.md
tests:
  - none (skill documentation only)
---

## Prompt

Use the @.claude/skills/skill-creator skill to create a new skill called "agent-communication".

This skill should provide expert knowledge on:
- Message protocol design (AgentMessage, AgentResponse)
- Request-response patterns between agents
- Action-based routing logic
- Correlation IDs for tracing
- Error handling in multi-agent systems
- Async message passing with queues

Create the skill in .claude/skills/agent-communication/

## Response snapshot

Created a comprehensive agent communication skill at `.claude/skills/agent-communication/` with:

1. **SKILL.md** - Core skill document with:
   - Frontmatter with name and description
   - AgentMessage and AgentResponse core types
   - Quick routing pattern example
   - Request-response flow diagram
   - Links to all reference files

2. **references/message-protocol.md** - Complete message design:
   - AgentMessage with validation, immutability, correlation
   - AgentResponse with factory methods and invariants
   - Action naming conventions (domain_operation)
   - Payload schemas with Pydantic
   - Serialization patterns

3. **references/routing-patterns.md** - Routing strategies:
   - Prefix routing (recommended for Phase I)
   - Registry pattern with AgentInfo metadata
   - Content-based routing
   - Declarative routing configuration
   - Middleware pattern for pre/post processing

4. **references/error-handling.md** - Multi-agent error handling:
   - Exception hierarchy (AgentError → ValidationError, NotFoundError, etc.)
   - Catch at boundary pattern
   - Error propagation through orchestrator
   - Retry with exponential backoff
   - Circuit breaker pattern

5. **references/async-messaging.md** - Async patterns:
   - BaseAsyncAgent interface
   - Priority-based async queue
   - Request-response with queues
   - Pub/sub event bus pattern
   - Graceful shutdown

6. **references/tracing-patterns.md** - Observability:
   - Correlation ID generation and propagation
   - Structured logging with structlog
   - Distributed tracing with spans
   - Request trace aggregation
   - Metrics collection

## Outcome

- Impact: Created reusable skill for implementing multi-agent communication patterns
- Tests: N/A (documentation skill)
- Files: 6 files created in `.claude/skills/agent-communication/`
- Next prompts: Run `/sp.tasks` to generate implementation tasks; use all three skills during implementation
- Reflection: Skill directly supports the Multi-Agent Architecture System spec requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add references for specific backend integrations (Redis queues, etc.)
