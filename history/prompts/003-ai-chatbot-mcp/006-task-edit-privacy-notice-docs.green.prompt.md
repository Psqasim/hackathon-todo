---
id: 006
title: Task Edit Fix, Privacy Notice, and Documentation Updates
stage: green
date: 2025-12-31
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-chatbot-mcp
branch: 003-ai-chatbot-mcp
user: ps_qasim
command: chat
labels: ["task-editing", "privacy-notice", "documentation", "testing-guides", "readme"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/task-card.tsx
  - frontend/app/chat/page.tsx
  - docs/PHASE-I-TESTING-GUIDE.md
  - docs/PHASE-II-TESTING-GUIDE.md
  - docs/PHASE-III-TESTING-GUIDE.md
  - README.md
tests:
  - Manual testing required for all changes
---

## Prompt

Fix task editing in dashboard and add privacy notice to chatbot:

## Part 1: Fix Task Update in Dashboard

Problem: Users cannot edit/update tasks in the Phase II dashboard (http://localhost:3000/dashboard)

Solution:
- Add edit button to task cards (pencil icon)
- Create edit form (or reuse existing task form)
- Allow users to modify title, description, priority, due date, tags
- Call API endpoint: PUT /api/users/{user_id}/tasks/{task_id}
- Update task list after successful edit

## Part 2: Add Privacy Notice to Chatbot

Problem: Users don't know their chats are stored with OpenAI

Solution:
- Create privacy notice component (modal/dialog)
- Show when user first visits /chat page
- Display message explaining:
  * Tasks stored in our database
  * Chat history stored with OpenAI for 30 days
  * Not used to train models
- Two buttons: "I Agree & Continue", "Go to Dashboard"
- Check localStorage on page load
- Don't show again if user already agreed

## Part 3: Update Documentation

Create separate testing guides and update README.

## Part 4: Create PHR

## Response snapshot

### Part 1: Task Editing Fix

**Finding:** The task editing functionality was already implemented! The issue was that edit/delete buttons only appeared on hover (`opacity-0 group-hover:opacity-100`), making them invisible on mobile devices.

**Fix applied to `frontend/components/task-card.tsx`:**
```tsx
// Changed from:
opacity-0 group-hover:opacity-100 transition-opacity duration-200

// Changed to:
sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-200
```

Now buttons are always visible on mobile, hover-to-show on desktop.

### Part 2: Privacy Notice Modal

**Added to `frontend/app/chat/page.tsx`:**

1. **localStorage helpers:**
   - `PRIVACY_CONSENT_KEY = "taskflow_chat_privacy_consent"`
   - `hasPrivacyConsent()` - checks if consent given
   - `setPrivacyConsent()` - saves consent to localStorage

2. **PrivacyNoticeModal component:**
   - Purple gradient header with lock icon
   - Three info cards explaining data handling:
     - Tasks: stored in our database
     - Chat History: stored with OpenAI for 30 days
     - Not Used for Training: data never trains AI models
   - Two buttons:
     - "Go to Dashboard" - redirects to /dashboard
     - "I Agree & Continue" - saves consent, shows chat

3. **State management:**
   - `showPrivacyNotice` - controls modal visibility
   - `hasConsent` - tracks if user has agreed
   - Check on page load, show modal if no consent

### Part 3: Documentation

**Created:**
- `docs/PHASE-I-TESTING-GUIDE.md` - Console app testing (11 tests)
- `docs/PHASE-II-TESTING-GUIDE.md` - Web app testing (14 tests, includes edit task test)

**Updated:**
- `docs/PHASE-III-TESTING-GUIDE.md` - Added Test 2: Privacy Notice Modal (renumbered all tests)
- `README.md` - Added Phase III section with:
  - Prerequisites (OpenAI API key)
  - Running instructions (3 terminals)
  - Features table
  - Architecture diagram
  - Data storage table
  - Updated comparison table (3 phases)

## Outcome

- ✅ Impact: Task editing now works on mobile, privacy notice informs users about data handling
- 🧪 Tests: Manual testing required - verify edit button visibility, privacy modal flow
- 📁 Files: 6 files modified/created
- 🔁 Next prompts: Test all features manually, verify mobile responsiveness
- 🧠 Reflection: The edit functionality was already there - the UX issue was visibility. Privacy notice uses same modal pattern as other consent flows.

## Evaluation notes (flywheel)

- Failure modes observed: None - straightforward implementation
- Graders run and results (PASS/FAIL): N/A - manual verification needed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add animation to privacy modal entrance
