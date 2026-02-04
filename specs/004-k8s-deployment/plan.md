# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-k8s-deployment` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-k8s-deployment/spec.md`

**Note**: This plan details the technical architecture and implementation approach for deploying TaskFlow to local Kubernetes cluster while maintaining all Phase I-III functionality.

## Summary

Deploy the TaskFlow Todo application to a local Kubernetes cluster using Docker Desktop, containerizing the FastAPI backend and Next.js frontend with production-ready multi-stage builds. This phase introduces cloud-native patterns (health probes, resource limits, ConfigMap/Secret management, security context) while maintaining zero changes to business logic from Phases I-III. The deployment uses ClusterIP for internal backend communication and LoadBalancer for external frontend access, connecting to the existing external Neon PostgreSQL database.

## Technical Context

**Language/Version**: Python 3.12+ (backend), Node.js 20+ (frontend), Bash (scripts)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Pydantic, httpx, OpenAI Agents SDK, MCP Python SDK, uvicorn
- Frontend: Next.js 16+, React 19+, TypeScript, TailwindCSS, Better Auth
- Build tools: UV (Python), npm (Node.js), Docker 24.0+
- Orchestration: Kubernetes 1.28+ (Docker Desktop), kubectl 1.28+, Helm 3.0+ (bonus)

**Storage**: Neon PostgreSQL (external, unchanged from Phase II-III)
**Testing**: pytest (backend), Jest/React Testing Library (frontend), docker CLI (image verification), kubectl (deployment verification)
**Target Platform**: Local Kubernetes cluster on Docker Desktop (Windows WSL2/macOS/Linux)
**Project Type**: Web application (monorepo: backend + frontend) with Kubernetes infrastructure

**Performance Goals**:
- Backend image build: <5 minutes
- Frontend image build: <3 minutes
- Backend image size: <500MB
- Frontend image size: <300MB
- Pod startup: <2 minutes (Running status)
- Health probe response: <5 seconds
- End-to-end task workflow: <30 seconds

**Constraints**:
- Images must run as non-root users (UID 1000)
- Must use imagePullPolicy: Never (local images)
- Resource requests: 256Mi/250m CPU (both services)
- Resource limits: 500Mi/500m CPU (backend), 512Mi/500m CPU (frontend)
- Health checks must not require database connection (keep fast)
- All Phase I-III functionality must remain operational
- No persistent volumes (stateless pods, external database)

**Scale/Scope**:
- 2 Deployments, 2 Services, 1 ConfigMap, 1 Secret, 1 Namespace
- 7 Kubernetes manifest files
- 2 multi-stage Dockerfiles
- 3 helper scripts (build, deploy, secrets generator)
- 27 total components across 6 implementation phases
- Bonus: 4 Helm chart components (Chart.yaml, values.yaml, templates/, helpers)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Agent Architecture Patterns
- **Compliance**: Phase IV adds new deployment interfaces (Docker, Kubernetes) without modifying existing agents
- **Orchestrator unchanged**: Main Orchestrator Agent continues coordinating Task Manager, Storage Handler, UI Controller
- **Subagent contracts preserved**: No changes to agent communication protocols
- **Justification**: Infrastructure layer (Docker/K8s) sits below application layer, agents communicate identically within containers

### ✅ Skill Reusability Standards
- **Compliance**: All skills remain technology-agnostic and interface-independent
- **Skills unchanged**: Task CRUD operations work identically in containers as in local/cloud environments
- **Stateless requirement met**: Skills continue using Storage Agent for state (no container-specific state)
- **Justification**: Containerization is transparent to application layer, skills see no difference

### ✅ Separation of Concerns
- **Compliance**: Docker/Kubernetes are infrastructure concerns, separate from UI/business/data layers
- **Layer preservation**:
  - UI Layer: Next.js frontend in container, same code as Phase II
  - Business Logic: Task Manager Agent in container, unchanged from Phase III
  - Data Layer: Storage Handler continues using external Neon PostgreSQL
- **Justification**: Containerization wraps existing layers without penetrating them

### ✅ Evolution Strategy
- **Phase IV goals met**:
  - Docker containerization of all services ✓
  - Local Kubernetes deployment (Docker Desktop) ✓
  - Helm charts for orchestration ✓
  - kubectl for K8s operations ✓
- **Non-breaking evolution**: Phase I-III continue functioning, new deployment option added
- **Justification**: Additive change - local dev still works, cloud deployment (Phase II-III) still works, K8s is third option

### ✅ Testing Standards
- **TDD compliance**: Tests written before Docker/K8s implementation
- **Coverage target**: Infrastructure tests (Dockerfile builds, pod health, service connectivity) added to existing 80%+ coverage
- **Test hierarchy maintained**:
  - Unit tests: Unchanged (agent/skill logic containerized but tested identically)
  - Integration tests: Add container-to-container communication tests
  - E2E tests: Add K8s deployment workflow tests (build → deploy → verify → test)
  - Contract tests: Add health endpoint contract tests

### ✅ Code Quality Requirements
- **Python/Node.js standards maintained**: No code quality changes required (infrastructure only)
- **Dependency management**: UV (backend), npm (frontend) continue working in containers
- **New dependencies**: None - using existing tools differently (docker, kubectl are external tools)
- **Justification**: Dockerfiles and K8s manifests are configuration (YAML/Dockerfile), not Python/JS code

### ✅ Error Handling
- **Container-specific errors**: Health probe failures, pod crashes, service unavailability
- **Error principles applied**:
  - Liveness probe detects failures → automatic pod restart
  - Readiness probe removes unhealthy pods from service endpoints
  - Startup probe allows slow initialization → prevents premature restarts
- **Logging**: Container stdout/stderr captured by kubectl logs, structured logging preserved
- **Justification**: Kubernetes error handling complements application error handling, adds infrastructure resilience

### ✅ Spec-Driven Development
- **Specification complete**: specs/004-k8s-deployment/spec.md approved (12/12 quality checklist items passed)
- **Implementation fidelity**: This plan references spec sections, all components map to functional requirements
- **Documentation**: README.md, PHASE-IV-TESTING-GUIDE.md, DEPLOYMENT.md updates planned
- **Justification**: SDD workflow followed rigorously, plan derived from spec

### Constitution Compliance Summary

**Status**: ✅ **FULLY COMPLIANT** - No violations, no exceptions needed

All 8 core principles satisfied:
1. Agent architecture unchanged (infrastructure layer separate)
2. Skills remain reusable (containerization transparent)
3. Separation of concerns maintained (infrastructure ≠ business logic)
4. Evolution strategy followed (Phase IV goals met, non-breaking)
5. Testing standards applied (TDD for infrastructure components)
6. Code quality preserved (configuration files, not code changes)
7. Error handling enhanced (K8s resilience + app error handling)
8. Spec-driven development followed (approved spec → detailed plan)

## Project Structure

### Documentation (this feature)

```text
specs/004-k8s-deployment/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (COMPLETE)
├── research.md          # Phase 0: K8s best practices research (TO CREATE)
├── data-model.md        # Phase 1: Container/Pod/Service entities (TO CREATE)
├── quickstart.md        # Phase 1: Local K8s setup guide (TO CREATE)
├── contracts/           # Phase 1: Health endpoint, K8s resource contracts (TO CREATE)
│   ├── health-endpoint.yaml
│   ├── backend-deployment.yaml
│   └── frontend-deployment.yaml
├── checklists/
│   └── requirements.md  # Spec quality validation (COMPLETE)
└── tasks.md             # Phase 2: Implementation tasks (/sp.tasks - NOT YET)
```

### Source Code (repository root)

```text
# Existing structure (from Phase I-III)
backend/
├── src/
│   ├── agents/          # Orchestrator, Task Manager, Storage Handler, UI Controller
│   ├── skills/          # Task CRUD skills (unchanged)
│   ├── models/          # Pydantic models, SQLModel entities
│   ├── interfaces/
│   │   └── api.py       # FastAPI routes (ADD /health endpoint)
│   └── mcp_server/      # MCP server implementation
├── tests/               # pytest tests (ADD container tests)
├── pyproject.toml       # UV dependencies
├── uv.lock
└── Dockerfile           # NEW: Multi-stage backend image

frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # React components
│   └── lib/             # API client, utilities
├── public/              # Static assets
├── tests/               # Jest/React tests
├── package.json
├── next.config.js       # UPDATE: Add output: 'standalone'
└── Dockerfile           # NEW: Multi-stage frontend image

# New Kubernetes infrastructure (Phase IV)
k8s/
├── namespace.yaml           # NEW: taskflow namespace
├── configmap.yaml           # NEW: Non-sensitive config
├── secrets.yaml             # NEW: Base64 secrets (generated, gitignored)
├── backend-deployment.yaml  # NEW: Backend pods with health probes
├── backend-service.yaml     # NEW: ClusterIP service
├── frontend-deployment.yaml # NEW: Frontend pods
└── frontend-service.yaml    # NEW: LoadBalancer service

scripts/
├── build-images.sh          # NEW: Automated Docker builds
├── deploy-k8s.sh            # NEW: Automated K8s deployment
├── generate-secrets.sh      # NEW: Create secrets.yaml from .env
└── start-backend.sh         # NEW: Container startup script (FastAPI + MCP)

# Helm chart (Bonus)
helm/taskflow/
├── Chart.yaml               # NEW: Helm metadata
├── values.yaml              # NEW: Configurable values
├── templates/
│   ├── _helpers.tpl         # NEW: Template functions
│   ├── namespace.yaml       # NEW: Templated K8s resources
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
└── .helmignore

docs/
├── PHASE-IV-TESTING-GUIDE.md  # NEW: K8s deployment testing guide
└── DEPLOYMENT.md              # UPDATE: Add K8s section

# Root-level Docker exclusions
.dockerignore                  # NEW: Exclude from backend build context
frontend/.dockerignore         # NEW: Exclude from frontend build context

# Phase I console (unchanged)
src/
├── cli/                       # Click/Typer CLI (still works locally)
└── ...
```

**Structure Decision**:
- **Existing monorepo preserved**: `backend/` and `frontend/` directories unchanged
- **New infrastructure added**: `k8s/` for manifests, `helm/` for charts, `scripts/` for automation
- **Dockerfiles co-located**: Backend Dockerfile at root (context: entire backend/), frontend Dockerfile in frontend/ (context: frontend/)
- **Separation maintained**: Infrastructure (k8s/, helm/) separate from application code (backend/, frontend/)
- **Phase I independence**: src/ CLI remains functional for local console usage

## Complexity Tracking

**No violations detected** - Constitution Check passed all gates. No complexity justification needed.

---

## Phase 0: Research & Investigation

**Objective**: Resolve Context7 research findings into actionable design decisions for Docker/Kubernetes implementation.

### Research Areas

1. **Docker Multi-Stage Build Patterns**
   - **Question**: What's the optimal multi-stage pattern for Python (UV) and Node.js (Next.js standalone)?
   - **Research task**: Compare builder+runtime pattern vs dependencies+builder+runtime pattern
   - **Output**: Decision on stage count, base image selection (slim vs alpine), layer optimization

2. **Kubernetes Health Probe Timing**
   - **Question**: What are the correct initialDelaySeconds, periodSeconds, failureThreshold values for FastAPI and Next.js?
   - **Research task**: Analyze startup times, determine probe timing to avoid false failures
   - **Output**: Specific timing values for liveness, readiness, startup probes

3. **Next.js Standalone Output**
   - **Question**: How to configure Next.js for optimal container deployment?
   - **Research task**: Understand standalone mode, required files (.next/standalone, .next/static, public)
   - **Output**: next.config.js changes, Dockerfile copy patterns

4. **ConfigMap vs Secret Usage**
   - **Question**: Which configuration belongs in ConfigMap vs Secret?
   - **Research task**: Review sensitivity of each environment variable
   - **Output**: Categorization list (JWT_ALGORITHM → ConfigMap, JWT_SECRET_KEY → Secret)

5. **Non-Root User Security**
   - **Question**: How to create and switch to non-root users in Debian (slim) and Alpine containers?
   - **Research task**: Compare `adduser` (Debian) vs `adduser`/`addgroup` (Alpine) syntax
   - **Output**: Exact user creation commands for both base images

6. **Resource Limit Tuning**
   - **Question**: Are 256Mi/250m CPU requests and 500Mi/500m CPU limits appropriate?
   - **Research task**: Measure actual resource usage in development, add headroom
   - **Output**: Justified resource values or adjustments

### Research Deliverable: `research.md`

**Contents**:
- **Docker Base Images**: Decision (python:3.12-slim, node:20-alpine), rationale (size vs compatibility), alternatives (alpine variants, full images)
- **Multi-Stage Build Strategy**: Decision (2-stage backend, 3-stage frontend), rationale (layer caching, size optimization)
- **Health Probe Configuration**: Decision matrix (startup: 5s×30=150s max, liveness: 30s initial/10s period, readiness: 10s initial/5s period)
- **Next.js Standalone**: Implementation steps (config change, file copy pattern, environment variables)
- **ConfigMap Design**: Non-sensitive list (JWT_ALGORITHM, JWT_EXPIRATION_DAYS, BACKEND_URL, MCP_BACKEND_URL)
- **Secret Design**: Sensitive list (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY, OAuth credentials)
- **Security Context**: User creation commands (Debian: `adduser --uid 1000 --disabled-password`, Alpine: `addgroup -g 1000 && adduser -u 1000`)
- **Resource Allocation**: Justification (backend: higher CPU for API requests, frontend: higher memory for Next.js SSR)

---

## Phase 1: Architecture & Contracts

**Objective**: Define container/pod/service entities, API contracts, and deployment interfaces.

### Component 1: Data Model (`data-model.md`)

**Entities** (Infrastructure, not application data):

1. **Docker Image (Backend)**
   - **Attributes**:
     - Name: taskflow-backend
     - Tag: latest
     - Base: python:3.12-slim
     - Layers: builder (UV + dependencies), runtime (copied .venv + source)
     - Size constraint: <500MB
     - User: appuser (UID 1000)
     - Exposed ports: 7860 (FastAPI), 8001 (MCP)
   - **Relationships**: Used by Backend Deployment
   - **Validation**: Must pass non-root user check, health endpoint must respond

2. **Docker Image (Frontend)**
   - **Attributes**:
     - Name: taskflow-frontend
     - Tag: latest
     - Base: node:20-alpine
     - Layers: dependencies (npm ci), builder (npm run build), runner (standalone copy)
     - Size constraint: <300MB
     - User: nodejs (UID 1000)
     - Exposed port: 3000
   - **Relationships**: Used by Frontend Deployment
   - **Validation**: Must serve homepage on port 3000, standalone mode verified

3. **Namespace**
   - **Attributes**:
     - Name: taskflow
     - Labels: {app: taskflow, phase: 4}
   - **Relationships**: Contains all deployments, services, configmaps, secrets
   - **Validation**: Must exist before resource creation

4. **ConfigMap**
   - **Attributes**:
     - Name: taskflow-config
     - Namespace: taskflow
     - Data keys: JWT_ALGORITHM, JWT_EXPIRATION_DAYS, BACKEND_URL, NEXT_PUBLIC_API_URL, MCP_BACKEND_URL
   - **Relationships**: Referenced by both deployments as environment variables
   - **Validation**: All values must be plain text (not base64), keys must match app expectations

5. **Secret**
   - **Attributes**:
     - Name: taskflow-secrets
     - Namespace: taskflow
     - Data keys (base64): DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
   - **Relationships**: Referenced by backend deployment as environment variables
   - **Validation**: All values must be base64-encoded, keys must exist in .env source

6. **Backend Deployment**
   - **Attributes**:
     - Name: backend-deployment
     - Namespace: taskflow
     - Replicas: 1
     - Selector: {app: taskflow-backend}
     - Image: taskflow-backend:latest
     - Ports: 7860, 8001
     - Resources: {requests: 256Mi/250m, limits: 500Mi/500m}
     - Probes: liveness, readiness, startup on /health:7860
     - Security: runAsNonRoot, runAsUser 1000
   - **Relationships**: Creates backend pods, referenced by backend service
   - **State transitions**: Pending → ContainerCreating → Running → (crash) → Restarting → Running

7. **Backend Service**
   - **Attributes**:
     - Name: backend-service
     - Namespace: taskflow
     - Type: ClusterIP
     - Port: 8000 (external within cluster)
     - TargetPort: 7860 (container port)
     - Selector: {app: taskflow-backend}
   - **Relationships**: Routes traffic to backend pods
   - **Validation**: Must have ClusterIP assigned, endpoint list must include pod IPs

8. **Frontend Deployment**
   - **Attributes**:
     - Name: frontend-deployment
     - Namespace: taskflow
     - Replicas: 1
     - Selector: {app: taskflow-frontend}
     - Image: taskflow-frontend:latest
     - Port: 3000
     - Resources: {requests: 256Mi/250m, limits: 512Mi/500m}
     - Probes: liveness, readiness on /:3000
     - Security: runAsNonRoot, runAsUser 1000
   - **Relationships**: Creates frontend pods, referenced by frontend service
   - **State transitions**: Same as backend deployment

9. **Frontend Service**
   - **Attributes**:
     - Name: frontend-service
     - Namespace: taskflow
     - Type: LoadBalancer
     - Port: 80 (external public)
     - TargetPort: 3000 (container port)
     - Selector: {app: taskflow-frontend}
   - **Relationships**: Routes external traffic to frontend pods
   - **Validation**: Must have LoadBalancer IP (or localhost on Docker Desktop), accessible from browser

10. **Health Probe**
    - **Attributes**:
      - Type: liveness | readiness | startup
      - Mechanism: httpGet | tcpSocket | exec
      - Path: /health (backend), / (frontend)
      - Port: 7860 (backend), 3000 (frontend)
      - Timing: initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold
    - **Relationships**: Embedded in deployment specs, executed by kubelet
    - **State transitions**: Unknown → Success → Failure → (action: restart pod or remove from endpoints)

**Entity Relationships Diagram**:
```
[Namespace: taskflow]
    │
    ├── [ConfigMap] ──env──> [Backend Deployment] ──creates──> [Backend Pod]
    │                             │                                 │
    ├── [Secret] ────env──> ──────┘                                 │
    │                                                                │
    └── [Backend Service] ──routes to──> ───────────────────────────┘

[Namespace: taskflow]
    │
    ├── [ConfigMap] ──env──> [Frontend Deployment] ──creates──> [Frontend Pod]
    │                             │                                  │
    └── [Frontend Service] ──routes to──> ────────────────────────────┘
         (LoadBalancer)

[Docker Images]
    ├── taskflow-backend:latest ──used by──> [Backend Deployment]
    └── taskflow-frontend:latest ──used by──> [Frontend Deployment]
```

### Component 2: API Contracts (`contracts/`)

**Contract 1: Health Endpoint** (`contracts/health-endpoint.yaml`)

```yaml
openapi: 3.0.0
info:
  title: Backend Health Check
  version: 1.0.0
paths:
  /health:
    get:
      summary: Health check endpoint for Kubernetes probes
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [healthy]
                  timestamp:
                    type: string
                    format: date-time
                required:
                  - status
              example:
                status: healthy
                timestamp: "2026-02-03T10:30:00Z"
```

**Contract 2: Backend Deployment Specification** (`contracts/backend-deployment.yaml`)

```yaml
# Schema validation for backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: taskflow
  labels:
    app: taskflow-backend
    phase: "4"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: taskflow-backend
  template:
    metadata:
      labels:
        app: taskflow-backend
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: backend
        image: taskflow-backend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 7860
          name: fastapi
        - containerPort: 8001
          name: mcp
        envFrom:
        - configMapRef:
            name: taskflow-config
        - secretRef:
            name: taskflow-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "500Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 7860
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 7860
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 7860
          periodSeconds: 5
          failureThreshold: 30
```

**Contract 3: Frontend Deployment Specification** (`contracts/frontend-deployment.yaml`)

```yaml
# Schema validation for frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  namespace: taskflow
  labels:
    app: taskflow-frontend
    phase: "4"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: taskflow-frontend
  template:
    metadata:
      labels:
        app: taskflow-frontend
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: frontend
        image: taskflow-frontend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: taskflow-config
              key: NEXT_PUBLIC_API_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 20
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Component 3: Quickstart Guide (`quickstart.md`)

**Contents**:
1. **Prerequisites**:
   - Docker Desktop 4.0+ installed
   - Kubernetes enabled in Docker Desktop settings
   - kubectl CLI available (comes with Docker Desktop)
   - Git repository cloned
   - .env file configured with Neon DATABASE_URL, JWT_SECRET_KEY, OAuth credentials, OPENAI_API_KEY

2. **Quick Start (5 steps)**:
   ```bash
   # Step 1: Verify Kubernetes is running
   kubectl cluster-info
   kubectl get nodes  # Should show 1 node in Ready status

   # Step 2: Build Docker images (takes 5-8 minutes)
   bash scripts/build-images.sh

   # Step 3: Generate Kubernetes secrets from .env
   bash scripts/generate-secrets.sh

   # Step 4: Deploy to Kubernetes (takes 2-3 minutes)
   bash scripts/deploy-k8s.sh

   # Step 5: Access the application
   kubectl get svc -n taskflow frontend-service  # Get LoadBalancer IP
   # Open browser: http://localhost (or shown IP)
   ```

3. **Verification**:
   ```bash
   # Check pods are running
   kubectl get pods -n taskflow

   # Check logs
   kubectl logs -n taskflow -l app=taskflow-backend
   kubectl logs -n taskflow -l app=taskflow-frontend

   # Test backend health from within cluster
   kubectl exec -n taskflow <backend-pod> -- curl http://localhost:7860/health

   # Test frontend accessibility
   curl http://localhost  # Should return HTML
   ```

4. **Troubleshooting**:
   - Pod stuck in Pending: Check resources with `kubectl describe pod`
   - Pod stuck in ImagePullBackOff: Verify imagePullPolicy: Never, images exist locally
   - Pod crashing: Check logs with `kubectl logs`, describe pod for events
   - Health probes failing: Increase initialDelaySeconds, check /health endpoint works locally
   - LoadBalancer pending: On Docker Desktop, may take 30s, use `localhost` to access

5. **Cleanup**:
   ```bash
   kubectl delete namespace taskflow
   docker rmi taskflow-backend:latest taskflow-frontend:latest
   ```

---

## Phase 2: Implementation Roadmap

**Objective**: Break down the 27 components into 6 sequential phases for implementation.

### Phase A: Docker Image Preparation (Backend)

**Components**: 1-4
**Duration estimate**: 2-3 hours
**Dependencies**: None (can start immediately)

1. **Optimize Backend Dockerfile** (Component 1)
   - Create two-stage build: builder (UV sync) + runtime (copy .venv + source)
   - Add non-root user creation and USER directive
   - Configure health check and expose ports
   - Test build: `docker build -t taskflow-backend:latest .`

2. **Add Backend Health Endpoint** (Component 2)
   - Implement GET /health in src/interfaces/api.py
   - Return {"status": "healthy", "timestamp": "<ISO-8601>"}
   - Test locally: `curl http://localhost:7860/health`

3. **Create Backend Startup Script** (Component 3)
   - Write scripts/start-backend.sh
   - Start MCP server in background, wait 5s, start FastAPI
   - Handle SIGTERM for graceful shutdown
   - Make executable: `chmod +x scripts/start-backend.sh`

4. **Create .dockerignore (Backend)** (Component 4)
   - Exclude .git, node_modules, frontend/, tests/, __pycache__, .env
   - Test build size improvement

**Acceptance**:
- Backend image builds without errors in <5 minutes
- Image size <500MB
- Running container responds to /health with 200 OK
- Container runs as UID 1000 (verify with `docker run --rm taskflow-backend:latest id`)

### Phase B: Docker Image Preparation (Frontend)

**Components**: 5-7
**Duration estimate**: 2-3 hours
**Dependencies**: None (parallel with Phase A)

5. **Create Frontend Dockerfile** (Component 5)
   - Three-stage build: dependencies (npm ci) + builder (npm run build) + runner (copy standalone)
   - Add non-root user (nodejs UID 1000)
   - Copy .next/standalone, .next/static, public
   - Test build: `docker build -t taskflow-frontend:latest ./frontend`

6. **Configure Next.js Standalone** (Component 6)
   - Update frontend/next.config.js: `output: 'standalone'`
   - Test local build: `npm run build` creates .next/standalone

7. **Create .dockerignore (Frontend)** (Component 7)
   - Exclude node_modules, .next, .git, *.md
   - Test build size improvement

**Acceptance**:
- Frontend image builds without errors in <3 minutes
- Image size <300MB
- Running container serves homepage on port 3000
- Container runs as UID 1000

### Phase C: Kubernetes Manifests

**Components**: 8-14
**Duration estimate**: 3-4 hours
**Dependencies**: Phase A+B complete (images built)

8. **Create Namespace** (Component 8)
   - Write k8s/namespace.yaml
   - Apply: `kubectl apply -f k8s/namespace.yaml`

9. **Create ConfigMap** (Component 9)
   - Write k8s/configmap.yaml with non-sensitive config
   - Apply: `kubectl apply -f k8s/configmap.yaml`

10. **Create Secrets** (Component 10)
    - Write k8s/secrets.yaml with base64-encoded values
    - Mark as gitignored (never commit)
    - Apply: `kubectl apply -f k8s/secrets.yaml`

11. **Create Backend Deployment** (Component 11)
    - Write k8s/backend-deployment.yaml following contract
    - Include all probes, resource limits, security context
    - Apply: `kubectl apply -f k8s/backend-deployment.yaml`

12. **Create Backend Service** (Component 12)
    - Write k8s/backend-service.yaml (ClusterIP)
    - Apply: `kubectl apply -f k8s/backend-service.yaml`

13. **Create Frontend Deployment** (Component 13)
    - Write k8s/frontend-deployment.yaml following contract
    - Include probes, resource limits, security context
    - Apply: `kubectl apply -f k8s/frontend-deployment.yaml`

14. **Create Frontend Service** (Component 14)
    - Write k8s/frontend-service.yaml (LoadBalancer)
    - Apply: `kubectl apply -f k8s/frontend-service.yaml`

**Acceptance**:
- All manifests apply without errors
- Pods reach Running status within 2 minutes
- Backend service has ClusterIP assigned
- Frontend service has LoadBalancer IP (or localhost)
- Health probes pass (no restarts)

### Phase D: Helper Scripts & Documentation

**Components**: 15-18
**Duration estimate**: 2 hours
**Dependencies**: Phase C complete (manifests created)

15. **Create Build Script** (Component 15)
    - Write scripts/build-images.sh
    - Automate backend + frontend builds, show sizes
    - Make executable: `chmod +x scripts/build-images.sh`

16. **Create Deploy Script** (Component 16)
    - Write scripts/deploy-k8s.sh
    - Apply all manifests in order, wait for pods, show status
    - Make executable: `chmod +x scripts/deploy-k8s.sh`

17. **Create Secrets Generator** (Component 17)
    - Write scripts/generate-secrets.sh
    - Read .env, base64 encode, write k8s/secrets.yaml
    - Add warning comments, make executable

18. **Create Testing Guide** (Component 18)
    - Write docs/PHASE-IV-TESTING-GUIDE.md
    - Document prerequisites, build, deploy, verify, troubleshoot

**Acceptance**:
- All scripts executable and run without errors
- Build script completes in <10 minutes
- Deploy script creates all resources successfully
- Secrets generator produces valid YAML
- Testing guide clear and accurate

### Phase E: Helm Chart (Bonus)

**Components**: 19-22
**Duration estimate**: 3-4 hours
**Dependencies**: Phase C complete (manifests exist to templatize)

19. **Create Helm Chart Structure** (Component 19)
    - Run: `helm create helm/taskflow`
    - Clean up default files, keep structure

20. **Create Chart.yaml** (Component 20)
    - Define name, version, appVersion, description

21. **Create values.yaml** (Component 21)
    - Extract configurable values from manifests
    - Define backend/frontend images, replicas, resources

22. **Create Helm Templates** (Component 22)
    - Convert k8s/*.yaml to helm/taskflow/templates/*.yaml
    - Add Go templating: {{ .Values.backend.image }}
    - Create _helpers.tpl for common labels

**Acceptance**:
- `helm lint ./helm/taskflow` passes
- `helm install taskflow ./helm/taskflow` creates all resources
- `helm upgrade` works
- `helm uninstall` removes all resources cleanly

### Phase F: Integration & Testing

**Components**: 23-27
**Duration estimate**: 2-3 hours
**Dependencies**: Phase A-D complete (all components exist)

23. **Verify Local K8s Setup** (Component 23)
    - Check Docker Desktop, Kubernetes enabled, kubectl context

24. **Run Image Build Tests** (Component 24)
    - Test both images build, sizes correct, non-root users

25. **Run K8s Deployment Tests** (Component 25)
    - Test pods Running, probes passing, services created, LoadBalancer accessible

26. **Run End-to-End Tests** (Component 26)
    - Test Phase I console (uv run todo)
    - Test Phase II web UI via LoadBalancer
    - Test Phase III chatbot via LoadBalancer
    - Test OAuth, database, CRUD operations

27. **Update Documentation** (Component 27)
    - Update README.md with Phase IV section
    - Ensure PHASE-IV-TESTING-GUIDE.md complete
    - Update DEPLOYMENT.md with K8s instructions

**Acceptance**:
- All tests pass
- Documentation complete and accurate
- Phase I-III functionality verified unchanged
- Demo video created (90 seconds max)

---

## Implementation Dependencies

**Phase-level dependencies**:
```
Phase A (Backend Docker) ──┐
                           ├──> Phase C (K8s Manifests) ──> Phase D (Scripts) ──> Phase F (Testing)
Phase B (Frontend Docker) ─┘                                                      ↑
                                                                                   │
Phase E (Helm - Bonus) ────────────────────────────────────────────────────────────┘
```

**Critical path**: A/B → C → D → F (Phases A and B parallelizable)

**Estimated total time**: 14-19 hours (without Helm), 17-23 hours (with Helm bonus)

---

## Risk Mitigation

### Risk 1: Image Size Exceeds Limits
- **Mitigation**: Use multi-stage builds, .dockerignore, Alpine for frontend
- **Monitoring**: Check `docker images` after each build
- **Fallback**: Remove unnecessary dependencies, use distroless images

### Risk 2: Health Probes Fail Intermittently
- **Mitigation**: Tune initialDelaySeconds based on actual startup time, use startup probe
- **Monitoring**: `kubectl describe pod` shows probe failures
- **Fallback**: Increase timing values, simplify health check (remove DB check)

### Risk 3: Pods Exceed Resource Limits
- **Mitigation**: Monitor actual usage in development, set realistic limits with headroom
- **Monitoring**: `kubectl top pods -n taskflow` shows resource usage
- **Fallback**: Increase limits, optimize application memory usage

### Risk 4: Database Connection Issues from K8s
- **Mitigation**: Verify DATABASE_URL accessible from containers (test with curl/psql in pod)
- **Monitoring**: Backend logs show connection errors
- **Fallback**: Check firewall, Neon IP allowlist, connection string format

### Risk 5: Next.js Standalone Build Incomplete
- **Mitigation**: Verify .next/standalone contains server.js, copy all required folders
- **Monitoring**: Frontend logs show "Cannot find module" errors
- **Fallback**: Debug with `docker run -it --entrypoint sh` to inspect filesystem

---

## Deliverables Summary

**Phase 0 (Research)**:
- ✅ research.md (1 file)

**Phase 1 (Design)**:
- ✅ data-model.md (1 file)
- ✅ contracts/ (3 files: health-endpoint.yaml, backend-deployment.yaml, frontend-deployment.yaml)
- ✅ quickstart.md (1 file)
- ✅ Agent context update (automatic)

**Phase 2 (Tasks)**:
- Deferred to /sp.tasks command

**Total artifacts created by /sp.plan**: 6 files (research.md, data-model.md, quickstart.md, 3 contracts)

---

## Next Steps

1. **Execute /sp.tasks**: Generate implementation tasks from this plan
2. **Implement Phase A-B**: Build Docker images
3. **Implement Phase C**: Create Kubernetes manifests
4. **Implement Phase D**: Automate with scripts
5. **Implement Phase E** (optional): Create Helm chart
6. **Implement Phase F**: Test end-to-end
7. **Demo**: Record 90-second video, submit via form

**Plan Status**: ✅ COMPLETE - Ready for /sp.tasks command
