---
id: 010
title: OAuth Logout UX Improvements
stage: general
date: 2025-12-29
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-app
branch: 002-fullstack-web-app
user: psqasim
command: conversation
labels: ["oauth", "logout", "ux", "github", "google", "authentication"]
links:
  spec: specs/002-fullstack-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/auth-client.ts
  - frontend/components/header.tsx
  - frontend/app/page.tsx
  - src/interfaces/api.py
  - src/config.py
  - .env.example
  - frontend/README.md
  - README.md
tests:
  - Manual OAuth flow testing (Google & GitHub)
---

## Prompt

Fix the GitHub OAuth re-login behavior to match Google's flow:

**Problem:**
After logout, clicking "Sign in with GitHub" redirects directly to dashboard without showing the login page.

**Root Cause:**
GitHub OAuth tokens/sessions are being cached somewhere (browser localStorage, cookies, or backend session).

**Solution Requirements:**
1. Clear localStorage completely on signout
2. Clear all auth-related cookies
3. Clear any cached OAuth state
4. Redirect to homepage (not signin page)
5. Fix slow logout issue
6. Improve logout UI/UX (remove double-click requirement)

Also fix: when user clicks Home from dashboard, it auto-redirects back to dashboard after 1 second.

## Response snapshot

### Changes Made:

**1. auth-client.ts - Enhanced signout function:**
- Added `clearAllCookies()` helper to clear all browser cookies
- Updated `clearAuth()` to clear localStorage, sessionStorage, and cookies
- Made `signout()` non-blocking - clears auth immediately, then notifies backend asynchronously

**2. header.tsx - Improved logout UX:**
- Removed double-click confirmation requirement
- Added single-click logout with loading spinner
- Uses `window.location.href = "/"` for clean redirect (clears React state)

**3. page.tsx (Home) - Fixed auto-redirect issue:**
- Removed auto-redirect to dashboard for authenticated users
- Added `isLoggedIn` state to conditionally show different CTAs
- Authenticated users see "Go to Dashboard" button instead of redirect

**4. OAuth Backend Fixes:**
- Added `backend_url` config setting for OAuth callback URLs
- Fixed redirect_uri to use backend URL (port 8000) instead of frontend (port 3000)
- Updated CORS to allow multiple origins

## Outcome

- Impact: OAuth login/logout flow now works correctly for both Google and GitHub
- Tests: Manual testing of OAuth flows confirmed working
- Files: 8 files modified
- Next prompts: None - feature complete
- Reflection: OAuth redirect_uri must point to backend, not frontend

## Evaluation notes (flywheel)

- Failure modes observed: OAuth callback URL misconfiguration causing 404 on frontend
- Graders run and results (PASS/FAIL): PASS - Manual testing confirmed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add token blacklist for true JWT invalidation
