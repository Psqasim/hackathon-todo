# Research: Full-Stack Web Application (Phase II)

**Feature Branch**: `002-fullstack-web-app`
**Date**: 2025-12-28
**Status**: Complete

## Research Tasks

### 1. Better Auth + FastAPI JWT Integration

**Decision**: Use shared BETTER_AUTH_SECRET for JWT validation

**Rationale**:
- Better Auth in Next.js creates JWT tokens with user claims
- FastAPI validates these tokens using python-jose with the same secret
- No need for session database synchronization between apps
- Stateless authentication scales horizontally

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Session cookies | Requires shared session store between apps |
| OAuth2 authorization server | Over-engineered for single application |
| API key authentication | No user identity, single credential for all |

**Implementation Pattern**:
```python
# Backend JWT validation (FastAPI)
from jose import jwt, JWTError
from fastapi import HTTPException, Header

def get_current_user(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "")
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
    return payload.get("sub")  # user_id
```

---

### 2. StorageBackend Protocol Extension

**Decision**: Add optional `user_id` filter parameter to existing protocol methods

**Rationale**:
- Maintains backward compatibility with Phase I in-memory backend
- PostgreSQL backend implements filtering at query level
- No breaking changes to StorageHandlerAgent interface

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| New UserTaskStorage protocol | Would require StorageHandlerAgent rewrite |
| Separate user filtering middleware | Adds complexity, not DRY |
| Task model with embedded user filtering | Mixes concerns, violates SRP |

**Implementation Pattern**:
```python
# Extended protocol methods (optional user_id)
async def query(
    self,
    status: str | None = None,
    user_id: str | None = None,  # NEW: optional filter
) -> list[Task]:
    ...
```

---

### 3. Next.js 16 App Router + Better Auth

**Decision**: Use server-side session with middleware protection

**Rationale**:
- App Router supports server components for data fetching
- Middleware protects routes before rendering
- Server Actions for mutations (no client-side API calls for auth)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Pages Router | Deprecated pattern, less performant |
| Client-side only auth | Security issues, hydration flicker |
| NextAuth.js | Better Auth has simpler JWT setup |

**Key Files**:
```
frontend/
├── lib/auth.ts           # Better Auth configuration
├── lib/auth-client.ts    # Client-side auth helpers
├── middleware.ts         # Route protection
└── app/api/auth/[...all]/route.ts  # Auth API routes
```

---

### 4. SQLModel vs Raw SQLAlchemy

**Decision**: Use SQLModel for database models

**Rationale**:
- Combines Pydantic validation with SQLAlchemy ORM
- Single model definition for validation AND persistence
- Native async support with asyncpg
- Matches existing Pydantic-based Task model pattern

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Raw SQLAlchemy | Separate validation models needed |
| Prisma (Python) | Limited Python support, TypeScript-focused |
| Tortoise ORM | Less mature, smaller ecosystem |

**Migration Strategy**:
- Keep existing Pydantic `Task` model for API contracts
- Create SQLModel `TaskDB` and `UserDB` for database tables
- Convert between models at storage layer boundary

---

### 5. Neon PostgreSQL Connection

**Decision**: Use psycopg2-binary with connection pooling

**Rationale**:
- Neon uses standard PostgreSQL wire protocol
- psycopg2-binary includes compiled binaries (no build required)
- SQLModel/SQLAlchemy handle connection pooling automatically

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| asyncpg | Would require full async rewrite of storage layer |
| psycopg3 | Less mature, SQLModel compatibility issues |
| Neon serverless driver | JavaScript-only, not available for Python |

**Connection String Format**:
```
postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

---

### 6. CORS Configuration

**Decision**: Allow localhost:3000 in development, configurable for production

**Rationale**:
- Frontend (Next.js) on port 3000
- Backend (FastAPI) on port 8000
- CORS required for cross-origin requests with credentials

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 7. API Route Structure

**Decision**: RESTful routes with user_id in path

**Rationale**:
- Clear ownership semantics: `/api/users/{user_id}/tasks`
- JWT token provides authentication
- Path parameter provides authorization context
- Matches hackathon spec requirements

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `/api/tasks` (implicit user) | Less explicit, harder to debug |
| GraphQL | Over-engineered for CRUD operations |
| tRPC | Requires TypeScript backend |

---

### 8. Testing Strategy Alignment

**Decision**: Maintain 60%+ coverage, add API integration tests

**Rationale**:
- Phase I achieved 56.72% with 148 tests
- Add FastAPI TestClient tests for endpoints
- Keep existing unit tests for agents/skills

**Test Categories**:
| Category | Location | Tools |
|----------|----------|-------|
| Unit (agents) | `tests/unit/` | pytest, pytest-asyncio |
| API integration | `tests/integration/api/` | FastAPI TestClient |
| Database | `tests/integration/db/` | pytest with test DB |
| Frontend (optional) | `frontend/tests/` | Vitest |

---

## Resolved Clarifications

All technical decisions have been made. No [NEEDS CLARIFICATION] items remain.

## Dependencies Confirmed

| Dependency | Version | Purpose |
|------------|---------|---------|
| fastapi | ^0.109.0 | REST API framework |
| uvicorn[standard] | ^0.27.0 | ASGI server |
| sqlmodel | ^0.0.14 | ORM with Pydantic |
| psycopg2-binary | ^2.9.9 | PostgreSQL driver |
| python-jose[cryptography] | ^3.3.0 | JWT validation |
| python-multipart | ^0.0.6 | Form data parsing |
| next | 16.x | React framework |
| better-auth | latest | Authentication |
| tailwindcss | ^3.4.0 | Styling |
