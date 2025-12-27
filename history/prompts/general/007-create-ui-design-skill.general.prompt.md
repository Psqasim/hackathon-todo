---
id: 007
title: Create UI Design Skill
stage: general
date: 2025-12-27
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-agent-architecture
user: human
command: skill-creator
labels: ["skill", "ui-design", "accessibility", "tailwind", "rich"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/ui-design-skill/SKILL.md
  - .claude/skills/ui-design-skill/references/design-principles.md
  - .claude/skills/ui-design-skill/references/rich-console-ui.md
  - .claude/skills/ui-design-skill/references/tailwind-patterns.md
  - .claude/skills/ui-design-skill/references/responsive-design.md
  - .claude/skills/ui-design-skill/references/accessibility-wcag.md
  - .claude/skills/ui-design-skill/references/design-systems.md
tests:
  - none
---

## Prompt

Use the @.claude/skills/skill-creator skill to create a new skill called "ui-design-skill".

This skill should provide expert knowledge on:
- User-centered design principles
- Console UI with Rich library (Phase I)
- Web UI with Tailwind CSS (Phase II)
- Responsive design patterns
- Accessibility (WCAG guidelines)
- Design systems and consistency

Create the skill in .claude/skills/ui-design-skill/

## Response snapshot

Created comprehensive `ui-design-skill` at `.claude/skills/ui-design-skill/` with progressive disclosure design:

**SKILL.md** - Core quick reference with:
- Design decision framework
- Technology selection table (Rich vs Tailwind)
- Nielsen's 10 usability heuristics
- Visual hierarchy (typography, color, spacing)
- Console UI quick start (Rich library)
- Web UI quick start (Tailwind CSS)
- Accessibility checklist
- Links to all reference files

**Reference Files:**
1. `design-principles.md` - User-centered design, Gestalt principles, feedback design, information architecture
2. `rich-console-ui.md` - Tables, panels, progress bars, prompts, layouts, live display, todo app patterns
3. `tailwind-patterns.md` - Layout patterns, components (cards, buttons, forms), feedback, dark mode
4. `responsive-design.md` - Mobile-first approach, breakpoints, layout patterns, touch considerations
5. `accessibility-wcag.md` - WCAG principles (POUR), color contrast, keyboard nav, ARIA, testing
6. `design-systems.md` - Design tokens, component library, documentation, maintenance

## Outcome

- Impact: Created UI/UX design skill for both Phase I (Console) and Phase II (Web) development
- Tests: none (documentation skill)
- Files: 7 files created (SKILL.md + 6 references)
- Next prompts: Run `/sp.tasks` to generate Phase I implementation tasks
- Reflection: Skill provides comprehensive coverage from console to web, with accessibility built-in

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A (skill creation)
- Prompt variant (if applicable): standard skill-creator pattern
- Next experiment: Consider adding Rich-to-web migration patterns reference
