---
id: 006
title: Create GitHub Actions Skill
stage: general
date: 2025-12-27
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: human
command: skill-creator
labels: ["skill", "github-actions", "ci-cd", "devops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/github-actions-skill/SKILL.md
  - .claude/skills/github-actions-skill/references/workflow-syntax.md
  - .claude/skills/github-actions-skill/references/ci-pipelines.md
  - .claude/skills/github-actions-skill/references/matrix-strategies.md
  - .claude/skills/github-actions-skill/references/secrets-env.md
  - .claude/skills/github-actions-skill/references/docker-workflows.md
  - .claude/skills/github-actions-skill/references/deployment-automation.md
tests:
  - none
---

## Prompt

Use the @.claude/skills/skill-creator skill to create a new skill called 'github-actions-skill'. This skill should provide expert guidance on GitHub Actions CI/CD workflows.

Key topics to cover:
1. **Workflow syntax** - triggers (on: push, pull_request, workflow_dispatch), jobs, steps, actions
2. **CI pipelines** - Python CI with pytest, Node.js CI, linting, type checking
3. **Matrix strategies** - Testing across Python versions, OS platforms
4. **Secrets and env vars** - Using secrets, environment variables, GITHUB_TOKEN
5. **Docker workflows** - Building and pushing images, multi-platform builds
6. **Deployment automation** - Deploying to Vercel, AWS, Kubernetes

## Response snapshot

Created comprehensive `github-actions-skill` at `.claude/skills/github-actions-skill/` with progressive disclosure design:

**SKILL.md** - Core quick reference with:
- Quick start workflow example
- Common triggers overview
- Job dependencies pattern
- Matrix strategy basics
- Links to all reference files

**Reference Files:**
1. `workflow-syntax.md` - Complete YAML syntax (triggers, jobs, steps, conditionals, expressions)
2. `ci-pipelines.md` - Python CI, Node.js CI, FastAPI CI, Next.js CI, monorepo patterns
3. `matrix-strategies.md` - Multi-version testing, include/exclude, dynamic matrices
4. `secrets-env.md` - Repository/environment secrets, GITHUB_TOKEN permissions, secure patterns
5. `docker-workflows.md` - Build/push, multi-registry, multi-platform, caching, security scanning
6. `deployment-automation.md` - Vercel, AWS S3/ECS, Kubernetes, SSH, blue-green, rollbacks

## Outcome

- Impact: Created production-ready CI/CD skill for Phases IV-V (Kubernetes, Cloud deployment)
- Tests: none (documentation skill)
- Files: 7 files created (SKILL.md + 6 references)
- Next prompts: Run `/sp.tasks` to generate Phase I implementation tasks
- Reflection: Skill completes the development toolchain (Python, testing, agents, Next.js, FastAPI, CI/CD)

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A (skill creation)
- Prompt variant (if applicable): standard skill-creator pattern
- Next experiment: Consider adding reusable workflow patterns reference
