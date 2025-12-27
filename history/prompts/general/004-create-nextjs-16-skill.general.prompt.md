---
id: 004
title: Create Next.js 16 Skill
stage: general
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: developer
command: skill creation
labels: ["skill", "nextjs", "react", "app-router", "server-actions", "better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/nextjs-16-skill/SKILL.md
  - .claude/skills/nextjs-16-skill/references/app-router.md
  - .claude/skills/nextjs-16-skill/references/server-client-components.md
  - .claude/skills/nextjs-16-skill/references/server-actions.md
  - .claude/skills/nextjs-16-skill/references/better-auth.md
  - .claude/skills/nextjs-16-skill/references/api-routes.md
  - .claude/skills/nextjs-16-skill/references/react-19-patterns.md
tests:
  - none (skill documentation only)
---

## Prompt

Use the @.claude/skills/skill-creator skill to create a new skill called "nextjs-16-skill".

This skill should provide expert knowledge on:
- Next.js 16 App Router architecture
- Server Components vs Client Components
- Server Actions for mutations
- Better Auth integration patterns
- API route handlers
- React 19 patterns (use client, useFormStatus)

Create the skill in .claude/skills/nextjs-16-skill/

## Response snapshot

Created a comprehensive Next.js 16 skill at `.claude/skills/nextjs-16-skill/` with:

1. **SKILL.md** - Core skill document with:
   - Component decision tree (Server vs Client)
   - Server Component example with async data fetching
   - Client Component example with state
   - Server Action quick example
   - Project structure guide
   - Links to all reference files

2. **references/app-router.md** - App Router architecture:
   - File-based routing and special files
   - Layouts (root, nested, protected)
   - Dynamic routes and catch-all
   - Loading states and Suspense
   - Error handling and not-found
   - Navigation patterns
   - Parallel and intercepting routes
   - Metadata configuration

3. **references/server-client-components.md** - Component patterns:
   - When to use Server vs Client
   - Data fetching and caching strategies
   - Composition patterns
   - Context providers setup
   - Anti-patterns to avoid
   - Best practices

4. **references/server-actions.md** - Mutation patterns:
   - Basic Server Actions
   - Validation with Zod
   - useActionState for form state
   - Optimistic updates with useOptimistic
   - Revalidation strategies
   - Authentication in actions

5. **references/better-auth.md** - Authentication:
   - Installation and setup
   - Sign in/up/out components
   - Session management (server/client)
   - Protected routes and layouts
   - OAuth providers (Google, GitHub)
   - Middleware protection

6. **references/api-routes.md** - API handlers:
   - GET, POST, PUT, DELETE handlers
   - Dynamic route parameters
   - Query params, headers, cookies
   - Response types and streaming
   - Error handling with Zod
   - CORS configuration

7. **references/react-19-patterns.md** - React 19 features:
   - useFormStatus for pending state
   - useActionState for form handling
   - useOptimistic for instant updates
   - useTransition for non-blocking UI
   - Complete form patterns

## Outcome

- Impact: Created reusable skill for Phase II web development with Next.js 16
- Tests: N/A (documentation skill)
- Files: 7 files created in `.claude/skills/nextjs-16-skill/`
- Next prompts: Run `/sp.tasks` for Phase I, then use this skill for Phase II web app
- Reflection: Skill covers full Next.js 16 App Router stack for hackathon Phase II

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add Tailwind CSS patterns reference for styling
