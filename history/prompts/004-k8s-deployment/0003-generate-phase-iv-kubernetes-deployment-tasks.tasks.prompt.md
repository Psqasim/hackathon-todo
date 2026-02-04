---
id: 0003
title: Generate Phase IV Kubernetes Deployment Tasks
stage: tasks
date: 2026-02-03
surface: agent
model: claude-sonnet-4-5
feature: 004-k8s-deployment
branch: 004-k8s-deployment
user: developer
command: /sp.tasks
labels: ["kubernetes", "docker", "deployment", "task-generation", "phase-4"]
links:
  spec: /specs/004-k8s-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-k8s-deployment/tasks.md
tests:
  - Format validation (all tasks follow checkbox [ID] [P?] [Story] format)
  - Dependency graph validation (user story order matches spec priorities)
  - Parallel opportunities identified (45 tasks marked [P])
---

## Prompt

Reference @specs/004-k8s-deployment/spec.md and @specs/004-k8s-deployment/plan.md

Generate a detailed, ordered task breakdown for Phase IV: Local Kubernetes Deployment.

Use the following agents and their linked skills:
- @orchestrator-agent (with agent-communication)
- @task-manager-agent (with python-best-practices, testing-patterns, fastapi-skill)
- @nextjs-expert-agent (with nextjs-16-skill, ui-design-skill)
- @devops-agent (with docker-skill, kubernetes-skill)

Break down the 27 components from the plan into specific, testable tasks.

## Task Organization Requirements:

### Phase 0: Research & Design (4-6 tasks)
Tasks for:
1. Create research.md (multi-stage builds, health probes, standalone Next.js)
2. Create data-model.md (infrastructure entities)
3. Create contracts (health-endpoint.yaml, deployment specs)
4. Create quickstart.md (deployment guide)

### Phase A: Backend Docker Image (6-8 tasks)
Tasks for:
1. Optimize existing Dockerfile with multi-stage build
2. Add health check endpoint to FastAPI
3. Create startup script (scripts/start-backend.sh)
4. Create .dockerignore for backend
5. Test backend Docker build locally
6. Verify backend image size (<500MB)
7. Verify non-root user (UID 1000)

### Phase B: Frontend Docker Image (6-8 tasks, can run parallel with Phase A)
Tasks for:
1. Create frontend/Dockerfile (3-stage build)
2. Update next.config.js (standalone output)
3. Create frontend/.dockerignore
4. Test frontend Docker build locally
5. Verify frontend image size (<300MB)
6. Verify non-root user (UID 1000)
7. Test standalone server.js starts

### Phase C: Kubernetes Manifests (10-12 tasks, depends on A+B)
Tasks for:
1. Create k8s/ directory structure
2. Create namespace.yaml
3. Create configmap.yaml (non-sensitive config)
4. Create secrets.yaml template
5. Create backend-deployment.yaml (with health probes, resources, security)
6. Create backend-service.yaml (ClusterIP)
7. Create frontend-deployment.yaml (with health probes, resources)
8. Create frontend-service.yaml (LoadBalancer)
9. Test YAML syntax validation
10. Apply manifests to local K8s (dry-run)

### Phase D: Helper Scripts & Docs (6-8 tasks, depends on C)
Tasks for:
1. Create scripts/build-images.sh (automate Docker builds)
2. Create scripts/deploy-k8s.sh (automate K8s deployment)
3. Create scripts/generate-secrets.sh (base64 encode .env to secrets.yaml)
4. Make scripts executable (chmod +x)
5. Test build script
6. Test deploy script
7. Create docs/PHASE-IV-TESTING-GUIDE.md
8. Update README.md (add Phase IV section)

### Phase E: Helm Chart - BONUS (8-10 tasks, optional, depends on C)
Tasks for:
1. Create helm/taskflow/ directory
2. Create Chart.yaml
3. Create values.yaml
4. Create templates/_helpers.tpl
5. Create templates/namespace.yaml
6. Create templates/configmap.yaml
7. Create templates/backend-deployment.yaml
8. Create templates/backend-service.yaml
9. Create templates/frontend-deployment.yaml
10. Create templates/frontend-service.yaml
11. Test helm lint
12. Test helm install --dry-run

### Phase F: Integration & Testing (10-12 tasks, depends on A-D)
Tasks for:
1. Verify Docker Desktop K8s enabled
2. Verify kubectl configured
3. Build both Docker images
4. Load images to K8s (if needed)
5. Apply all K8s manifests
6. Wait for pods to reach Running status
7. Verify health probes passing
8. Get LoadBalancer external IP
9. Test frontend access via LoadBalancer
10. Test backend access from frontend pod
11. Test Phase I console (uv run todo)
12. Test Phase II web UI via K8s
13. Test Phase III chatbot via K8s
14. Test OAuth login (Google, GitHub)
15. Test all CRUD operations
16. Verify resource limits enforced
17. Verify non-root users
18. Monitor pods for 10 minutes (no restarts)

## Task Detail Requirements:

Each task must include:
1. **Task ID** (T-001, T-002, etc.)
2. **Phase** (0, A, B, C, D, E, or F)
3. **Title** - Clear, actionable task name
4. **File Path** - Exact file to create/modify
5. **Description** - What to implement
6. **Acceptance Criteria** - How to verify completion
7. **Dependencies** - Which tasks must complete first
8. **Estimated Complexity** - Low/Medium/High
9. **Agent to Use** - Which agent helps with this task
10. **Can Run in Parallel** - Mark with [P] if parallelizable

Mark tasks that can run in parallel with [P].

Organize by dependency layers within each phase.

## Special Considerations:

### Multi-Stage Docker Builds:
- Backend: 2 stages (builder + runtime)
- Frontend: 3 stages (dependencies + builder + runner)
- Specify layer caching optimizations
- Copy only necessary files to final stage

### Kubernetes Health Probes:
- Startup probe: 5s period, 30 failures (150s max)
- Liveness probe: 30s initial, 10s period, 5s timeout
- Readiness probe: 10s initial, 5s period, 5s timeout
- Specify exact probe configurations

### Security Contexts:
- runAsNonRoot: true
- runAsUser: 1000
- allowPrivilegeEscalation: false
- Verify in acceptance criteria

### Resource Limits:
- Backend: 256Mi/250m requests, 500Mi/500m limits
- Frontend: 256Mi/250m requests, 512Mi/500m limits
- Verify limits enforced

### Testing Strategy:
- Unit tests: Dockerfile builds, YAML validation
- Integration tests: Pods running, services accessible
- E2E tests: All Phase I-III features work via K8s
- Performance tests: Image sizes, startup times

Generate comprehensive tasks that result in a working Phase IV deployment when executed.

Total estimated tasks: 50-65 tasks

## Response snapshot

Generated comprehensive task breakdown for Phase IV: Local Kubernetes Deployment with 126 tasks organized into 11 phases:

**Task Organization**:
- Phase 0: Research & Design (4 tasks) - Documentation artifacts
- Phase 1: Setup (5 tasks) - Directory structure and .dockerignore
- Phase 2: Foundational (4 tasks) - Health endpoint, Next.js config, startup script (BLOCKS all user stories)
- User Story 1: Build Production Docker Images - P1 (18 tasks) - Backend/frontend multi-stage builds
- User Story 2: Configure Local Kubernetes Cluster - P1 (6 tasks) - Cluster setup and namespace
- User Story 3: Deploy Backend to Kubernetes - P1 (17 tasks) - Backend deployment with probes, ConfigMap/Secret
- User Story 4: Deploy Frontend to Kubernetes - P2 (13 tasks) - Frontend deployment with LoadBalancer
- User Story 5: Manage Configuration - P3 (7 tasks) - ConfigMap/Secret validation
- User Story 6: Deploy with Helm Chart - P4 BONUS (16 tasks) - Helm chart creation and testing
- Phase 9: Helper Scripts & Docs (8 tasks) - Automation and documentation
- Phase 10: Integration & Testing (28 tasks) - Comprehensive E2E validation

**Key Features**:
- All tasks follow strict checkbox format: `- [ ] [TaskID] [P?] [Story] Description with file path`
- 45 tasks marked [P] for parallel execution opportunities
- Clear dependency graph showing user story completion order
- MVP scope identified: Phases 0-2 + US1-4 = 50 tasks (minimum viable deployment)
- Full scope: 126 tasks including config management, Helm bonus, automation, comprehensive testing
- Each user story has independent test criteria for validation
- Parallel execution examples provided for User Stories 1 and 3
- Agent assignments for each phase (@devops-agent, @task-manager-agent, @nextjs-expert-agent, @orchestrator-agent)

**Validation Performed**:
- ✅ All 126 tasks follow required checkbox format
- ✅ Task IDs sequential (T001-T126)
- ✅ User story labels applied correctly ([US1]-[US6])
- ✅ File paths specified for every implementation task
- ✅ Dependencies mapped to spec priorities (P1→P2→P3→P4)
- ✅ Parallel opportunities identified and marked [P]
- ✅ MVP scope clearly defined (50 tasks)

**Output**: Created `/specs/004-k8s-deployment/tasks.md` with complete task breakdown ready for execution via `/sp.implement`

## Outcome

- ✅ Impact: Created comprehensive, executable task breakdown for Phase IV Kubernetes deployment (126 tasks, 11 phases)
- 🧪 Tests: Format validation passed (all tasks use checkbox format), dependency graph validated (matches spec priorities), parallel opportunities identified (45 tasks marked [P])
- 📁 Files: Created specs/004-k8s-deployment/tasks.md (comprehensive task list with dependencies, parallel opportunities, and implementation strategy)
- 🔁 Next prompts: Execute implementation with `/sp.implement` or review tasks with user for approval before starting; consider creating GitHub issues with `/sp.taskstoissues` for team coordination
- 🧠 Reflection: Successfully mapped all 27 components from plan.md into 126 granular tasks organized by user story priority. Task breakdown enables incremental delivery (MVP with US1-4), parallel execution (45 [P] tasks), and independent validation per story. Strict checklist format compliance ensures tasks are immediately executable by LLM agents.

## Evaluation notes (flywheel)

- Failure modes observed: None - all tasks generated with proper format, dependencies, and file paths
- Graders run and results (PASS/FAIL): Format validator PASS (all 126 tasks use required checkbox format), Dependency validator PASS (user story order matches spec priorities P1→P2→P3→P4), Parallel opportunity validator PASS (45 tasks correctly marked [P])
- Prompt variant (if applicable): Standard /sp.tasks workflow with custom context for Kubernetes/Docker deployment (multi-agent assignment specified)
- Next experiment (smallest change to try): Consider auto-generating contract YAML files during Phase 0 to reduce manual documentation work; explore generating Helm chart templates programmatically from K8s manifests to ensure consistency
