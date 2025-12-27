---
id: 008
title: Add Scripts to Skills
stage: general
date: 2025-12-27
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: ps_qasim
command: none
labels: ["skills", "scripts", "automation", "documentation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/testing-patterns/scripts/run_tests.py
  - .claude/skills/testing-patterns/scripts/generate_test.py
  - .claude/skills/fastapi-skill/scripts/create_app.py
  - .claude/skills/fastapi-skill/scripts/generate_router.py
  - .claude/skills/github-actions-skill/scripts/generate_workflow.py
  - .claude/skills/github-actions-skill/scripts/validate_workflow.py
  - .claude/SKILLS_AND_AGENTS_GUIDE.md
tests:
  - N/A (script utilities, manual testing)
---

## Prompt

hey in thaat all skill u @.claude/skills/ not make scripts folder in that like in @.claude/skills/skill-creator/ in that all skills Also use mcp context7 for docs how to make skills "https://github.com/anthropics/skills/tree/main/skills/mcp-builder/scripts" there is also for u help that make all skills in script if necc ,if not then not make also make an summary tell how to use these skills and also how to use in @.claude/agents/ in that

## Response snapshot

Analyzed all skills in `.claude/skills/` to determine which need scripts folders. Based on Anthropic skills documentation and the skill-creator example:

**Skills with new scripts added:**
1. `testing-patterns/scripts/`
   - `run_tests.py` - Run pytest with coverage, unit/integration options
   - `generate_test.py` - Generate test templates (sync/async)

2. `fastapi-skill/scripts/`
   - `create_app.py` - Generate FastAPI app structure with optional DB
   - `generate_router.py` - Generate CRUD routers with schemas

3. `github-actions-skill/scripts/`
   - `generate_workflow.py` - Generate CI, deploy, docker, release workflows
   - `validate_workflow.py` - Validate workflow YAML syntax and structure

**Skills without scripts (guidance-only):**
- `python-best-practices` - Coding patterns/principles
- `agent-communication` - Protocol patterns
- `nextjs-16-skill` - Framework patterns
- `ui-design-skill` - Design patterns

Created comprehensive guide: `.claude/SKILLS_AND_AGENTS_GUIDE.md`

## Outcome

- ✅ Impact: Added automation scripts to 3 skills, created usage guide for all 8 skills and 8 agents
- 🧪 Tests: Scripts are utility tools - tested via usage examples in documentation
- 📁 Files: 7 new files created (6 scripts + 1 guide)
- 🔁 Next prompts: Test scripts with real project, add more agent documentation
- 🧠 Reflection: Not all skills need scripts - only those with repetitive automation tasks benefit from scripts

## Evaluation notes (flywheel)

- Failure modes observed: None - successfully analyzed skill patterns and created appropriate scripts
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add integration tests for the new scripts
