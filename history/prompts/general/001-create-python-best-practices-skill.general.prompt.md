---
id: 001
title: Create Python Best Practices Skill
stage: general
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: developer
command: skill creation
labels: ["skill", "python", "best-practices", "code-quality"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/python-best-practices/SKILL.md
  - .claude/skills/python-best-practices/references/async-patterns.md
  - .claude/skills/python-best-practices/references/pydantic-patterns.md
  - .claude/skills/python-best-practices/references/solid-patterns.md
  - .claude/skills/python-best-practices/references/error-handling.md
tests:
  - none (skill documentation only)
---

## Prompt

Use the @.claude/skills/skill-creator skill to help me create a new skill called "python-best-practices"

## Response snapshot

Created a comprehensive Python best practices skill at `.claude/skills/python-best-practices/` with:

1. **SKILL.md** - Core skill document with frontmatter and guidance on:
   - Type hints (Python 3.12+ syntax)
   - Async patterns overview
   - Clean code principles (DRY)
   - Dependency injection patterns
   - Quick reference for error handling

2. **references/async-patterns.md** - Deep dive into:
   - async/await fundamentals
   - Concurrent execution (gather, TaskGroup)
   - Async context managers
   - Common pitfalls and solutions

3. **references/pydantic-patterns.md** - Comprehensive coverage of:
   - Model basics and configuration
   - Field and model validators
   - Field constraints
   - Serialization/deserialization
   - Settings management

4. **references/solid-patterns.md** - All SOLID principles with Python examples:
   - Single Responsibility (SRP)
   - Open/Closed (OCP)
   - Liskov Substitution (LSP)
   - Interface Segregation (ISP)
   - Dependency Inversion (DIP)

5. **references/error-handling.md** - Error handling patterns:
   - Custom exception hierarchy
   - When to catch vs propagate
   - Result pattern alternative
   - Structured logging with structlog

## Outcome

- Impact: Created reusable skill for enforcing Python code quality during development
- Tests: N/A (documentation skill)
- Files: 5 files created in `.claude/skills/python-best-practices/`
- Next prompts: Run `/sp.tasks` to generate implementation tasks from the plan
- Reflection: Used skill-creator skill as reference for proper structure with progressive disclosure

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add testing-patterns.md reference for pytest guidance
