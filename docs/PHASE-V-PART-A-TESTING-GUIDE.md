# Phase V Part A Testing Guide

## Overview

Phase V Part A adds three independent features to TaskFlow:
1. **Sort Functionality** - Organize tasks by due_date, priority, created_at, or title
2. **Recurring Tasks** - Auto-create next occurrence when recurring tasks are completed
3. **Event Publishing** - Publish task lifecycle events (preparation for Kafka integration)

This guide provides step-by-step testing instructions for each feature.

---

## Prerequisites

1. **Backend Running**: `uvicorn src.interfaces.api:app --reload --port 8000`
2. **Frontend Running**: `cd frontend && npm run dev`
3. **Database**: PostgreSQL running with tables created
4. **User Account**: Sign up/sign in to access dashboard
5. **Python Dependencies**: `pip install -e .` (includes python-dateutil)

---

## Feature 1: Sort Functionality Testing

### Test 1.1: Sort by Priority

**Setup**: Create tasks with different priorities
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Urgent Task",
    "priority": "urgent"
  }'

curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Low Priority Task",
    "priority": "low"
  }'

curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High Priority Task",
    "priority": "high"
  }'
```

**Test Steps**:
1. Open dashboard at `http://localhost:3000/dashboard`
2. Click the "Sort by" dropdown (upper right of task list)
3. Select "Priority"
4. **Expected**: Tasks appear in order: Urgent → High → Low
5. Click the up/down arrow button to toggle order
6. **Expected**: Order reverses: Low → High → Urgent

**Pass Criteria**: ✅ Tasks reorder correctly, priority sorting works

---

### Test 1.2: Sort by Due Date

**Setup**: Create tasks with various due dates
```bash
# Task due tomorrow
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Due Tomorrow",
    "due_date": "2026-02-06T10:00:00Z"
  }'

# Task due next week
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Due Next Week",
    "due_date": "2026-02-12T10:00:00Z"
  }'

# Task with no due date
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "No Due Date"
  }'
```

**Test Steps**:
1. In dashboard, select "Sort by: Due Date"
2. **Expected** (desc): Nearest due date first, tasks without due dates last
3. Toggle to ascending order
4. **Expected** (asc): Earliest due date first, tasks without due dates last

**Pass Criteria**: ✅ NULL due dates handled correctly, dates sort properly

---

### Test 1.3: Sort Persistence

**Test Steps**:
1. Select "Sort by: Title" with ascending order
2. Reload the page (F5)
3. **Expected**: Sort selection persists (still "Title, ascending")
4. Open browser DevTools → Application → Local Storage
5. **Expected**: Keys `taskSortBy` and `taskSortOrder` are present

**Pass Criteria**: ✅ Sort preference saved and restored from localStorage

---

## Feature 2: Recurring Tasks Testing

### Test 2.1: Daily Recurring Task

**Setup**: Create daily recurring task
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "due_date": "2026-02-06T09:00:00Z",
    "is_recurring": true,
    "recurrence_pattern": "daily"
  }'
```

**Test Steps**:
1. Find "Daily Standup" task in dashboard
2. Check the checkbox to mark it complete
3. **Expected**:
   - Original task shows as completed with checkmark
   - Toast notification appears: "✅ Task completed! Next occurrence created for Feb 7, 2026"
   - New "Daily Standup" task appears with due_date = Feb 7, 2026 09:00
4. Wait 5 seconds
5. **Expected**: Toast auto-hides

**Pass Criteria**: ✅ Next occurrence created +1 day, toast notification appears

---

### Test 2.2: Weekly Recurring Task

**Setup**: Create weekly recurring task
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "due_date": "2026-02-06T14:00:00Z",
    "is_recurring": true,
    "recurrence_pattern": "weekly"
  }'
```

**Test Steps**:
1. Complete "Team Meeting" task
2. **Expected**: New task created with due_date = Feb 13, 2026 14:00 (+7 days)
3. **Expected**: Toast shows "Next occurrence created for Feb 13, 2026"

**Pass Criteria**: ✅ Weekly recurrence adds 7 days correctly

---

### Test 2.3: Monthly Recurring Task (Edge Case)

**Setup**: Create task due on Jan 31
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Monthly Report",
    "due_date": "2026-01-31T17:00:00Z",
    "is_recurring": true,
    "recurrence_pattern": "monthly"
  }'
```

**Test Steps**:
1. Complete "Monthly Report" task
2. **Expected**: Next occurrence due_date = Feb 28, 2026 17:00 (not Feb 31, which doesn't exist)
3. Complete that task
4. **Expected**: Next occurrence due_date = Mar 31, 2026 17:00

**Pass Criteria**: ✅ Monthly recurrence handles month-end dates correctly

---

### Test 2.4: Non-Recurring Task

**Setup**: Create normal task (not recurring)
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "One-Time Task",
    "due_date": "2026-02-06T10:00:00Z",
    "is_recurring": false
  }'
```

**Test Steps**:
1. Complete "One-Time Task"
2. **Expected**:
   - Task marked as completed
   - NO toast notification
   - NO new task created

**Pass Criteria**: ✅ Non-recurring tasks don't create next occurrence

---

## Feature 3: Event Publishing Testing

### Test 3.1: Task Created Event

**Setup**: Ensure `DAPR_ENABLED=false` in `.env` (default)

**Test Steps**:
1. Watch backend logs: `tail -f logs/app.log` (or check console)
2. Create a new task via dashboard
3. **Expected Log Entries**:
   ```
   task_created task_id=<uuid> user_id=<user_id>
   Dapr disabled, skipping publish to task-events: TaskEvent
   ```

**Pass Criteria**: ✅ Event logged but not sent (Dapr disabled)

---

### Test 3.2: Task with Due Date - Reminder Event

**Test Steps**:
1. Create task with due_date set to 2 hours from now
2. **Expected Log Entries**:
   ```
   task_created task_id=<uuid> user_id=<user_id>
   Dapr disabled, skipping publish to task-events: TaskEvent
   Dapr disabled, skipping publish to reminders: ReminderEvent
   ```
3. Create task with due_date in 30 minutes
4. **Expected**: No reminder event (remind_at would be in past)

**Pass Criteria**: ✅ Reminder scheduled only if remind_at > now

---

### Test 3.3: Task Updated Event

**Test Steps**:
1. Update task title or priority via dashboard
2. **Expected Log Entries**:
   ```
   task_updated task_id=<uuid> user_id=<user_id>
   Dapr disabled, skipping publish to task-events: TaskEvent
   ```
3. Update task due_date to 3 hours from now
4. **Expected**: Additional reminder event logged

**Pass Criteria**: ✅ Update events published, reminder rescheduled

---

### Test 3.4: Task Completed Event

**Test Steps**:
1. Mark task as complete
2. **Expected Log Entries**:
   ```
   task_completion_toggled task_id=<uuid> user_id=<user_id> completed=True
   Dapr disabled, skipping publish to task-events: TaskEvent
   ```

**Pass Criteria**: ✅ Completed event published

---

### Test 3.5: Task Deleted Event

**Test Steps**:
1. Delete a task
2. **Expected Log Entries**:
   ```
   task_deleted task_id=<uuid> user_id=<user_id>
   Dapr disabled, skipping publish to task-events: TaskEvent
   ```

**Pass Criteria**: ✅ Deleted event published with task snapshot

---

### Test 3.6: Non-Blocking Event Publishing

**Test Steps**:
1. Create 10 tasks rapidly (use loop or script)
2. **Expected**: All tasks created successfully without delays
3. Check logs after all tasks created
4. **Expected**: All event logs present (may be out of order due to async)

**Pass Criteria**: ✅ API responses not blocked by event publishing

---

## Integration Testing

### Integration Test 1: Sort + Recurring

**Test Steps**:
1. Create 3 recurring tasks with different priorities
2. Sort by priority
3. Complete the highest priority recurring task
4. **Expected**:
   - Next occurrence appears at correct priority position
   - List remains sorted by priority

**Pass Criteria**: ✅ Features work together seamlessly

---

### Integration Test 2: All Features Combined

**Test Steps**:
1. Create recurring task with due_date and high priority
2. Sort by due_date
3. Complete the task
4. **Expected**:
   - Toast notification appears
   - Next occurrence created
   - Event published (check logs)
   - List re-sorted with new task
5. Change sort to priority
6. **Expected**: Tasks reorder by priority

**Pass Criteria**: ✅ All three features work together without conflicts

---

## API Testing (Optional)

### Test Sort API Directly

```bash
# Sort by priority descending
curl http://localhost:8000/api/users/{user_id}/tasks?sort=priority&order=desc \
  -H "Authorization: Bearer {token}"

# Sort by due_date ascending
curl http://localhost:8000/api/users/{user_id}/tasks?sort=due_date&order=asc \
  -H "Authorization: Bearer {token}"

# Sort by title ascending
curl http://localhost:8000/api/users/{user_id}/tasks?sort=title&order=asc \
  -H "Authorization: Bearer {token}"
```

**Expected**: JSON response with tasks in correct order

---

### Test Complete Recurring Task API

```bash
curl -X PATCH http://localhost:8000/api/users/{user_id}/tasks/{task_id}/complete \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

**Expected Response**:
```json
{
  "completed_task": {
    "id": "...",
    "title": "...",
    "status": "completed",
    ...
  },
  "next_occurrence": {
    "id": "...",
    "title": "...",
    "status": "pending",
    "due_date": "2026-02-13T10:00:00Z",
    ...
  }
}
```

---

## Troubleshooting

### Issue: Sort dropdown doesn't appear
- **Cause**: Frontend not rebuilt after code changes
- **Fix**: Restart frontend dev server: `npm run dev`

### Issue: Recurring task doesn't create next occurrence
- **Check**: Task has `is_recurring=true` AND `due_date` is set
- **Check**: Recurrence pattern is valid ("daily", "weekly", "monthly", "yearly")
- **Check**: Backend logs for errors

### Issue: Toast notification doesn't appear
- **Check**: Browser console for JavaScript errors
- **Check**: Task actually has next occurrence in API response
- **Fix**: Clear browser cache and reload

### Issue: Events not published
- **Expected**: When `DAPR_ENABLED=false`, events are only logged
- **Check**: Backend logs for "Dapr disabled, skipping publish"
- **Note**: Actual event delivery requires Part B (Kafka + Dapr)

### Issue: Sort preference doesn't persist
- **Check**: Browser localStorage is enabled
- **Check**: Not in incognito/private browsing mode
- **Fix**: Clear localStorage and try again

---

## Performance Testing

### Test Sort Performance

**Test Steps**:
1. Create 100 tasks with random priorities and due dates
2. Sort by each option (priority, due_date, created_at, title)
3. Measure response time in Network tab
4. **Expected**: < 500ms for all sort operations

### Test Recurring Task Creation Performance

**Test Steps**:
1. Create 50 recurring tasks
2. Complete all 50 simultaneously (use script)
3. Measure time to create 50 next occurrences
4. **Expected**: < 10 seconds total

---

## Regression Testing

Ensure existing features still work:

### Phase 1-4 Features
- [ ] User authentication (signup/signin)
- [ ] Task CRUD operations
- [ ] Task filtering (pending/completed tabs)
- [ ] Search functionality
- [ ] AI chat interface
- [ ] Priority and tags
- [ ] Kubernetes deployment

**Pass Criteria**: All existing features work without breaking

---

## Success Criteria Summary

### Sort Functionality
- [X] Backend accepts sort_by and sort_order parameters
- [X] Priority sorting uses correct order (urgent > high > medium > low)
- [X] Due date sorting handles NULL values correctly
- [X] Frontend dropdown works with all 4 sort options
- [X] Sort preference persists in localStorage
- [X] Ascending/descending toggle works

### Recurring Tasks
- [X] Daily recurrence adds +1 day
- [X] Weekly recurrence adds +7 days
- [X] Monthly recurrence handles month-end dates
- [X] Next occurrence created with correct due_date
- [X] Toast notification appears and auto-hides
- [X] Non-recurring tasks don't create next occurrence

### Event Publishing
- [X] Task created event published
- [X] Task updated event published
- [X] Task completed event published
- [X] Task deleted event published
- [X] Reminder events scheduled for tasks with due_date
- [X] Events are non-blocking (asyncio.create_task)
- [X] App works normally when DAPR_ENABLED=false

---

## Next Steps

After passing all tests in Part A:
1. **Part B**: Install Kafka + Dapr on Minikube
2. **Part B**: Deploy notification service
3. **Part B**: Set `DAPR_ENABLED=true` and test actual event delivery
4. **Part C**: Deploy to Oracle Cloud (OKE)

---

**Testing Guide Version**: 1.0
**Date**: 2026-02-05
**Status**: Phase V Part A Complete ✅
