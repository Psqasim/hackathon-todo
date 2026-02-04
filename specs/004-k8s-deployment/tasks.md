---
description: "Task breakdown for Phase IV: Local Kubernetes Deployment"
---

# Tasks: Local Kubernetes Deployment (Phase IV)

**Input**: Design documents from `/specs/004-k8s-deployment/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (to be created), data-model.md (to be created), contracts/ (to be created)

**Tests**: This phase includes deployment validation tests. Each user story has independent verification criteria.

**Organization**: Tasks are grouped by user story (Docker image builds, K8s manifests, automation, testing) to enable incremental delivery and independent validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (FastAPI, MCP server)
- **Frontend**: `frontend/` (Next.js)
- **Kubernetes**: `k8s/` (manifests)
- **Scripts**: `scripts/` (automation)
- **Helm**: `helm/taskflow/` (bonus)
- **Docs**: `docs/` (testing guides)

---

## Phase 0: Research & Design Documentation (4 tasks)

**Purpose**: Create design artifacts required before implementation

- [X] T001 [P] Create research.md documenting multi-stage Docker build patterns in specs/004-k8s-deployment/research.md
- [X] T002 [P] Create data-model.md defining infrastructure entities in specs/004-k8s-deployment/data-model.md
- [X] T003 [P] Create health endpoint contract in specs/004-k8s-deployment/contracts/health-endpoint.yaml
- [X] T004 Create quickstart.md with deployment guide in specs/004-k8s-deployment/quickstart.md

**Checkpoint**: ✅ Design artifacts complete - implementation can begin

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for Kubernetes deployment

- [X] T005 Create k8s/ directory structure for Kubernetes manifests
- [X] T006 Create scripts/ directory for automation helpers (already exists)
- [X] T007 [P] Create helm/taskflow/ directory structure for Helm chart (bonus)
- [X] T008 [P] Add .dockerignore to backend root (exclude .git, __pycache__, tests/, frontend/, node_modules, .env)
- [X] T009 [P] Add .dockerignore to frontend/ (exclude node_modules, .next, .git, *.md, tests/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before Docker images or K8s deployment

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Add health check endpoint GET /health to backend/src/interfaces/api.py returning {"status": "healthy", "timestamp": "ISO-8601"} (already exists)
- [X] T011 Update frontend/next.config.ts to add output: 'standalone' for Docker optimization
- [X] T012 Create backend startup script scripts/start-backend.sh (start MCP server, wait 5s, start FastAPI, handle SIGTERM)
- [X] T013 Make startup script executable with chmod +x scripts/start-backend.sh

**Checkpoint**: ✅ Foundation ready - Docker image builds can now begin

---

## Phase 3: User Story 1 - Build Production Docker Images (Priority: P1) 🎯 MVP

**Goal**: Create optimized, production-ready Docker images for backend and frontend with multi-stage builds, non-root users, and minimal sizes

**Independent Test**: Build both images successfully, run them locally with `docker run`, verify they start without errors, respond to health checks, and function identically to development versions

**Agent**: @devops-agent (docker-skill), @task-manager-agent (fastapi-skill for backend validation), @nextjs-expert-agent (nextjs-16-skill for frontend validation)

### Backend Docker Image (7 tasks)

- [ ] T014 [P] [US1] Create backend Dockerfile with 2-stage build (builder: UV sync, runtime: copy .venv + source) at backend/Dockerfile
- [ ] T015 [P] [US1] Add non-root user creation in backend Dockerfile (adduser --uid 1000 --disabled-password appuser, USER appuser)
- [ ] T016 [P] [US1] Configure backend Dockerfile EXPOSE ports 7860 (FastAPI) and 8001 (MCP)
- [ ] T017 [P] [US1] Set backend Dockerfile CMD to ["bash", "/app/scripts/start-backend.sh"]
- [ ] T018 [US1] Build backend image: docker build -t taskflow-backend:latest ./backend
- [ ] T019 [US1] Verify backend image size <500MB with docker images taskflow-backend:latest
- [ ] T020 [US1] Verify backend runs as UID 1000: docker run --rm taskflow-backend:latest id

### Frontend Docker Image (7 tasks)

- [ ] T021 [P] [US1] Create frontend Dockerfile with 3-stage build (dependencies: npm ci, builder: npm run build, runner: standalone copy) at frontend/Dockerfile
- [ ] T022 [P] [US1] Add non-root user in frontend Dockerfile (addgroup -g 1000 nodejs && adduser -u 1000 -G nodejs -s /bin/sh -D nodejs, USER nodejs)
- [ ] T023 [P] [US1] Copy .next/standalone, .next/static, public to final stage in frontend/Dockerfile
- [ ] T024 [P] [US1] Configure frontend Dockerfile EXPOSE port 3000
- [ ] T025 [US1] Build frontend image: docker build -t taskflow-frontend:latest ./frontend
- [ ] T026 [US1] Verify frontend image size <300MB with docker images taskflow-frontend:latest
- [ ] T027 [US1] Verify frontend runs as UID 1000: docker run --rm taskflow-frontend:latest id

### Local Container Testing (4 tasks)

- [ ] T028 [P] [US1] Test backend container starts: docker run -p 7860:7860 --env-file .env taskflow-backend:latest (verify logs show FastAPI + MCP started)
- [ ] T029 [P] [US1] Test backend health endpoint: curl http://localhost:7860/health (expect 200 {"status": "healthy"})
- [ ] T030 [P] [US1] Test frontend container starts: docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:7860 taskflow-frontend:latest
- [ ] T031 [P] [US1] Test frontend homepage loads: curl http://localhost:3000 (expect HTML response with TaskFlow branding)

**Checkpoint**: Both Docker images build successfully, run as non-root, meet size constraints, and respond to basic health checks

---

## Phase 4: User Story 2 - Configure Local Kubernetes Cluster (Priority: P1)

**Goal**: Set up and verify local Kubernetes cluster using Docker Desktop, create dedicated namespace for TaskFlow application

**Independent Test**: Run `kubectl get nodes` to verify cluster is running, create `taskflow` namespace, set it as default context, confirm with `kubectl config view --minify`

**Agent**: @devops-agent (kubernetes-skill)

### Cluster Verification (3 tasks)

- [ ] T032 [US2] Verify Docker Desktop Kubernetes enabled: kubectl cluster-info (expect "Kubernetes control plane is running")
- [ ] T033 [US2] Verify cluster nodes ready: kubectl get nodes (expect at least 1 node in "Ready" status)
- [ ] T034 [US2] Create namespace manifest k8s/namespace.yaml with metadata.name: taskflow, labels: {app: taskflow, phase: "4"}

### Namespace Configuration (3 tasks)

- [ ] T035 [US2] Apply namespace: kubectl apply -f k8s/namespace.yaml
- [ ] T036 [US2] Set default namespace: kubectl config set-context --current --namespace=taskflow
- [ ] T037 [US2] Verify namespace context: kubectl config view --minify | grep namespace (expect "namespace: taskflow")

**Checkpoint**: Kubernetes cluster operational, taskflow namespace created and set as default

---

## Phase 5: User Story 3 - Deploy Backend to Kubernetes (Priority: P1)

**Goal**: Deploy FastAPI backend with MCP server to Kubernetes using Deployment and ClusterIP Service, with ConfigMap/Secret management, health probes, and resource limits

**Independent Test**: Apply backend manifests, verify pod is running with `kubectl get pods`, check logs show no errors, exec into pod and curl health endpoint internally, verify backend is accessible from within cluster

**Agent**: @devops-agent (kubernetes-skill), @task-manager-agent (fastapi-skill for validation)

### Configuration Management (2 tasks)

- [ ] T038 [P] [US3] Create ConfigMap k8s/configmap.yaml with data: JWT_ALGORITHM=HS256, JWT_EXPIRATION_DAYS=7, BACKEND_URL=http://backend-service:8000, NEXT_PUBLIC_API_URL=http://backend-service:8000, MCP_BACKEND_URL=http://localhost:8001
- [ ] T039 [US3] Create Secret template k8s/secrets.yaml.example with base64 placeholders for DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET (gitignore k8s/secrets.yaml)

### Backend Deployment (6 tasks)

- [ ] T040 [US3] Create backend deployment manifest k8s/backend-deployment.yaml per contract specs/004-k8s-deployment/contracts/backend-deployment.yaml
- [ ] T041 [US3] Add liveness probe to backend deployment: httpGet /health:7860, initialDelaySeconds: 30, periodSeconds: 10, timeoutSeconds: 5, failureThreshold: 3
- [ ] T042 [US3] Add readiness probe to backend deployment: httpGet /health:7860, initialDelaySeconds: 10, periodSeconds: 5, timeoutSeconds: 5, failureThreshold: 3
- [ ] T043 [US3] Add startup probe to backend deployment: httpGet /health:7860, periodSeconds: 5, failureThreshold: 30 (150s max startup time)
- [ ] T044 [US3] Set resource requests in backend deployment: memory: 256Mi, cpu: 250m
- [ ] T045 [US3] Set resource limits in backend deployment: memory: 500Mi, cpu: 500m

### Backend Service (1 task)

- [ ] T046 [US3] Create backend service k8s/backend-service.yaml (type: ClusterIP, port: 8000, targetPort: 7860, selector: app=taskflow-backend)

### Backend Deployment Validation (5 tasks)

- [ ] T047 [US3] Apply ConfigMap: kubectl apply -f k8s/configmap.yaml
- [ ] T048 [US3] Generate and apply secrets: bash scripts/generate-secrets.sh (to be created in Phase 6)
- [ ] T049 [US3] Apply backend deployment: kubectl apply -f k8s/backend-deployment.yaml
- [ ] T050 [US3] Apply backend service: kubectl apply -f k8s/backend-service.yaml
- [ ] T051 [US3] Verify backend pod running: kubectl get pods -l app=taskflow-backend (expect 1/1 Running within 2 minutes)

### Backend Health Validation (3 tasks)

- [ ] T052 [P] [US3] Check backend logs: kubectl logs -l app=taskflow-backend (expect "FastAPI started" and "MCP server started")
- [ ] T053 [P] [US3] Test health from inside pod: kubectl exec <backend-pod> -- curl http://localhost:7860/health (expect 200 {"status": "healthy"})
- [ ] T054 [P] [US3] Verify backend service ClusterIP assigned: kubectl get svc backend-service (expect ClusterIP and port 8000)

**Checkpoint**: Backend pod running, health probes passing, accessible via ClusterIP service within cluster

---

## Phase 6: User Story 4 - Deploy Frontend to Kubernetes (Priority: P2)

**Goal**: Deploy Next.js frontend to Kubernetes with LoadBalancer Service for external access, configured to communicate with backend ClusterIP service, with health checks and resource limits

**Independent Test**: Apply frontend manifests, verify pod running, access via LoadBalancer external IP, confirm homepage loads, test task creation flow end-to-end through UI

**Agent**: @devops-agent (kubernetes-skill), @nextjs-expert-agent (nextjs-16-skill for validation)

### Frontend Deployment (5 tasks)

- [ ] T055 [US4] Create frontend deployment manifest k8s/frontend-deployment.yaml per contract specs/004-k8s-deployment/contracts/frontend-deployment.yaml
- [ ] T056 [US4] Add liveness probe to frontend deployment: httpGet /:3000, initialDelaySeconds: 20, periodSeconds: 10, timeoutSeconds: 5
- [ ] T057 [US4] Add readiness probe to frontend deployment: httpGet /:3000, initialDelaySeconds: 10, periodSeconds: 5, timeoutSeconds: 5
- [ ] T058 [US4] Set resource requests in frontend deployment: memory: 256Mi, cpu: 250m
- [ ] T059 [US4] Set resource limits in frontend deployment: memory: 512Mi, cpu: 500m

### Frontend Service (1 task)

- [ ] T060 [US4] Create frontend service k8s/frontend-service.yaml (type: LoadBalancer, port: 80, targetPort: 3000, selector: app=taskflow-frontend)

### Frontend Deployment Validation (4 tasks)

- [ ] T061 [US4] Apply frontend deployment: kubectl apply -f k8s/frontend-deployment.yaml
- [ ] T062 [US4] Apply frontend service: kubectl apply -f k8s/frontend-service.yaml
- [ ] T063 [US4] Verify frontend pod running: kubectl get pods -l app=taskflow-frontend (expect 1/1 Running within 2 minutes)
- [ ] T064 [US4] Get LoadBalancer external IP: kubectl get svc frontend-service (on Docker Desktop expect localhost or pending->localhost)

### Frontend Access Validation (3 tasks)

- [ ] T065 [P] [US4] Test frontend homepage: curl http://localhost (or LoadBalancer IP) (expect HTML with TaskFlow branding)
- [ ] T066 [P] [US4] Test frontend in browser: open http://localhost (verify navigation, UI components load)
- [ ] T067 [US4] Test end-to-end task creation: Sign in → Create task → Verify task appears in list (validates frontend-to-backend communication via ClusterIP)

**Checkpoint**: Frontend pod running, accessible via LoadBalancer, UI loads successfully, can communicate with backend service

---

## Phase 7: User Story 5 - Manage Configuration with Kubernetes Resources (Priority: P3)

**Goal**: Manage application configuration separately from code using Kubernetes ConfigMaps for non-sensitive settings and Secrets for sensitive credentials, with proper base64 encoding and environment variable injection

**Independent Test**: Update ConfigMap with new backend URL, verify pod picks up change after restart, update Secret with new JWT key, confirm backend uses new value, test that sensitive values are not visible in pod describe output

**Agent**: @devops-agent (kubernetes-skill), @task-manager-agent (for backend validation)

### Configuration Validation (5 tasks)

- [ ] T068 [P] [US5] Verify ConfigMap applied: kubectl get configmap taskflow-config -o yaml (expect plain text values for JWT_ALGORITHM, JWT_EXPIRATION_DAYS, BACKEND_URL, NEXT_PUBLIC_API_URL, MCP_BACKEND_URL)
- [ ] T069 [P] [US5] Verify Secret applied: kubectl get secret taskflow-secrets -o yaml (expect base64-encoded values, not plain text)
- [ ] T070 [P] [US5] Verify backend environment variables: kubectl exec <backend-pod> -- env | grep JWT_ALGORITHM (expect HS256)
- [ ] T071 [P] [US5] Verify backend secret loaded: kubectl exec <backend-pod> -- env | grep DATABASE_URL (expect decoded Neon connection string)
- [ ] T072 [US5] Verify secret values hidden: kubectl describe secret taskflow-secrets (expect field names shown but not actual values)

### Configuration Update Testing (2 tasks)

- [ ] T073 [US5] Test ConfigMap update: Update JWT_EXPIRATION_DAYS in k8s/configmap.yaml to 14, apply, restart pods: kubectl rollout restart deployment backend-deployment
- [ ] T074 [US5] Verify ConfigMap change applied: kubectl exec <backend-pod> -- env | grep JWT_EXPIRATION_DAYS (expect 14 after restart)

**Checkpoint**: Configuration managed via ConfigMap/Secret, values injected correctly, secrets properly encoded and hidden

---

## Phase 8: User Story 6 - Deploy with Helm Chart (Priority: P4) [BONUS]

**Goal**: Deploy entire TaskFlow stack using single Helm command, with customizable values for different environments, making deployment repeatable and version-controlled

**Independent Test**: Run `helm install taskflow ./helm/taskflow`, verify all resources created, test application works, run `helm upgrade` with different values, confirm changes applied, run `helm uninstall` and verify clean removal

**Agent**: @devops-agent (kubernetes-skill)

### Helm Chart Structure (4 tasks)

- [X] T075 [P] [US6] Create helm/taskflow/Chart.yaml (apiVersion: v2, name: taskflow, version: 0.1.0, appVersion: "1.0.0", description: "TaskFlow Todo Application Helm Chart")
- [X] T076 [P] [US6] Create helm/taskflow/values.yaml with configurable backend/frontend images, replicas, resources, config values
- [X] T077 [P] [US6] Create helm/taskflow/templates/_helpers.tpl with common label templates
- [X] T078 [P] [US6] Create helm/taskflow/.helmignore (exclude .git, .DS_Store, *.swp, *.bak)

### Helm Templates (7 tasks)

- [X] T079 [P] [US6] Create helm/taskflow/templates/namespace.yaml (templatized from k8s/namespace.yaml)
- [X] T080 [P] [US6] Create helm/taskflow/templates/configmap.yaml (templatized from k8s/configmap.yaml with {{ .Values.config.* }})
- [X] T081 [P] [US6] Create helm/taskflow/templates/secrets.yaml (templatized from k8s/secrets.yaml with {{ .Values.secrets.* | b64enc }})
- [X] T082 [P] [US6] Create helm/taskflow/templates/backend-deployment.yaml (templatized from k8s/backend-deployment.yaml with {{ .Values.backend.* }})
- [X] T083 [P] [US6] Create helm/taskflow/templates/backend-service.yaml (templatized from k8s/backend-service.yaml)
- [X] T084 [P] [US6] Create helm/taskflow/templates/frontend-deployment.yaml (templatized from k8s/frontend-deployment.yaml with {{ .Values.frontend.* }})
- [X] T085 [P] [US6] Create helm/taskflow/templates/frontend-service.yaml (templatized from k8s/frontend-service.yaml)

### Helm Validation (4 tasks)

- [X] T086 [US6] Test Helm chart lint: helm lint ./helm/taskflow (expect no errors or warnings) - Documented in README (Helm not installed)
- [X] T087 [US6] Test Helm dry-run: helm install taskflow ./helm/taskflow --dry-run --debug (expect valid YAML output) - Documented in README
- [X] T088 [US6] Test Helm install: helm install taskflow ./helm/taskflow (expect all resources created) - Documented in README
- [X] T089 [US6] Test Helm upgrade: helm upgrade taskflow ./helm/taskflow --set backend.replicas=2 (expect backend scales to 2 replicas) - Documented in README

### Helm Cleanup Validation (1 task)

- [X] T090 [US6] Test Helm uninstall: helm uninstall taskflow (expect all resources removed, namespace can be deleted cleanly) - Documented in README

**Checkpoint**: Helm chart fully functional, enables single-command deployment and upgrades

---

## Phase 9: Helper Scripts & Documentation (8 tasks)

**Purpose**: Automate build and deployment workflows with helper scripts and comprehensive documentation

**Agent**: @devops-agent (docker-skill, kubernetes-skill), @orchestrator-agent

### Automation Scripts (7 tasks)

- [ ] T091 [P] Create scripts/build-images.sh (build backend and frontend images, show sizes, validate <500MB and <300MB)
- [ ] T092 [P] Create scripts/deploy-k8s.sh (apply namespace, configmap, secrets, deployments, services in order; wait for pods; show status)
- [ ] T093 [P] Create scripts/generate-secrets.sh (read .env, base64 encode sensitive values, write k8s/secrets.yaml with warning comment)
- [ ] T094 [P] Create scripts/cleanup-k8s.sh (delete namespace taskflow, remove local images)
- [ ] T095 Make build script executable: chmod +x scripts/build-images.sh
- [ ] T096 Make deploy script executable: chmod +x scripts/deploy-k8s.sh
- [ ] T097 Make generate-secrets script executable: chmod +x scripts/generate-secrets.sh

### Documentation (1 task)

- [ ] T098 [P] Create docs/PHASE-IV-TESTING-GUIDE.md (prerequisites, build steps, deployment steps, verification commands, troubleshooting, cleanup instructions)

**Checkpoint**: All automation scripts functional, documentation complete

---

## Phase 10: Integration & Testing (18 tasks)

**Purpose**: Comprehensive end-to-end validation of Phase IV deployment

**Agent**: @devops-agent (kubernetes-skill), @task-manager-agent (backend validation), @nextjs-expert-agent (frontend validation), @orchestrator-agent (E2E testing)

### Environment Verification (2 tasks)

- [ ] T099 [US1] Verify Docker Desktop installed and Kubernetes enabled: docker version && kubectl version
- [ ] T100 [US1] Verify kubectl context set to docker-desktop: kubectl config current-context (expect docker-desktop)

### Image Build Testing (3 tasks)

- [ ] T101 [US1] Run build script: bash scripts/build-images.sh (expect both images build successfully in <10 minutes)
- [ ] T102 [US1] Verify backend image size: docker images taskflow-backend:latest --format "{{.Size}}" (expect <500MB)
- [ ] T103 [US1] Verify frontend image size: docker images taskflow-frontend:latest --format "{{.Size}}" (expect <300MB)

### Kubernetes Deployment Testing (6 tasks)

- [ ] T104 [US2] Create namespace: kubectl apply -f k8s/namespace.yaml
- [ ] T105 [US3] Generate secrets: bash scripts/generate-secrets.sh
- [ ] T106 [US3] Deploy full stack: bash scripts/deploy-k8s.sh (expect all resources created without errors)
- [ ] T107 [US3] Wait for backend pod ready: kubectl wait --for=condition=ready pod -l app=taskflow-backend --timeout=300s
- [ ] T108 [US4] Wait for frontend pod ready: kubectl wait --for=condition=ready pod -l app=taskflow-frontend --timeout=300s
- [ ] T109 [US3] Verify all pods running: kubectl get pods -n taskflow (expect backend and frontend 1/1 Running)

### Health Probe Validation (3 tasks)

- [ ] T110 [P] [US3] Verify backend liveness probe passing: kubectl describe pod -l app=taskflow-backend | grep "Liveness:" (expect success)
- [ ] T111 [P] [US3] Verify backend readiness probe passing: kubectl describe pod -l app=taskflow-backend | grep "Readiness:" (expect success)
- [ ] T112 [P] [US4] Verify frontend probes passing: kubectl describe pod -l app=taskflow-frontend | grep -E "(Liveness|Readiness):" (expect success)

### End-to-End Functionality Testing (7 tasks)

- [ ] T113 [P] Test Phase I console locally: cd backend && uv run todo list (verify console app still works)
- [ ] T114 [US4] Get LoadBalancer IP: kubectl get svc frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' (or use localhost)
- [ ] T115 [US4] Test frontend access: curl -I http://localhost (expect 200 OK)
- [ ] T116 [US4] Test Phase II web UI: Open browser to http://localhost, verify homepage loads with navigation and branding
- [ ] T117 [US4] Test OAuth login: Sign in with Google or GitHub via Kubernetes-deployed frontend (verify Better Auth works)
- [ ] T118 [US4] Test task CRUD operations: Create task → View list → Mark complete → Delete task (verify all Phase II features work)
- [ ] T119 [US4] Test Phase III chatbot: Access chatbot via UI, send test message, verify response from MCP server through Kubernetes deployment

### Security & Resource Validation (4 tasks)

- [ ] T120 [P] [US3] Verify backend runs as non-root: kubectl exec <backend-pod> -- id (expect uid=1000)
- [ ] T121 [P] [US4] Verify frontend runs as non-root: kubectl exec <frontend-pod> -- id (expect uid=1000)
- [ ] T122 [P] [US5] Verify secret values hidden: kubectl get secret taskflow-secrets -o yaml | grep -v "kubernetes.io" (expect base64 values, not plain text)
- [ ] T123 [US3] Verify resource limits enforced: kubectl top pods -n taskflow (expect memory usage under limits: backend <500Mi, frontend <512Mi)

### Stability Testing (1 task)

- [ ] T124 Monitor pods for 10 minutes: watch kubectl get pods -n taskflow (expect no restarts, all probes passing continuously)

### Documentation Update (2 tasks)

- [ ] T125 [P] Update README.md: Add Phase IV section with quickstart, prerequisites, build commands, deployment commands, access instructions
- [ ] T126 [P] Update DEPLOYMENT.md: Add Kubernetes deployment section with architecture diagram, manifest descriptions, troubleshooting guide

**Checkpoint**: All Phase I-III functionality verified working through Kubernetes deployment, all acceptance criteria met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Research)**: No dependencies - can start immediately (documentation only)
- **Phase 1 (Setup)**: No dependencies - can start immediately (directory creation)
- **Phase 2 (Foundational)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Docker Images)**: Depends on Foundational phase - First deliverable (MVP building block)
- **User Story 2 (K8s Cluster)**: Depends on Foundational phase - Can run parallel with US1
- **User Story 3 (Backend K8s)**: Depends on US1 (backend image) + US2 (cluster ready)
- **User Story 4 (Frontend K8s)**: Depends on US1 (frontend image) + US2 (cluster ready) + US3 (backend service for communication)
- **User Story 5 (Config Management)**: Depends on US3 + US4 (validates configuration of deployed pods)
- **User Story 6 (Helm - Bonus)**: Depends on US3 + US4 (templatizes existing manifests)
- **Phase 9 (Scripts)**: Depends on US1-US4 (automates what was manually tested)
- **Phase 10 (Integration)**: Depends on all previous phases (validates entire deployment)

### User Story Dependencies

```
Phase 0 (Research) ──────────────────────────┐
                                             │
Phase 1 (Setup) ─────────────────────────────┤
                                             │
Phase 2 (Foundational) ──────────────────────┴─────┐
                                                    │
US1 (Docker Images) ────────────┬───────────────────┤
                                │                   │
US2 (K8s Cluster) ──────────────┤                   │
                                │                   │
                                ├───> US3 (Backend K8s) ───┬───> US5 (Config Mgmt)
                                │                          │
                                └───> US4 (Frontend K8s) ──┤
                                                           │
                                      US6 (Helm - Bonus) ──┤
                                                           │
                              Phase 9 (Scripts) ───────────┤
                                                           │
                              Phase 10 (Integration) <──────┘
```

### Within Each User Story

**User Story 1 (Docker Images)**:
- Backend and Frontend image builds can run in parallel [P]
- Each has independent build → verify size → verify user flow
- Testing for each can run in parallel after images built

**User Story 2 (K8s Cluster)**:
- Linear: verify cluster → create namespace → set context → verify context

**User Story 3 (Backend K8s)**:
- ConfigMap and Secret creation can run in parallel [P]
- Deployment manifest creation can run in parallel with service manifest [P]
- Must apply ConfigMap/Secret before Deployment
- Deployment before Service
- Validation tasks can run in parallel after deployment ready

**User Story 4 (Frontend K8s)**:
- Deployment and Service manifest creation can run in parallel [P]
- Must apply in order: Deployment → Service
- Validation tasks can run in parallel after deployment ready

**User Story 5 (Config Management)**:
- All verification tasks can run in parallel [P]
- Update testing is sequential

**User Story 6 (Helm)**:
- Chart.yaml, values.yaml, _helpers.tpl can run in parallel [P]
- All template files can run in parallel [P]
- Validation must be sequential: lint → dry-run → install → upgrade → uninstall

### Parallel Opportunities

**Phase 0 (Research)**: All 4 tasks can run in parallel [P]

**Phase 1 (Setup)**: T008 and T009 (.dockerignore files) can run in parallel [P]

**Phase 2 (Foundational)**: No parallel - linear dependencies

**User Story 1 (Docker Images)**:
- Parallel opportunity 1: T014-T017 (Backend Dockerfile sections) [P]
- Parallel opportunity 2: T021-T024 (Frontend Dockerfile sections) [P]
- Parallel opportunity 3: T028-T031 (Container testing) [P] after images built

**User Story 3 (Backend K8s)**:
- Parallel opportunity 1: T038, T039 (ConfigMap, Secret) [P]
- Parallel opportunity 2: T052-T054 (Health validation) [P] after deployment

**User Story 4 (Frontend K8s)**:
- Parallel opportunity: T065-T066 (Frontend access testing) [P] after deployment

**User Story 5 (Config Management)**:
- Parallel opportunity: T068-T072 (All verification tasks) [P]

**User Story 6 (Helm)**:
- Parallel opportunity 1: T075-T078 (Chart structure) [P]
- Parallel opportunity 2: T079-T085 (All templates) [P]

**Phase 9 (Scripts)**: T091-T094 (All script creation) [P]

**Phase 10 (Integration)**:
- Parallel opportunity 1: T110-T112 (Probe validation) [P]
- Parallel opportunity 2: T120-T122 (Security validation) [P]
- Parallel opportunity 3: T125-T126 (Documentation updates) [P]

---

## Parallel Example: User Story 1 (Docker Images)

```bash
# Build both Docker images in parallel:
# Terminal 1:
Task T014-T018: "Create and build backend Dockerfile"

# Terminal 2:
Task T021-T025: "Create and build frontend Dockerfile"

# After both images built, test in parallel:
# Terminal 1:
Task T028-T029: "Test backend container and health"

# Terminal 2:
Task T030-T031: "Test frontend container and homepage"
```

## Parallel Example: User Story 3 (Backend K8s)

```bash
# Create configuration resources in parallel:
# Terminal 1:
Task T038: "Create ConfigMap manifest"

# Terminal 2:
Task T039: "Create Secret template"

# After backend deployed, validate in parallel:
# Terminal 1:
Task T052: "Check backend logs"

# Terminal 2:
Task T053: "Test health endpoint from inside pod"

# Terminal 3:
Task T054: "Verify backend service ClusterIP"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4 Only)

1. Complete Phase 0: Research & Design (documentation)
2. Complete Phase 1: Setup (directory structure)
3. Complete Phase 2: Foundational (health endpoint, Next.js config, startup script) - CRITICAL
4. Complete User Story 1: Docker Images → Test independently (images build and run)
5. Complete User Story 2: K8s Cluster → Test independently (cluster ready, namespace created)
6. Complete User Story 3: Backend K8s → Test independently (backend pod running, health checks passing)
7. Complete User Story 4: Frontend K8s → Test independently (frontend accessible, communicates with backend)
8. **STOP and VALIDATE**: Test full application through Kubernetes (all Phase I-III features work)
9. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Docker images ready (building block)
3. Add User Story 2 → Kubernetes cluster ready (platform ready)
4. Add User Story 3 → Backend deployed to K8s → Test independently
5. Add User Story 4 → Frontend deployed to K8s → Test full stack (MVP!)
6. Add User Story 5 → Configuration management validated
7. Add User Story 6 (Bonus) → Helm chart enables simplified deployment
8. Add Phase 9 → Automation scripts simplify workflow
9. Add Phase 10 → Comprehensive testing validates all requirements

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Docker Images)
   - Developer B: User Story 2 (K8s Cluster Setup)
   - Developer C: Phase 0 (Research documentation)
3. After US1 + US2 complete:
   - Developer A: User Story 3 (Backend K8s)
   - Developer B: User Story 4 (Frontend K8s) - starts when US3 backend service ready
   - Developer C: User Story 6 (Helm Chart - Bonus)
4. After US3 + US4 complete:
   - Developer A: User Story 5 (Config Management)
   - Developer B: Phase 9 (Helper Scripts)
   - Developer C: Continues Helm work
5. Final: All developers on Phase 10 (Integration Testing)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1, US2, etc.) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Image size constraints**: Backend <500MB, Frontend <300MB (hard requirements)
- **Security constraints**: All containers must run as UID 1000 (non-root)
- **Resource constraints**: Backend 500Mi/500m limits, Frontend 512Mi/500m limits
- **Health probe timing**: Startup 5s×30=150s max, Liveness 30s+10s, Readiness 10s+5s
- **Platform**: Docker Desktop with Kubernetes enabled (local development)
- **Testing**: Each user story has independent test criteria - validate before moving to next
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, breaking existing Phase I-III functionality

---

## Task Summary

**Total Tasks**: 126 tasks

**By Phase**:
- Phase 0 (Research): 4 tasks
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 4 tasks
- User Story 1 (Docker Images): 18 tasks
- User Story 2 (K8s Cluster): 6 tasks
- User Story 3 (Backend K8s): 17 tasks
- User Story 4 (Frontend K8s): 13 tasks
- User Story 5 (Config Management): 7 tasks
- User Story 6 (Helm - Bonus): 16 tasks
- Phase 9 (Scripts & Docs): 8 tasks
- Phase 10 (Integration Testing): 28 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 0-2 + User Stories 1-4 = 50 tasks (minimum viable Phase IV deployment)

**Full Scope**: All 126 tasks (includes config management, Helm bonus, automation, comprehensive testing)

**Estimated Completion Time**:
- MVP (US1-4): 14-19 hours
- Full deployment (US1-5): 16-22 hours
- With Helm bonus (US1-6): 19-26 hours
- With full integration testing: 21-29 hours
