# Phase II: Web Application Testing Guide

Testing guide for the full-stack web application with authentication, OAuth, and PostgreSQL.

---

## Environment Setup

### Backend `.env` File

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Frontend `.env.local` File

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## How to Run Phase II

### Terminal 1 - Backend (Port 8000)

```bash
cd /path/to/hackathon-todo
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     database_engine_created
INFO:     database_tables_created
INFO:     api_starting
INFO:     Application startup complete.
```

### Terminal 2 - Frontend (Port 3000)

```bash
cd /path/to/hackathon-todo/frontend
npm install  # first time only
npm run dev
```

**Expected output:**
```
▲ Next.js 16.x
- Local: http://localhost:3000
✓ Ready
```

---

## Manual Testing Steps

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected:** `{"status": "healthy"}`

---

### Test 2: User Registration

1. Open http://localhost:3000
2. Click "Sign Up" or "Get Started"
3. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: TestPassword123
4. Submit form

**Expected:**
- Account created successfully
- Redirected to dashboard
- Welcome message with user name

---

### Test 3: User Sign In

1. Sign out if logged in
2. Go to http://localhost:3000/signin
3. Enter email and password
4. Submit

**Expected:**
- Successful login
- JWT token stored
- Redirected to dashboard

---

### Test 4: Create a Task

1. From dashboard, click "Add New Task" button
2. Fill in:
   - Title: Buy groceries
   - Description: Milk, bread, eggs
   - Priority: High
   - Due Date: Tomorrow
   - Tags: shopping, food
3. Click "Add Task"

**Expected:**
- Task appears in list
- Priority badge shows "High" (orange)
- Due date shows "Due tomorrow"
- Tags display as chips

---

### Test 5: Edit a Task

1. Hover over a task card
2. Click the **pencil icon** (Edit button)
3. Modify the task:
   - Change title to "Buy groceries and snacks"
   - Change priority to "Urgent"
4. Click "Update Task"

**Expected:**
- Form pre-filled with existing data
- Task updates immediately
- Changes reflected in task list
- Priority badge now shows "Urgent" (red)

---

### Test 6: Complete a Task

1. Click the circular checkbox on a task
2. Verify task status changes

**Expected:**
- Checkbox fills with checkmark
- Task title gets strikethrough
- Status badge changes to "Completed"
- Completion timestamp appears

---

### Test 7: Uncomplete a Task

1. Click checkbox on a completed task

**Expected:**
- Task reverts to "Pending" status
- Strikethrough removed
- Completion timestamp removed

---

### Test 8: Delete a Task

1. Hover over a task card
2. Click the **trash icon** (Delete button)
3. Click again to confirm

**Expected:**
- Delete confirmation tooltip appears
- Task removed from list after second click
- Task count updates

---

### Test 9: Search Tasks

1. Type in search bar: "groceries"
2. Verify results

**Expected:**
- Real-time filtering as you type
- Only matching tasks shown
- Result count displayed
- Clear button (X) appears

---

### Test 10: Filter by Status

1. Click "Pending" tab
2. Click "Completed" tab
3. Click "All" tab

**Expected:**
- Task list filters correctly
- Badge counts update
- Smooth transitions

---

### Test 11: Dashboard Statistics

Verify the stats cards show:
- Total Tasks (correct count)
- In Progress (pending count)
- Completed (completed count)
- Success Rate (percentage)

---

### Test 12: Responsive Design

1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test iPhone SE (320px)

**Expected:**
- [ ] Task cards stack vertically
- [ ] Edit/delete buttons always visible on mobile
- [ ] Search bar full width
- [ ] Filter tabs scrollable
- [ ] No horizontal overflow

---

### Test 13: OAuth Login (If Configured)

1. Sign out
2. Click "Continue with Google" or "Continue with GitHub"
3. Complete OAuth flow

**Expected:**
- Redirected to OAuth provider
- After approval, redirected back
- Account created/logged in
- User info populated from OAuth

---

### Test 14: Session Expiration

1. Log in
2. Wait for JWT to expire (or manually delete token)
3. Try to access dashboard

**Expected:**
- Redirected to sign in page
- Clear error message
- Auth state cleared

---

## API Testing

### Create Task via API

```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API Task",
    "description": "Created via API",
    "priority": "high",
    "tags": ["api", "test"]
  }'
```

### Update Task via API

```bash
curl -X PUT http://localhost:8000/api/users/{user_id}/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task",
    "priority": "urgent"
  }'
```

### Delete Task via API

```bash
curl -X DELETE http://localhost:8000/api/users/{user_id}/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Automated Tests

### Run Backend Tests

```bash
uv run pytest tests/ -v --cov=src
```

### Run with Coverage Report

```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Common Issues & Fixes

### Issue 1: CORS Error

**Symptom:** "Access-Control-Allow-Origin" error in console

**Fix:** Verify `FRONTEND_URL` in backend `.env` matches your frontend URL

### Issue 2: 401 Unauthorized

**Symptom:** API calls fail with 401

**Fix:**
- Check JWT token is being sent
- Verify token hasn't expired
- Re-login to get new token

### Issue 3: Database Connection Failed

**Symptom:** "Connection refused" error

**Fix:**
- Verify `DATABASE_URL` is correct
- Check PostgreSQL is running
- Test connection: `psql $DATABASE_URL -c "SELECT 1"`

### Issue 4: OAuth Callback Error

**Symptom:** "Redirect URI mismatch"

**Fix:**
- Verify callback URLs in OAuth provider settings
- Must match exactly: `http://localhost:8000/api/auth/google/callback`

---

## Phase II Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| User Registration | Yes | Email/password |
| User Sign In | Yes | JWT tokens |
| OAuth Login | Yes | Google, GitHub |
| Create Task | Yes | With all fields |
| Edit Task | Yes | Hover for edit button |
| Delete Task | Yes | Two-click confirm |
| Complete Task | Yes | Toggle checkbox |
| Priority Levels | Yes | Low, Medium, High, Urgent |
| Due Dates | Yes | With relative display |
| Tags | Yes | Up to 10 per task |
| Search | Yes | Real-time |
| Filters | Yes | All, Pending, Completed |
| Statistics | Yes | Dashboard cards |
| Responsive | Yes | Mobile-friendly |

---

## Summary

Phase II provides a complete web application with:
- User authentication (JWT + OAuth)
- Full CRUD operations for tasks
- Rich task metadata (priority, due dates, tags)
- Beautiful, responsive UI
- PostgreSQL persistence

**Next:** Phase III adds AI chatbot with natural language task management.
