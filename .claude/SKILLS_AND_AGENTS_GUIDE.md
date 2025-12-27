# Skills and Agents Guide

This guide explains how to use the skills and agents in this project for the Todo application development.

---

## Overview

| Type | Purpose | Location |
|------|---------|----------|
| **Skills** | Provide specialized knowledge and reusable scripts | `.claude/skills/` |
| **Agents** | Handle specific domains in the multi-agent system | `.claude/agents/` |

---

## Skills

Skills are modular packages that extend Claude's capabilities. They contain:
- **SKILL.md** - Main instructions and guidance
- **references/** - Detailed documentation loaded on demand
- **scripts/** - Executable automation scripts

### How to Invoke Skills

Skills are invoked automatically based on context, or explicitly:

```
/skill-name           # Invoke a skill by name
/python-best-practices # Example: Get Python coding guidance
```

---

### Available Skills

#### 1. `skill-creator`
**Purpose**: Create and package new skills

**Scripts**:
| Script | Usage | Description |
|--------|-------|-------------|
| `init_skill.py` | `python scripts/init_skill.py my-skill --path .claude/skills/` | Create new skill from template |
| `package_skill.py` | `python scripts/package_skill.py path/to/skill` | Package skill for distribution |
| `quick_validate.py` | `python scripts/quick_validate.py path/to/skill` | Validate skill structure |

---

#### 2. `python-best-practices`
**Purpose**: Python 3.12+ coding patterns and clean code principles

**When to use**: Writing/reviewing Python code for type hints, async patterns, Pydantic models, SOLID principles

**No scripts needed** - This is a guidance-only skill

**Key Topics**:
- Type hints and generics
- Async/await patterns
- Pydantic v2 models
- Dependency injection
- Error handling

---

#### 3. `testing-patterns`
**Purpose**: Python testing with pytest

**Scripts**:
| Script | Usage | Description |
|--------|-------|-------------|
| `run_tests.py` | `python scripts/run_tests.py --unit --verbose` | Run tests with coverage |
| `generate_test.py` | `python scripts/generate_test.py TaskManager --path tests/` | Generate test templates |

**Examples**:
```bash
# Run all tests with coverage
python .claude/skills/testing-patterns/scripts/run_tests.py

# Run only unit tests
python .claude/skills/testing-patterns/scripts/run_tests.py --unit

# Generate async test template
python .claude/skills/testing-patterns/scripts/generate_test.py StorageAgent --path tests/unit/ --async
```

---

#### 4. `fastapi-skill`
**Purpose**: FastAPI backend development

**Scripts**:
| Script | Usage | Description |
|--------|-------|-------------|
| `create_app.py` | `python scripts/create_app.py todo_api --path src/` | Generate FastAPI app structure |
| `generate_router.py` | `python scripts/generate_router.py tasks --path src/routers/` | Generate CRUD router |

**Examples**:
```bash
# Create new FastAPI app with database
python .claude/skills/fastapi-skill/scripts/create_app.py todo_api --path src/ --with-db

# Generate tasks router with schemas
python .claude/skills/fastapi-skill/scripts/generate_router.py tasks --path src/routers/ --with-schema
```

---

#### 5. `github-actions-skill`
**Purpose**: CI/CD pipelines with GitHub Actions

**Scripts**:
| Script | Usage | Description |
|--------|-------|-------------|
| `generate_workflow.py` | `python scripts/generate_workflow.py ci --path .github/workflows/` | Generate workflow files |
| `validate_workflow.py` | `python scripts/validate_workflow.py --all` | Validate workflow YAML |

**Workflow Types**:
- `ci` - Continuous Integration (lint, test, coverage)
- `deploy` - Deployment with environment gates
- `docker` - Docker build and push
- `release` - PyPI publishing

**Examples**:
```bash
# Generate CI workflow
python .claude/skills/github-actions-skill/scripts/generate_workflow.py ci --path .github/workflows/

# Validate all workflows
python .claude/skills/github-actions-skill/scripts/validate_workflow.py --all
```

---

#### 6. `nextjs-16-skill`
**Purpose**: Next.js 16 App Router development

**When to use**: Building Next.js pages, Server/Client Components, Server Actions, Better Auth

**No scripts needed** - Guidance for modern Next.js patterns

---

#### 7. `agent-communication`
**Purpose**: Multi-agent communication patterns

**When to use**: Designing message protocols, routing logic, error handling between agents

**No scripts needed** - Architectural patterns and protocols

---

#### 8. `ui-design-skill`
**Purpose**: UI/UX design for console and web

**When to use**: Rich library console UIs, Tailwind CSS, accessibility, design systems

**No scripts needed** - Design guidance and patterns

---

## Agents

Agents are specialized workers in the multi-agent Todo application. Each agent handles a specific domain.

### How to Invoke Agents

Agents are invoked via the Task tool with a specific `subagent_type`:

```
Task tool with subagent_type="orchestrator-agent"
```

---

### Available Agents

#### 1. `orchestrator-agent`
**Role**: Central coordinator that routes messages between subagents

**Responsibilities**:
- Agent registry management
- Message routing based on action prefixes
- Lifecycle management (startup/shutdown)
- Error handling and recovery

**When to use**: Designing the main coordinator, implementing routing logic, debugging message routing

---

#### 2. `task-manager-agent`
**Role**: Business logic for task operations

**Actions Handled**:
| Action | Description |
|--------|-------------|
| `task_add` | Create new task with validation |
| `task_delete` | Remove task by ID |
| `task_update` | Modify existing task |
| `task_list` | List tasks with optional filters |
| `task_complete` | Toggle completion status |

**When to use**: Implementing CRUD operations, validation logic, business rules

---

#### 3. `storage-handler-agent`
**Role**: Data persistence layer

**Actions Handled**:
| Action | Description |
|--------|-------------|
| `storage_save` | Save task (auto-generates ID) |
| `storage_get` | Retrieve task by ID |
| `storage_delete` | Remove task |
| `storage_list` | List all tasks |
| `storage_query` | Query with filters |

**When to use**: Implementing storage backends, handling data integrity, planning migrations

---

#### 4. `ui-controller-agent`
**Role**: Console UI with Rich library

**Actions Handled**:
| Action | Description |
|--------|-------------|
| `ui_show_menu` | Display main menu |
| `ui_show_tasks` | Show task list table |
| `ui_show_message` | Display info/error messages |
| `ui_confirm` | Yes/no confirmation prompt |
| `ui_get_input` | Text input prompt |
| `ui_get_choice` | Menu selection |

**When to use**: Building console displays, implementing user prompts, formatting output

---

#### 5. `github-workflow-agent`
**Role**: GitHub Actions CI/CD specialist

**When to use**: Setting up pipelines, automating tests, configuring deployments, managing secrets

---

#### 6. `nextjs-expert-agent`
**Role**: Next.js 16 development specialist

**When to use**: App Router patterns, Server/Client Components, Server Actions, Better Auth

---

#### 7. `ui-ux-design-agent`
**Role**: Interface design specialist

**When to use**: Designing interfaces, improving UX, accessibility, design systems

---

#### 8. `project-structure-agent`
**Role**: Codebase organization specialist

**When to use**: Setting up projects, refactoring folder structure, planning features

---

## Multi-Agent Architecture

```
                    ┌─────────────────┐
                    │  Orchestrator   │
                    │     Agent       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Task Manager   │ │    Storage      │ │  UI Controller  │
│     Agent       │ │    Agent        │ │     Agent       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Message Flow

1. User request → Orchestrator
2. Orchestrator routes by action prefix:
   - `task_*` → Task Manager Agent
   - `storage_*` → Storage Agent
   - `ui_*` → UI Controller Agent
3. Agent processes and returns response
4. Orchestrator returns result to user

---

## Quick Reference

### Running Skill Scripts

All skill scripts are located in `.claude/skills/<skill-name>/scripts/`:

```bash
# Testing
python .claude/skills/testing-patterns/scripts/run_tests.py

# FastAPI
python .claude/skills/fastapi-skill/scripts/create_app.py my_app --path src/

# GitHub Actions
python .claude/skills/github-actions-skill/scripts/generate_workflow.py ci

# Skill Creation
python .claude/skills/skill-creator/scripts/init_skill.py my-skill --path .claude/skills/
```

### Skills Without Scripts

These skills provide guidance only (no automation needed):
- `python-best-practices` - Coding patterns
- `agent-communication` - Protocol patterns
- `nextjs-16-skill` - Framework patterns
- `ui-design-skill` - Design patterns
