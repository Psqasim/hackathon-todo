# Phase I: Console Application Testing Guide

Testing guide for the Rich console-based todo application with in-memory storage.

---

## Quick Start

```bash
# Run the console application
uv run todo
```

---

## Manual Testing Steps

### Test 1: Application Startup

```bash
uv run todo
```

**Expected:**
- Rich console menu appears with options:
  1. Add Task
  2. List Tasks
  3. Complete Task
  4. Delete Task
  5. Exit

**Screenshot checkpoint:** Main menu visible with all options

---

### Test 2: Add a Task

1. From main menu, select **1** (Add Task)
2. Enter task title: `Buy groceries`
3. Enter description: `Milk, bread, eggs`

**Expected:**
- Success message: "Task created successfully"
- Task ID displayed
- Returns to main menu

---

### Test 3: List Tasks

1. From main menu, select **2** (List Tasks)

**Expected:**
- Table displays with columns: ID, Title, Status, Created
- "Buy groceries" task appears with status "pending"
- Beautiful Rich table formatting

---

### Test 4: Add Multiple Tasks

1. Add 3 more tasks:
   - "Call mom" (no description)
   - "Finish homework" with description "Math chapter 5"
   - "Walk the dog"

2. List tasks again

**Expected:**
- All 4 tasks appear in the list
- Tasks ordered by creation time
- All status = "pending"

---

### Test 5: Complete a Task

1. From main menu, select **3** (Complete Task)
2. Enter the ID of "Buy groceries" task
3. List tasks

**Expected:**
- Task status changes to "completed"
- Completed task shows checkmark or different color
- Confirmation message displayed

---

### Test 6: Complete Already Completed Task

1. Try to complete the same task again

**Expected:**
- Task should toggle back to "pending"
- OR show message that task is already completed

---

### Test 7: Delete a Task

1. From main menu, select **4** (Delete Task)
2. Enter the ID of a task to delete
3. Confirm deletion
4. List tasks

**Expected:**
- Confirmation prompt before deletion
- Task removed from list
- Success message displayed

---

### Test 8: Delete Non-existent Task

1. Try to delete with invalid ID: `invalid-uuid-here`

**Expected:**
- Error message: "Task not found"
- Application handles gracefully
- Returns to main menu

---

### Test 9: Empty Task List

1. Delete all remaining tasks
2. List tasks

**Expected:**
- Empty state message: "No tasks found" or similar
- No error thrown
- Option to add new tasks

---

### Test 10: Exit Application

1. From main menu, select **5** (Exit)

**Expected:**
- Graceful exit with goodbye message
- No errors in terminal

---

### Test 11: Data Persistence Check

1. Exit the application
2. Run `uv run todo` again
3. List tasks

**Expected:**
- Empty list (in-memory storage doesn't persist)
- This is expected behavior for Phase I

---

## Keyboard Navigation

| Key | Action |
|-----|--------|
| 1-5 | Select menu option |
| Enter | Confirm input |
| Ctrl+C | Exit application |

---

## Architecture Verification

The console app uses the multi-agent architecture:

```
Console Input
    ↓
UIControllerAgent (Rich console display)
    ↓
OrchestratorAgent (command routing)
    ↓
TaskManagerAgent (business logic)
    ↓
StorageHandlerAgent (data operations)
    ↓
InMemoryBackend (temporary storage)
```

### Verify Agent Logs

Run with debug logging:
```bash
STRUCTLOG_LEVEL=DEBUG uv run todo
```

**Expected:**
- Log messages showing agent interactions
- Message routing between agents visible

---

## Common Issues & Fixes

### Issue 1: Command Not Found

**Symptom:** `uv run todo` not recognized

**Fix:**
```bash
uv sync --all-extras
```

### Issue 2: Rich Not Displaying Colors

**Symptom:** Plain text without formatting

**Fix:**
- Use a terminal that supports ANSI colors
- Try: `TERM=xterm-256color uv run todo`

### Issue 3: Unicode Characters Not Showing

**Symptom:** Boxes or question marks instead of icons

**Fix:**
- Use a font with unicode support (e.g., Nerd Font)
- Or use basic ASCII mode if available

---

## Phase I Limitations (By Design)

| Feature | Status | Notes |
|---------|--------|-------|
| Persistence | No | Data lost on exit |
| Authentication | No | Single user |
| Priority levels | No | Added in Phase II |
| Due dates | No | Added in Phase II |
| Tags | No | Added in Phase II |
| Web access | No | Console only |

---

## Summary

Phase I is a console application that demonstrates:
- Multi-agent architecture
- Rich terminal UI
- Basic CRUD operations
- In-memory storage

**Next:** Phase II adds web interface, authentication, and persistent storage.
