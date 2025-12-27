---
id: 002
title: Create Testing Patterns Skill
stage: general
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: developer
command: skill creation
labels: ["skill", "testing", "pytest", "tdd", "mocking"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/testing-patterns/SKILL.md
  - .claude/skills/testing-patterns/references/pytest-setup.md
  - .claude/skills/testing-patterns/references/mocking-patterns.md
  - .claude/skills/testing-patterns/references/async-testing.md
  - .claude/skills/testing-patterns/references/tdd-workflow.md
  - .claude/skills/testing-patterns/references/integration-testing.md
tests:
  - none (skill documentation only)
---

## Prompt

Use the @.claude/skills/skill-creator skill to create a new skill called "testing-patterns".

This skill should provide expert knowledge on:
- Pytest setup and configuration
- Unit testing with mocks and fixtures
- Integration testing workflows
- Async testing with pytest-asyncio
- Test coverage strategies (80%+ target)
- TDD (Test-Driven Development) approach

Create the skill in .claude/skills/testing-patterns/

## Response snapshot

Created a comprehensive testing patterns skill at `.claude/skills/testing-patterns/` with:

1. **SKILL.md** - Core skill document with:
   - Frontmatter with name and comprehensive description
   - Basic test structure examples
   - Fixture patterns for dependencies
   - Test organization and directory structure
   - Coverage target guidance (80%+)
   - Links to all reference files

2. **references/pytest-setup.md** - Detailed pytest configuration:
   - pyproject.toml configuration
   - Built-in and custom markers
   - Fixture scopes (function, class, module, session)
   - Fixture factories and autouse
   - conftest.py hierarchy
   - CLI options reference

3. **references/mocking-patterns.md** - Mocking strategies:
   - Test doubles overview (stub, mock, fake, spy)
   - unittest.mock basics (MagicMock, return values, assertions)
   - Patching (decorator, context manager, patch.object)
   - pytest-mock (recommended approach)
   - Dependency injection testing
   - Fake implementations

4. **references/async-testing.md** - Async testing with pytest-asyncio:
   - Setup and configuration
   - Basic async tests (auto mode)
   - Async fixtures with cleanup
   - Testing concurrent operations
   - AsyncMock patterns
   - Common pitfalls

5. **references/tdd-workflow.md** - TDD approach:
   - Red-Green-Refactor cycle
   - Phase-by-phase guide
   - Complete TDD example
   - Test naming conventions
   - Arrange-Act-Assert structure
   - Best practices and pitfalls

6. **references/integration-testing.md** - Integration testing:
   - Test pyramid overview
   - Workflow testing patterns
   - Contract testing for protocols
   - Component integration
   - Test data builders
   - Markers for test selection

## Outcome

- Impact: Created reusable skill for enforcing testing best practices during development
- Tests: N/A (documentation skill)
- Files: 6 files created in `.claude/skills/testing-patterns/`
- Next prompts: Run `/sp.tasks` to generate implementation tasks, then use both python-best-practices and testing-patterns skills during implementation
- Reflection: Progressive disclosure pattern applied - SKILL.md provides quick patterns, reference files provide deep dives

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add coverage-strategies.md reference with detailed coverage configuration
