"""
FastAPI REST API interface.

Phase II: Web API for multi-user task management with OAuth support.
Phase V: Added event publishing for task lifecycle events.
"""

from __future__ import annotations

import asyncio
import secrets
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any, AsyncGenerator
from urllib.parse import urlencode

import httpx
import structlog
from fastapi import FastAPI, HTTPException, Query
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlmodel import Session, select

from src.auth import (
    CurrentUser,
    CurrentUserWithToken,
    create_access_token,
    hash_password,
    verify_password,
)
from src.config import ALLOWED_ORIGINS, settings
from src.db import create_tables, get_engine
from src.models import UserDB
from src.models.requests import (
    AuthResponse,
    CompleteTaskRequest,
    CompleteTaskResponse,
    CreateTaskRequest,
    DeleteTaskResponse,
    MessageResponse,
    SigninRequest,
    SignupRequest,
    SingleTaskResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
    UserResponse,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    logger.info("api_starting")
    create_tables()
    yield
    # Shutdown
    logger.info("api_shutting_down")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user task management (Phase II)",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS with dynamic origins from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# =============================================================================
# Health Endpoints
# =============================================================================


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/health/db", tags=["health"])
async def database_health() -> dict[str, str]:
    """Database connection health check."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "connected"}
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}",
        )


# =============================================================================
# Auth Endpoints
# =============================================================================


@app.post(
    "/api/auth/signup",
    response_model=AuthResponse,
    status_code=http_status.HTTP_201_CREATED,
    tags=["auth"],
)
async def signup(request: SignupRequest) -> AuthResponse:
    """
    Register a new user account.

    - Creates user with hashed password
    - Returns JWT token and user info

    Raises:
        409 Conflict: If email already exists
    """
    engine = get_engine()

    with Session(engine) as session:
        # Check if email already exists (T028)
        existing = session.exec(
            select(UserDB).where(UserDB.email == request.email)
        ).first()

        if existing:
            logger.warning("signup_email_exists", email=request.email)
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Create user with hashed password (T026, T027)
        user_db = UserDB(
            email=request.email,
            name=request.name,
            hashed_password=hash_password(request.password),
        )
        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        # Generate JWT token (T027)
        token = create_access_token({"sub": user_db.id})

        logger.info("user_registered", user_id=user_db.id, email=request.email)

        return AuthResponse(
            user=UserResponse(
                id=user_db.id,
                email=user_db.email,
                name=user_db.name,
                created_at=user_db.created_at,
            ),
            token=token,
        )


@app.post("/api/auth/signin", response_model=AuthResponse, tags=["auth"])
async def signin(request: SigninRequest) -> AuthResponse:
    """
    Sign in with email and password.

    - Verifies credentials
    - Returns JWT token and user info

    Raises:
        401 Unauthorized: If credentials are invalid
    """
    engine = get_engine()

    with Session(engine) as session:
        # Find user by email
        user_db = session.exec(
            select(UserDB).where(UserDB.email == request.email)
        ).first()

        if not user_db or not verify_password(request.password, user_db.hashed_password):
            logger.warning("signin_failed", email=request.email)
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Generate JWT token
        token = create_access_token({"sub": user_db.id})

        logger.info("user_signed_in", user_id=user_db.id)

        return AuthResponse(
            user=UserResponse(
                id=user_db.id,
                email=user_db.email,
                name=user_db.name,
                created_at=user_db.created_at,
            ),
            token=token,
        )


@app.post("/api/auth/signout", response_model=MessageResponse, tags=["auth"])
async def signout() -> MessageResponse:
    """
    Sign out the current user.

    Note: JWT tokens are stateless, so signout is handled client-side
    by removing the token. This endpoint exists for API consistency.
    """
    return MessageResponse(message="Signed out successfully")


# =============================================================================
# OAuth Endpoints
# =============================================================================

# In-memory OAuth state storage (use Redis in production)
oauth_states: dict[str, str] = {}


@app.get("/api/auth/google", tags=["oauth"])
async def google_oauth_start() -> RedirectResponse:
    """
    Start Google OAuth flow.
    Redirects user to Google's authorization page.
    """
    if not settings.google_client_id:
        raise HTTPException(
            status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "google"

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{settings.backend_url.rstrip('/')}/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@app.get("/api/auth/google/callback", tags=["oauth"])
async def google_oauth_callback(code: str, state: str) -> RedirectResponse:
    """
    Handle Google OAuth callback.
    Exchanges code for tokens, creates/updates user, redirects with JWT.
    """
    # Verify state
    if state not in oauth_states:
        return RedirectResponse(url=f"{settings.frontend_url}/signin?error=invalid_state")

    del oauth_states[state]

    if not settings.google_client_id or not settings.google_client_secret:
        return RedirectResponse(url=f"{settings.frontend_url}/signin?error=not_configured")

    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{settings.backend_url.rstrip('/')}/auth/google/callback",
                },
            )

            if token_response.status_code != 200:
                logger.error("google_token_error", response=token_response.text)
                return RedirectResponse(url=f"{settings.frontend_url}/signin?error=token_error")

            tokens = token_response.json()
            access_token = tokens.get("access_token")

            # Get user info
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_response.status_code != 200:
                return RedirectResponse(url=f"{settings.frontend_url}/signin?error=userinfo_error")

            userinfo = userinfo_response.json()

        # Create or update user
        email = userinfo.get("email")
        name = userinfo.get("name", email.split("@")[0])

        engine = get_engine()
        with Session(engine) as session:
            user_db = session.exec(
                select(UserDB).where(UserDB.email == email)
            ).first()

            if not user_db:
                # Create new user with random password (OAuth user)
                user_db = UserDB(
                    email=email,
                    name=name,
                    hashed_password=hash_password(secrets.token_urlsafe(32)),
                )
                session.add(user_db)
                session.commit()
                session.refresh(user_db)
                logger.info("oauth_user_created", provider="google", user_id=user_db.id)
            else:
                # Update name if changed
                if user_db.name != name:
                    user_db.name = name
                    session.add(user_db)
                    session.commit()
                logger.info("oauth_user_signed_in", provider="google", user_id=user_db.id)

            # Generate JWT
            token = create_access_token({"sub": user_db.id})

            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{settings.frontend_url}/auth/callback?token={token}&user_id={user_db.id}&email={email}&name={name}"
            )

    except Exception as e:
        logger.error("google_oauth_error", error=str(e))
        return RedirectResponse(url=f"{settings.frontend_url}/signin?error=oauth_error")


@app.get("/api/auth/github", tags=["oauth"])
async def github_oauth_start() -> RedirectResponse:
    """
    Start GitHub OAuth flow.
    Redirects user to GitHub's authorization page.
    """
    if not settings.github_client_id:
        raise HTTPException(
            status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured",
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "github"

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": f"{settings.backend_url.rstrip('/')}/auth/github/callback",
        "scope": "read:user user:email",
        "state": state,
    }

    github_auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=github_auth_url)


@app.get("/api/auth/github/callback", tags=["oauth"])
async def github_oauth_callback(code: str, state: str) -> RedirectResponse:
    """
    Handle GitHub OAuth callback.
    Exchanges code for tokens, creates/updates user, redirects with JWT.
    """
    # Verify state
    if state not in oauth_states:
        return RedirectResponse(url=f"{settings.frontend_url}/signin?error=invalid_state")

    del oauth_states[state]

    if not settings.github_client_id or not settings.github_client_secret:
        return RedirectResponse(url=f"{settings.frontend_url}/signin?error=not_configured")

    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
            )

            if token_response.status_code != 200:
                logger.error("github_token_error", response=token_response.text)
                return RedirectResponse(url=f"{settings.frontend_url}/signin?error=token_error")

            tokens = token_response.json()
            access_token = tokens.get("access_token")

            if not access_token:
                return RedirectResponse(url=f"{settings.frontend_url}/signin?error=no_token")

            # Get user info
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if user_response.status_code != 200:
                return RedirectResponse(url=f"{settings.frontend_url}/signin?error=userinfo_error")

            userinfo = user_response.json()

            # Get email (may be private)
            email = userinfo.get("email")
            if not email:
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    primary = next((e for e in emails if e.get("primary")), None)
                    if primary:
                        email = primary.get("email")

            if not email:
                return RedirectResponse(url=f"{settings.frontend_url}/signin?error=no_email")

            name = userinfo.get("name") or userinfo.get("login", email.split("@")[0])

        # Create or update user
        engine = get_engine()
        with Session(engine) as session:
            user_db = session.exec(
                select(UserDB).where(UserDB.email == email)
            ).first()

            if not user_db:
                # Create new user with random password (OAuth user)
                user_db = UserDB(
                    email=email,
                    name=name,
                    hashed_password=hash_password(secrets.token_urlsafe(32)),
                )
                session.add(user_db)
                session.commit()
                session.refresh(user_db)
                logger.info("oauth_user_created", provider="github", user_id=user_db.id)
            else:
                # Update name if changed
                if user_db.name != name:
                    user_db.name = name
                    session.add(user_db)
                    session.commit()
                logger.info("oauth_user_signed_in", provider="github", user_id=user_db.id)

            # Generate JWT
            token = create_access_token({"sub": user_db.id})

            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{settings.frontend_url}/auth/callback?token={token}&user_id={user_db.id}&email={email}&name={name}"
            )

    except Exception as e:
        logger.error("github_oauth_error", error=str(e))
        return RedirectResponse(url=f"{settings.frontend_url}/signin?error=oauth_error")


@app.get("/api/auth/me", response_model=UserResponse, tags=["auth"])
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """
    Get the current authenticated user's information.

    Requires: Valid JWT token in Authorization header

    Raises:
        401 Unauthorized: If not authenticated
    """
    engine = get_engine()

    with Session(engine) as session:
        user_db = session.get(UserDB, current_user)

        if not user_db:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return UserResponse(
            id=user_db.id,
            email=user_db.email,
            name=user_db.name,
            created_at=user_db.created_at,
        )


# =============================================================================
# Task Endpoints
# =============================================================================

# Import task models
from src.models import Task, TaskDB, db_to_task, task_to_db


@app.get("/api/users/{user_id}/tasks", response_model=TaskListResponse, tags=["tasks"])
async def list_tasks(
    user_id: str,
    current_user: CurrentUser,
    status_filter: str | None = Query(default=None, alias="status"),
    priority_filter: str | None = Query(default=None, alias="priority"),
    sort_by: str = Query(default="created_at", enum=["due_date", "priority", "created_at", "title"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"]),
) -> TaskListResponse:
    """
    Get all tasks for a user with sorting support.

    Args:
        user_id: User ID from path
        status: Optional filter by status (pending, completed)
        priority: Optional filter by priority (low, medium, high, urgent)
        sort_by: Sort field - due_date, priority, created_at, or title (default: created_at)
        sort_order: Sort order - asc or desc (default: desc)

    Raises:
        403 Forbidden: If user_id doesn't match authenticated user
    """
    # Authorization check (T047)
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks",
        )

    engine = get_engine()

    with Session(engine) as session:
        from sqlalchemy import case

        query = select(TaskDB).where(TaskDB.user_id == user_id)

        if status_filter:
            query = query.where(TaskDB.status == status_filter)

        if priority_filter:
            query = query.where(TaskDB.priority == priority_filter)

        # Apply sorting with special handling for priority and due_date
        if sort_by == "priority":
            # Priority order: urgent > high > medium > low
            priority_order = case(
                (TaskDB.priority == "urgent", 4),
                (TaskDB.priority == "high", 3),
                (TaskDB.priority == "medium", 2),
                (TaskDB.priority == "low", 1),
                else_=0
            )
            if sort_order == "asc":
                query = query.order_by(priority_order.asc())
            else:
                query = query.order_by(priority_order.desc())
        elif sort_by == "due_date":
            # Handle NULL values in due_date
            if sort_order == "asc":
                # nulls last for ascending
                query = query.order_by(TaskDB.due_date.asc().nullslast())
            else:
                # nulls first for descending
                query = query.order_by(TaskDB.due_date.desc().nullsfirst())
        else:
            # Standard sorting for created_at and title
            sort_column = getattr(TaskDB, sort_by, TaskDB.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

        tasks_db = session.exec(query).all()

        tasks = [
            TaskResponse(
                id=t.id,
                title=t.title,
                description=t.description,
                status=t.status,
                priority=t.priority,
                due_date=t.due_date,
                tags=t.tags or [],
                is_recurring=t.is_recurring,
                recurrence_pattern=t.recurrence_pattern,
                created_at=t.created_at,
                updated_at=t.updated_at,
                completed_at=t.completed_at,
            )
            for t in tasks_db
        ]

        return TaskListResponse(tasks=tasks)


@app.post(
    "/api/users/{user_id}/tasks",
    response_model=SingleTaskResponse,
    status_code=http_status.HTTP_201_CREATED,
    tags=["tasks"],
)
async def create_task_endpoint(
    user_id: str,
    request: CreateTaskRequest,
    current_user: CurrentUser,
) -> SingleTaskResponse:
    """
    Create a new task.

    Publishes task.created event and schedules reminder if due_date is set.

    Raises:
        403 Forbidden: If user_id doesn't match authenticated user
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user",
        )

    engine = get_engine()
    from src.events import get_publisher

    with Session(engine) as session:
        task_db = TaskDB(
            user_id=user_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            due_date=request.due_date,
            tags=request.tags,
            is_recurring=request.is_recurring,
            recurrence_pattern=request.recurrence_pattern,
        )
        session.add(task_db)
        session.commit()
        session.refresh(task_db)

        logger.info("task_created", task_id=task_db.id, user_id=user_id)

        # Publish task.created event (non-blocking)
        publisher = get_publisher()
        task_data = {
            "id": task_db.id,
            "title": task_db.title,
            "description": task_db.description,
            "status": task_db.status,
            "priority": task_db.priority,
            "due_date": task_db.due_date.isoformat() if task_db.due_date else None,
            "tags": task_db.tags or [],
            "is_recurring": task_db.is_recurring,
            "recurrence_pattern": task_db.recurrence_pattern,
        }
        asyncio.create_task(
            publisher.publish_task_event("created", task_db.id, user_id, task_data)
        )

        # Schedule reminder if due_date is set (1 hour before)
        if task_db.due_date:
            remind_at = task_db.due_date - timedelta(hours=1)
            if remind_at > datetime.now(UTC):
                asyncio.create_task(
                    publisher.publish_reminder_event(
                        task_db.id,
                        user_id,
                        task_db.title,
                        task_db.due_date,
                        remind_at,
                    )
                )

        return SingleTaskResponse(
            task=TaskResponse(
                id=task_db.id,
                title=task_db.title,
                description=task_db.description,
                status=task_db.status,
                priority=task_db.priority,
                due_date=task_db.due_date,
                tags=task_db.tags or [],
                is_recurring=task_db.is_recurring,
                recurrence_pattern=task_db.recurrence_pattern,
                created_at=task_db.created_at,
                updated_at=task_db.updated_at,
                completed_at=task_db.completed_at,
            )
        )


@app.get(
    "/api/users/{user_id}/tasks/{task_id}",
    response_model=SingleTaskResponse,
    tags=["tasks"],
)
async def get_task_endpoint(
    user_id: str,
    task_id: str,
    current_user: CurrentUser,
) -> SingleTaskResponse:
    """
    Get a single task by ID.

    Raises:
        403 Forbidden: If user_id doesn't match authenticated user
        404 Not Found: If task doesn't exist
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks",
        )

    engine = get_engine()

    with Session(engine) as session:
        task_db = session.exec(
            select(TaskDB).where(TaskDB.id == task_id, TaskDB.user_id == user_id)
        ).first()

        if not task_db:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}",
            )

        return SingleTaskResponse(
            task=TaskResponse(
                id=task_db.id,
                title=task_db.title,
                description=task_db.description,
                status=task_db.status,
                priority=task_db.priority,
                due_date=task_db.due_date,
                tags=task_db.tags or [],
                is_recurring=task_db.is_recurring,
                recurrence_pattern=task_db.recurrence_pattern,
                created_at=task_db.created_at,
                updated_at=task_db.updated_at,
                completed_at=task_db.completed_at,
            )
        )


@app.put(
    "/api/users/{user_id}/tasks/{task_id}",
    response_model=SingleTaskResponse,
    tags=["tasks"],
)
async def update_task_endpoint(
    user_id: str,
    task_id: str,
    request: UpdateTaskRequest,
    current_user: CurrentUser,
) -> SingleTaskResponse:
    """
    Update a task.

    Publishes task.updated event and reschedules reminder if due_date changed.

    Raises:
        403 Forbidden: If user_id doesn't match authenticated user
        404 Not Found: If task doesn't exist
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's tasks",
        )

    engine = get_engine()
    from src.events import get_publisher

    with Session(engine) as session:
        task_db = session.exec(
            select(TaskDB).where(TaskDB.id == task_id, TaskDB.user_id == user_id)
        ).first()

        if not task_db:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}",
            )

        # Track if due_date changed for reminder rescheduling
        old_due_date = task_db.due_date
        due_date_changed = False

        # Update fields
        if request.title is not None:
            task_db.title = request.title
        if request.description is not None:
            task_db.description = request.description
        if request.priority is not None:
            task_db.priority = request.priority
        if request.due_date is not None:
            task_db.due_date = request.due_date
            due_date_changed = old_due_date != request.due_date
        if request.tags is not None:
            task_db.tags = request.tags
        if request.is_recurring is not None:
            task_db.is_recurring = request.is_recurring
        if request.recurrence_pattern is not None:
            task_db.recurrence_pattern = request.recurrence_pattern

        task_db.updated_at = datetime.now(UTC)

        session.add(task_db)
        session.commit()
        session.refresh(task_db)

        logger.info("task_updated", task_id=task_id, user_id=user_id)

        # Publish task.updated event (non-blocking)
        publisher = get_publisher()
        task_data = {
            "id": task_db.id,
            "title": task_db.title,
            "description": task_db.description,
            "status": task_db.status,
            "priority": task_db.priority,
            "due_date": task_db.due_date.isoformat() if task_db.due_date else None,
            "tags": task_db.tags or [],
            "is_recurring": task_db.is_recurring,
            "recurrence_pattern": task_db.recurrence_pattern,
        }
        asyncio.create_task(
            publisher.publish_task_event("updated", task_db.id, user_id, task_data)
        )

        # Reschedule reminder if due_date changed
        if due_date_changed and task_db.due_date:
            remind_at = task_db.due_date - timedelta(hours=1)
            if remind_at > datetime.now(UTC):
                asyncio.create_task(
                    publisher.publish_reminder_event(
                        task_db.id,
                        user_id,
                        task_db.title,
                        task_db.due_date,
                        remind_at,
                    )
                )

        return SingleTaskResponse(
            task=TaskResponse(
                id=task_db.id,
                title=task_db.title,
                description=task_db.description,
                status=task_db.status,
                priority=task_db.priority,
                due_date=task_db.due_date,
                tags=task_db.tags or [],
                is_recurring=task_db.is_recurring,
                recurrence_pattern=task_db.recurrence_pattern,
                created_at=task_db.created_at,
                updated_at=task_db.updated_at,
                completed_at=task_db.completed_at,
            )
        )


@app.delete(
    "/api/users/{user_id}/tasks/{task_id}",
    response_model=DeleteTaskResponse,
    tags=["tasks"],
)
async def delete_task_endpoint(
    user_id: str,
    task_id: str,
    current_user: CurrentUser,
) -> DeleteTaskResponse:
    """
    Delete a task.

    Publishes task.deleted event.

    Raises:
        403 Forbidden: If user_id doesn't match authenticated user
        404 Not Found: If task doesn't exist
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user's tasks",
        )

    engine = get_engine()
    from src.events import get_publisher

    with Session(engine) as session:
        task_db = session.exec(
            select(TaskDB).where(TaskDB.id == task_id, TaskDB.user_id == user_id)
        ).first()

        if not task_db:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}",
            )

        # Capture task data before deletion
        task_data = {
            "id": task_db.id,
            "title": task_db.title,
            "description": task_db.description,
            "status": task_db.status,
            "priority": task_db.priority,
            "due_date": task_db.due_date.isoformat() if task_db.due_date else None,
            "tags": task_db.tags or [],
            "is_recurring": task_db.is_recurring,
            "recurrence_pattern": task_db.recurrence_pattern,
        }

        session.delete(task_db)
        session.commit()

        logger.info("task_deleted", task_id=task_id, user_id=user_id)

        # Publish task.deleted event (non-blocking)
        publisher = get_publisher()
        asyncio.create_task(
            publisher.publish_task_event("deleted", task_id, user_id, task_data)
        )

        return DeleteTaskResponse(deleted=True, task_id=task_id)


@app.patch(
    "/api/users/{user_id}/tasks/{task_id}/complete",
    response_model=CompleteTaskResponse,
    tags=["tasks"],
)
async def complete_task_endpoint(
    user_id: str,
    task_id: str,
    request: CompleteTaskRequest,
    current_user: CurrentUser,
) -> CompleteTaskResponse:
    """
    Toggle task completion status.

    For recurring tasks marked as completed, automatically creates the next occurrence.

    Raises:
        403 Forbidden: If user_id doesn't match authenticated user
        404 Not Found: If task doesn't exist
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this user's tasks",
        )

    engine = get_engine()

    with Session(engine) as session:
        task_db = session.exec(
            select(TaskDB).where(TaskDB.id == task_id, TaskDB.user_id == user_id)
        ).first()

        if not task_db:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}",
            )

        from src.utils.recurrence import calculate_next_due_date
        from src.events import get_publisher

        now = datetime.now(UTC)
        next_task_db = None

        if request.completed:
            task_db.status = "completed"
            task_db.completed_at = now

            # Check if task is recurring and should create next occurrence
            if task_db.is_recurring and task_db.recurrence_pattern and task_db.due_date:
                # Calculate next due date
                next_due_date = calculate_next_due_date(task_db.due_date, task_db.recurrence_pattern)

                # Create next occurrence
                next_task_db = TaskDB(
                    user_id=user_id,
                    title=task_db.title,
                    description=task_db.description,
                    priority=task_db.priority,
                    due_date=next_due_date,
                    tags=task_db.tags,
                    is_recurring=task_db.is_recurring,
                    recurrence_pattern=task_db.recurrence_pattern,
                    status="pending",
                    created_at=now,
                    updated_at=now,
                )
                session.add(next_task_db)

                logger.info(
                    "recurring_task_next_occurrence_created",
                    original_task_id=task_id,
                    next_task_id=next_task_db.id,
                    next_due_date=next_due_date.isoformat(),
                    user_id=user_id,
                )
        else:
            task_db.status = "pending"
            task_db.completed_at = None

        task_db.updated_at = now

        session.add(task_db)
        session.commit()
        session.refresh(task_db)

        if next_task_db:
            session.refresh(next_task_db)

        logger.info(
            "task_completion_toggled",
            task_id=task_id,
            user_id=user_id,
            completed=request.completed,
            created_next_occurrence=next_task_db is not None,
        )

        # Publish task.completed event (non-blocking)
        if request.completed:
            publisher = get_publisher()
            task_data = {
                "id": task_db.id,
                "title": task_db.title,
                "description": task_db.description,
                "status": task_db.status,
                "priority": task_db.priority,
                "due_date": task_db.due_date.isoformat() if task_db.due_date else None,
                "tags": task_db.tags or [],
                "is_recurring": task_db.is_recurring,
                "recurrence_pattern": task_db.recurrence_pattern,
            }
            asyncio.create_task(
                publisher.publish_task_event("completed", task_db.id, user_id, task_data)
            )

        return CompleteTaskResponse(
            completed_task=TaskResponse(
                id=task_db.id,
                title=task_db.title,
                description=task_db.description,
                status=task_db.status,
                priority=task_db.priority,
                due_date=task_db.due_date,
                tags=task_db.tags or [],
                is_recurring=task_db.is_recurring,
                recurrence_pattern=task_db.recurrence_pattern,
                created_at=task_db.created_at,
                updated_at=task_db.updated_at,
                completed_at=task_db.completed_at,
            ),
            next_occurrence=TaskResponse(
                id=next_task_db.id,
                title=next_task_db.title,
                description=next_task_db.description,
                status=next_task_db.status,
                priority=next_task_db.priority,
                due_date=next_task_db.due_date,
                tags=next_task_db.tags or [],
                is_recurring=next_task_db.is_recurring,
                recurrence_pattern=next_task_db.recurrence_pattern,
                created_at=next_task_db.created_at,
                updated_at=next_task_db.updated_at,
                completed_at=next_task_db.completed_at,
            ) if next_task_db else None
        )


# =============================================================================
# Convenience Task Endpoints (Current User)
# =============================================================================
# These endpoints automatically use the authenticated user's ID
# Equivalent to /api/users/{user_id}/tasks but without needing user_id in path


@app.get("/api/tasks", response_model=TaskListResponse, tags=["tasks"])
async def list_current_user_tasks(
    current_user: CurrentUser,
    status_filter: str | None = Query(default=None, alias="status"),
    priority_filter: str | None = Query(default=None, alias="priority"),
    sort_by: str = Query(default="created_at", enum=["due_date", "priority", "created_at", "title"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"]),
) -> TaskListResponse:
    """Get all tasks for the authenticated user."""
    return await list_tasks(
        user_id=current_user,
        current_user=current_user,
        status_filter=status_filter,
        priority_filter=priority_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@app.post(
    "/api/tasks",
    response_model=SingleTaskResponse,
    status_code=http_status.HTTP_201_CREATED,
    tags=["tasks"],
)
async def create_current_user_task(
    request: CreateTaskRequest,
    current_user: CurrentUser,
) -> SingleTaskResponse:
    """Create a new task for the authenticated user."""
    return await create_task_endpoint(
        user_id=current_user,
        request=request,
        current_user=current_user,
    )


@app.get("/api/tasks/{task_id}", response_model=SingleTaskResponse, tags=["tasks"])
async def get_current_user_task(
    task_id: str,
    current_user: CurrentUser,
) -> SingleTaskResponse:
    """Get a specific task for the authenticated user."""
    return await get_task_endpoint(
        user_id=current_user,
        task_id=task_id,
        current_user=current_user,
    )


@app.put("/api/tasks/{task_id}", response_model=SingleTaskResponse, tags=["tasks"])
async def update_current_user_task(
    task_id: str,
    request: UpdateTaskRequest,
    current_user: CurrentUser,
) -> SingleTaskResponse:
    """Update a specific task for the authenticated user."""
    return await update_task_endpoint(
        user_id=current_user,
        task_id=task_id,
        request=request,
        current_user=current_user,
    )


@app.delete("/api/tasks/{task_id}", response_model=DeleteTaskResponse, tags=["tasks"])
async def delete_current_user_task(
    task_id: str,
    current_user: CurrentUser,
) -> DeleteTaskResponse:
    """Delete a specific task for the authenticated user."""
    return await delete_task_endpoint(
        user_id=current_user,
        task_id=task_id,
        current_user=current_user,
    )


@app.patch(
    "/api/tasks/{task_id}/complete",
    response_model=CompleteTaskResponse,
    tags=["tasks"],
)
async def complete_current_user_task(
    task_id: str,
    request: CompleteTaskRequest,
    current_user: CurrentUser,
) -> CompleteTaskResponse:
    """Toggle completion status for the authenticated user's task."""
    return await complete_task_endpoint(
        user_id=current_user,
        task_id=task_id,
        request=request,
        current_user=current_user,
    )


# =============================================================================
# Chat Endpoints (Phase III - Spec Compliant)
# =============================================================================
#
# Architecture (Phase III Spec Requirement):
# - Chat history is stored in PostgreSQL (Conversation, Message tables)
# - Backend is stateless - all state comes from database
# - Conversations persist across server restarts
# - Frontend fetches conversations and messages from API
# =============================================================================

from src.models.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationDB,
    ConversationListResponse,
    ConversationSummary,
    ConversationDetail,
    DeleteResponse,
    MessageDB,
)


@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat_endpoint(
    request: ChatRequest,
    user_with_token: CurrentUserWithToken,
) -> ChatResponse:
    """
    Send a message to the AI chatbot.

    FR-020: POST /api/chat accepts message and optional conversation_id
    FR-021: Returns AI response with conversation_id for continuity
    FR-030: Stores conversation history in PostgreSQL database

    Args:
        request: Chat message and optional conversation_id

    Returns:
        AI response with conversation_id
    """
    from src.mcp_server.agent import TaskAgent

    # Extract user_id and token from the authenticated dependency
    user_id, token = user_with_token

    # Create agent with token for authenticated backend calls
    agent = TaskAgent(token=token)

    try:
        response = await agent.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
        )

        # Create response message
        assistant_message = ChatMessage(
            role="assistant",
            content=response.content,
        )

        logger.info(
            "chat_message_processed",
            user_id=user_id,
            conversation_id=response.conversation_id,
            tool_calls=len(response.tool_calls),
        )

        return ChatResponse(
            conversation_id=response.conversation_id,
            message=assistant_message,
        )
    except Exception as e:
        logger.error("chat_error", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {e!s}",
        )


@app.post("/api/users/{user_id}/chat", response_model=ChatResponse, tags=["chat"])
async def chat_endpoint_with_user_id(
    user_id: str,
    request: ChatRequest,
    current_user: CurrentUser,
) -> ChatResponse:
    """
    Send a message to the AI chatbot (spec-compliant endpoint).

    POST /api/{user_id}/chat as required by Phase III spec.
    Stores all messages in PostgreSQL for stateless backend.

    Args:
        user_id: User ID from path
        request: Chat message and optional conversation_id

    Returns:
        AI response with conversation_id
    """
    from src.mcp_server.agent import TaskAgent

    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to chat as this user",
        )

    # Create agent (no token needed for this endpoint pattern)
    agent = TaskAgent()

    try:
        response = await agent.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
        )

        # Create response message
        assistant_message = ChatMessage(
            role="assistant",
            content=response.content,
        )

        logger.info(
            "chat_message_processed",
            user_id=user_id,
            conversation_id=response.conversation_id,
            tool_calls=len(response.tool_calls),
        )

        return ChatResponse(
            conversation_id=response.conversation_id,
            message=assistant_message,
        )
    except Exception as e:
        logger.error("chat_error", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {e!s}",
        )


@app.get("/api/conversations", response_model=ConversationListResponse, tags=["chat"])
async def list_conversations(
    current_user: CurrentUser,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> ConversationListResponse:
    """
    List user's conversations from database.

    Phase III Spec Compliant: Returns conversations from PostgreSQL.
    """
    engine = get_engine()

    with Session(engine) as session:
        # Count total conversations
        from sqlalchemy import func
        total = session.exec(
            select(func.count()).select_from(ConversationDB).where(
                ConversationDB.user_id == current_user
            )
        ).one()

        # Get conversations with pagination
        convs = session.exec(
            select(ConversationDB)
            .where(ConversationDB.user_id == current_user)
            .order_by(ConversationDB.updated_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

        # Count messages per conversation
        conversations = []
        for conv in convs:
            msg_count = session.exec(
                select(func.count()).select_from(MessageDB).where(
                    MessageDB.conversation_id == conv.id
                )
            ).one()

            conversations.append(
                ConversationSummary(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=msg_count,
                )
            )

        return ConversationListResponse(
            conversations=conversations,
            total=total,
        )


@app.get("/api/users/{user_id}/conversations", response_model=ConversationListResponse, tags=["chat"])
async def list_user_conversations(
    user_id: str,
    current_user: CurrentUser,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> ConversationListResponse:
    """
    List user's conversations from database (spec-compliant endpoint).

    GET /api/{user_id}/conversations as required by Phase III spec.
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations",
        )

    engine = get_engine()

    with Session(engine) as session:
        # Count total conversations
        from sqlalchemy import func
        total = session.exec(
            select(func.count()).select_from(ConversationDB).where(
                ConversationDB.user_id == user_id
            )
        ).one()

        # Get conversations with pagination
        convs = session.exec(
            select(ConversationDB)
            .where(ConversationDB.user_id == user_id)
            .order_by(ConversationDB.updated_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

        # Count messages per conversation
        conversations = []
        for conv in convs:
            msg_count = session.exec(
                select(func.count()).select_from(MessageDB).where(
                    MessageDB.conversation_id == conv.id
                )
            ).one()

            conversations.append(
                ConversationSummary(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=msg_count,
                )
            )

        return ConversationListResponse(
            conversations=conversations,
            total=total,
        )


@app.get("/api/conversations/{conversation_id}", response_model=ConversationDetail, tags=["chat"])
async def get_conversation_by_id(
    conversation_id: str,
    current_user: CurrentUser,
) -> ConversationDetail:
    """
    Get a conversation with all messages by conversation ID.

    GET /api/conversations/{id} - returns conversation with message history.
    Uses the authenticated user's ID for authorization.
    """
    engine = get_engine()

    with Session(engine) as session:
        # Get conversation - verify it belongs to current user
        conv = session.exec(
            select(ConversationDB).where(
                ConversationDB.id == conversation_id,
                ConversationDB.user_id == current_user,
            )
        ).first()

        if not conv:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Get messages
        messages_db = session.exec(
            select(MessageDB)
            .where(MessageDB.conversation_id == conversation_id)
            .order_by(MessageDB.created_at.asc())
        ).all()

        messages = [
            ChatMessage(
                id=msg.id,
                role=msg.role,  # type: ignore
                content=msg.content,
                tool_calls=None,
                created_at=msg.created_at,
            )
            for msg in messages_db
        ]

        return ConversationDetail(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=messages,
        )


@app.get("/api/users/{user_id}/conversations/{conversation_id}", response_model=ConversationDetail, tags=["chat"])
async def get_conversation(
    user_id: str,
    conversation_id: str,
    current_user: CurrentUser,
) -> ConversationDetail:
    """
    Get a conversation with all messages.

    GET /api/{user_id}/conversations/{id} - returns conversation with message history.
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    engine = get_engine()

    with Session(engine) as session:
        # Get conversation
        conv = session.exec(
            select(ConversationDB).where(
                ConversationDB.id == conversation_id,
                ConversationDB.user_id == user_id,
            )
        ).first()

        if not conv:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Get messages
        messages_db = session.exec(
            select(MessageDB)
            .where(MessageDB.conversation_id == conversation_id)
            .order_by(MessageDB.created_at.asc())
        ).all()

        messages = [
            ChatMessage(
                id=msg.id,
                role=msg.role,  # type: ignore
                content=msg.content,
                tool_calls=None,  # Tool calls stored separately
                created_at=msg.created_at,
            )
            for msg in messages_db
        ]

        return ConversationDetail(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=messages,
        )


@app.get("/api/users/{user_id}/conversations/{conversation_id}/messages", tags=["chat"])
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    current_user: CurrentUser,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """
    Get messages for a conversation with pagination.

    GET /api/{user_id}/conversations/{id}/messages - returns paginated messages.
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    engine = get_engine()

    with Session(engine) as session:
        # Verify conversation exists and belongs to user
        conv = session.exec(
            select(ConversationDB).where(
                ConversationDB.id == conversation_id,
                ConversationDB.user_id == user_id,
            )
        ).first()

        if not conv:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Count total messages
        from sqlalchemy import func
        total = session.exec(
            select(func.count()).select_from(MessageDB).where(
                MessageDB.conversation_id == conversation_id
            )
        ).one()

        # Get messages with pagination
        messages_db = session.exec(
            select(MessageDB)
            .where(MessageDB.conversation_id == conversation_id)
            .order_by(MessageDB.created_at.asc())
            .offset(offset)
            .limit(limit)
        ).all()

        messages = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages_db
        ]

        return {
            "messages": messages,
            "total": total,
            "offset": offset,
            "limit": limit,
        }


@app.delete(
    "/api/conversations/{conversation_id}",
    response_model=DeleteResponse,
    tags=["chat"],
)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
) -> DeleteResponse:
    """
    Delete a conversation and all its messages.

    Phase III Spec Compliant: Deletes from PostgreSQL database.
    """
    engine = get_engine()

    with Session(engine) as session:
        # Find conversation
        conv = session.exec(
            select(ConversationDB).where(
                ConversationDB.id == conversation_id,
                ConversationDB.user_id == current_user,
            )
        ).first()

        if not conv:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Delete all messages first using bulk delete for FK safety
        from sqlalchemy import delete
        session.exec(
            delete(MessageDB).where(MessageDB.conversation_id == conversation_id)  # type: ignore
        )
        session.flush()  # Ensure messages are deleted before conversation

        # Delete conversation
        session.delete(conv)
        session.commit()

        logger.info(
            "conversation_deleted",
            conversation_id=conversation_id,
            user_id=current_user,
        )

        return DeleteResponse(deleted=True, id=conversation_id)


@app.delete(
    "/api/users/{user_id}/conversations/{conversation_id}",
    response_model=DeleteResponse,
    tags=["chat"],
)
async def delete_user_conversation(
    user_id: str,
    conversation_id: str,
    current_user: CurrentUser,
) -> DeleteResponse:
    """
    Delete a conversation and all its messages (spec-compliant endpoint).
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this conversation",
        )

    engine = get_engine()

    with Session(engine) as session:
        # Find conversation
        conv = session.exec(
            select(ConversationDB).where(
                ConversationDB.id == conversation_id,
                ConversationDB.user_id == user_id,
            )
        ).first()

        if not conv:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Delete all messages first using bulk delete for FK safety
        from sqlalchemy import delete
        session.exec(
            delete(MessageDB).where(MessageDB.conversation_id == conversation_id)  # type: ignore
        )
        session.flush()  # Ensure messages are deleted before conversation

        # Delete conversation
        session.delete(conv)
        session.commit()

        logger.info(
            "conversation_deleted",
            conversation_id=conversation_id,
            user_id=user_id,
        )

        return DeleteResponse(deleted=True, id=conversation_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.interfaces.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
