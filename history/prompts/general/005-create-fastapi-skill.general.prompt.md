---
id: 005
title: Create FastAPI Skill
stage: general
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: developer
command: skill creation
labels: ["skill", "fastapi", "python", "api", "sqlmodel", "pydantic"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/fastapi-skill/SKILL.md
  - .claude/skills/fastapi-skill/references/app-structure.md
  - .claude/skills/fastapi-skill/references/pydantic-models.md
  - .claude/skills/fastapi-skill/references/dependency-injection.md
  - .claude/skills/fastapi-skill/references/cors-config.md
  - .claude/skills/fastapi-skill/references/async-handlers.md
  - .claude/skills/fastapi-skill/references/sqlmodel-patterns.md
tests:
  - none (skill documentation only)
---

## Prompt

Use the @.claude/skills/skill-creator skill to create a new skill called "fastapi-skill".

This skill should provide expert knowledge on:
- FastAPI app structure and routing
- Pydantic models for request/response validation
- Dependency injection with Depends()
- CORS configuration for frontend integration
- Async route handlers
- SQLModel for database operations

Create the skill in .claude/skills/fastapi-skill/

## Response snapshot

Created a comprehensive FastAPI skill at `.claude/skills/fastapi-skill/` with:

1. **SKILL.md** - Core skill document with:
   - Quick start minimal app
   - Request/response model example
   - Dependency injection example
   - CORS setup for Next.js
   - Project structure guide
   - Links to all reference files

2. **references/app-structure.md** - App organization:
   - Application factory pattern
   - pydantic-settings configuration
   - Router organization and path operations
   - Response handling and status codes
   - Custom middleware
   - Exception handlers
   - API versioning
   - OpenAPI documentation

3. **references/pydantic-models.md** - Data validation:
   - Request models (create, update, partial)
   - Field validators and model validators
   - Response models with computed fields
   - Pagination patterns
   - Error response models
   - Enums and discriminated unions
   - Serialization and aliases

4. **references/dependency-injection.md** - Depends() patterns:
   - Simple and class-based dependencies
   - Database session dependency
   - Authentication (get_current_user)
   - Service layer dependencies
   - Scoped dependencies (request vs singleton)
   - Dependency overrides for testing
   - Sub-dependencies and chaining

5. **references/cors-config.md** - Frontend integration:
   - Development vs production config
   - Environment-based settings
   - All configuration options explained
   - Next.js fetch integration
   - Debugging CORS issues
   - Security considerations

6. **references/async-handlers.md** - Async patterns:
   - When to use async vs sync
   - Async SQLAlchemy operations
   - httpx for HTTP requests
   - Parallel requests with gather
   - File operations with aiofiles
   - Background tasks
   - Timeouts and concurrency control

7. **references/sqlmodel-patterns.md** - Database operations:
   - Setup and configuration
   - Model definitions with relationships
   - Separate request/response schemas
   - CRUD operations
   - Advanced queries (filter, sort, paginate)
   - Service layer pattern
   - Transactions and migrations

## Outcome

- Impact: Created reusable skill for Phase II backend API development
- Tests: N/A (documentation skill)
- Files: 7 files created in `.claude/skills/fastapi-skill/`
- Next prompts: Run `/sp.tasks` for Phase I, use this skill for Phase II backend
- Reflection: Skill complements nextjs-16-skill for full-stack Phase II development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add authentication patterns reference for JWT/OAuth
