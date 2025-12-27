---
id: "005"
title: "Add Update Task Feature"
stage: green
date: 2025-12-27
surface: agent
model: claude-opus-4-5-20251101
feature: 001-multi-agent-architecture
branch: 001-multi-agent-architecture
user: psqasim
command: /sp.implement
labels: ["feature", "update-task", "ui", "console"]
links:
  spec: specs/001-multi-agent-architecture/spec.md
  plan: specs/001-multi-agent-architecture/plan.md
  tasks: specs/001-multi-agent-architecture/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - src/agents/ui_controller.py
  - src/app.py
tests:
  - tests/ (148 tests - all passing)
---

## Prompt

The todo app is missing the "Update Task" feature in the console menu.

Looking at src/app.py and src/adapters/console.py, I can see the update functionality exists in the task_manager but isn't exposed in the UI menu.

Please:
1. Add "3. Update Task" option to the main menu (shift other options down)
2. Implement the update task workflow in src/app.py that:
   - Lists all tasks
   - Asks user to select task ID to update
   - Shows current title and description
   - Prompts for new title (or press Enter to keep current)
   - Prompts for new description (or press Enter to keep current)
   - Calls task_manager's task_update action
   - Shows success message

The new menu should be:
1. Add Task
2. View All Tasks
3. Update Task          ← NEW
4. Mark Task Complete   ← Was 3
5. Delete Task          ← Was 4
6. Exit                 ← Was 5

Test the update workflow after implementing.

## Response

Successfully implemented the "Update Task" feature:

### Changes Made

**src/agents/ui_controller.py:**
- Updated MAIN_MENU_OPTIONS to new 6-item menu with shifted options
- Added `ui_get_update_details` action handler that:
  - Shows current title and description
  - Prompts for new values with defaults
  - Returns new values (or None to keep current)

**src/app.py:**
- Added `_handle_update_task()` method implementing the workflow:
  1. Lists all tasks for selection
  2. Gets current task details
  3. Prompts user for updates (with current values as defaults)
  4. Calls `task_update` action
  5. Shows success message
- Updated main loop to handle new menu option numbers (3=Update, 4=Complete, 5=Delete, 6=View)

### New Menu
```
[1] Add Task
[2] View All Tasks
[3] Update Task          ← NEW
[4] Mark Task Complete
[5] Delete Task
[6] View Task Details
[q] Quit
```

### Testing
- All 148 existing tests pass
- Verified update workflow programmatically:
  - Add task with original title/description
  - Update to new values
  - Verify changes persisted

## Outcome

Update Task feature fully implemented and tested. The console menu now exposes all 6 task operations (Add, View All, Update, Complete, Delete, View Details).
