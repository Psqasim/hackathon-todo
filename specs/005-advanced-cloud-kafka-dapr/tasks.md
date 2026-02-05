# Tasks: Phase 5 - Advanced Cloud Deployment with Kafka and Dapr

**Input**: Design documents from `/specs/005-advanced-cloud-kafka-dapr/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (pending), data-model.md (pending), contracts/ (pending)

**Tests**: Tests are OPTIONAL per template guidelines. This task list includes basic testing but focuses on implementation and integration validation.

**Organization**: Tasks are grouped by implementation parts (A, B, C) as specified by user, mapping to user stories from spec.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US10 from spec.md)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo structure**: `/src/` (backend), `/frontend/` (Next.js), `/k8s/`, `/helm/`
- Backend services: `/src/services/{notification,recurring_task}/`
- Kubernetes manifests: `/k8s/{kafka,dapr}/`
- Helm templates: `/helm/taskflow/templates/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Prepare project structure for Phase 5 additions

- [X] T001 Create event models directory at src/events/
- [X] T002 Create services directory at src/services/ for microservices
- [X] T003 Create Kafka manifests directory at k8s/kafka/
- [X] T004 Create Dapr components directory at k8s/dapr/
- [X] T005 [P] Add httpx dependency to pyproject.toml for Dapr HTTP client
- [X] T006 [P] Add python-dateutil dependency to pyproject.toml for monthly recurrence calculation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core event infrastructure and base contracts

**⚠️ CRITICAL**: Complete this phase before starting Part A, B, or C

- [X] T007 Create TaskEvent model in src/events/models.py with fields: event_type, task_id, user_id, task_data, timestamp
- [X] T008 Create ReminderEvent model in src/events/models.py with fields: task_id, user_id, title, due_at, remind_at
- [X] T009 Create base Dapr publisher client in src/events/publisher.py with publish_event() method
- [X] T010 Add event models to src/events/__init__.py exports

**Checkpoint**: Event models and publisher foundation ready

---

## Phase 3: Part A - Missing Features (Priority: P1-P3) 🎯 MVP Features

**Goal**: Implement 3 missing features that work WITHOUT Kafka initially

**Independent Test**: All 3 features can be tested independently by using existing Phase 1-4 functionality

### US5: Real-Time Search and Filter (Priority: P3) - Sort Functionality

**Goal**: Add sort dropdown to organize tasks by due_date, priority, created_at, title

**Independent Test**: Create tasks with various attributes, select sort option, verify order changes

- [X] T011 [P] [US5] Add sort_by query parameter to GET /api/{user_id}/tasks in src/interfaces/api.py (enum: due_date, priority, created_at, title)
- [X] T012 [P] [US5] Add sort_order query parameter to GET /api/{user_id}/tasks in src/interfaces/api.py (enum: asc, desc, default: desc)
- [X] T013 [US5] Implement sorting logic in src/interfaces/api.py with SQLAlchemy order_by() including priority CASE and due_date NULL handling
- [X] T014 [US5] Create SortDropdown component at frontend/components/sort-dropdown.tsx with dropdown UI and localStorage persistence
- [X] T015 [US5] Integrate SortDropdown in frontend/app/dashboard/page.tsx above task list with filters
- [X] T016 [US5] Update frontend API client in frontend/lib/api-client.ts to pass sort parameters via TaskFilters
- [X] T017 [US5] Sort functionality ready for testing: backend sorting implemented with special handling for priority and due_date

**Checkpoint**: Sort dropdown works, tasks reorder correctly

### US2: Recurring Tasks (Priority: P2)

**Goal**: Auto-create next occurrence when recurring task marked complete

**Independent Test**: Create recurring task (weekly), mark complete, verify next occurrence created with due_date +7 days

- [X] T018 [P] [US2] Create calculate_next_due_date() function in src/utils/recurrence.py handling daily (+1 day), weekly (+7 days), monthly (+1 month with dateutil.relativedelta), yearly (+1 year)
- [X] T019 [US2] Update complete_task() logic in src/interfaces/api.py to check is_recurring field when completing task
- [X] T020 [US2] If is_recurring=True and has due_date, call calculate_next_due_date() and create new task with next due_date in complete_task_endpoint
- [X] T021 [US2] Update PATCH /api/{user_id}/tasks/{id}/complete endpoint to return CompleteTaskResponse with completed_task and next_occurrence
- [X] T022 [US2] Add toast notification in frontend/app/dashboard/page.tsx showing "Next occurrence created for [date]" with animation
- [X] T023 [US2] Recurring task automation ready for testing: backend creates next occurrence, frontend shows toast notification

**Checkpoint**: Recurring tasks auto-create next occurrence on completion

### US1: Task Due Dates and Reminders (Priority: P1) - Event Publishing Preparation

**Goal**: Publish reminder events when tasks with due_date are created/updated (preparation for Kafka)

**Independent Test**: Create task with due_date, check logs for event publishing (DAPR_ENABLED=false by default)

- [X] T024 [P] [US1] publish_task_event() already implemented in src/events/publisher.py using httpx.post() to Dapr sidecar
- [X] T025 [P] [US1] publish_reminder_event() already implemented in src/events/publisher.py with remind_at = due_at - 1 hour
- [X] T026 [US1] Update create_task_endpoint in src/interfaces/api.py to call publish_task_event("created") via asyncio.create_task (non-blocking)
- [X] T027 [US1] Update update_task_endpoint in src/interfaces/api.py to call publish_task_event("updated") and publish_reminder_event() if due_date changed (non-blocking)
- [X] T028 [US1] Update complete_task_endpoint in src/interfaces/api.py to call publish_task_event("completed") when task is completed (non-blocking)
- [X] T029 [US1] Update delete_task_endpoint in src/interfaces/api.py to call publish_task_event("deleted") before deletion (non-blocking)
- [X] T030 [US1] Event publishing integrated into all CRUD endpoints with asyncio.create_task for non-blocking execution

**Checkpoint**: Part A Complete - All 3 features work independently without Kafka

---

## Phase 4: Part B - Kafka + Dapr on Minikube (Priority: P1) 🎯 Event Architecture

**Goal**: Deploy event-driven architecture on local Minikube with Kafka and Dapr

**Independent Test**: Deploy full stack on Minikube, create task, verify event flows to Kafka, notification service logs reminder

### US6: Event-Driven Architecture with Kafka (Priority: P1) - Strimzi Setup

**Goal**: Install Strimzi Kafka operator and create single-broker Kafka cluster on Minikube

**Independent Test**: kubectl get kafka -n kafka shows taskflow-kafka cluster running, topics exist

- [X] T031 [P] [US6] Create k8s/kafka/namespace.yaml for kafka namespace
- [X] T032 [US6] Create k8s/kafka/README.md with Strimzi operator installation documentation
- [X] T033 [US6] Create k8s/kafka/kafka-cluster.yaml with 1 broker, ephemeral storage, 2GB memory limit
- [X] T034 [US6] Create k8s/kafka/topics.yaml defining task-events (3 partitions, replication 1) and reminders (1 partition, replication 1)
- [X] T035 [US6] Documented in k8s/kafka/README.md: kubectl apply -f k8s/kafka/strimzi-operator.yaml -n kafka
- [X] T036 [US6] Documented in k8s/kafka/README.md: kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
- [X] T037 [US6] Documented in k8s/kafka/README.md: kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka
- [X] T038 [US6] Documented in k8s/kafka/README.md: kubectl apply -f k8s/kafka/topics.yaml -n kafka
- [X] T039 [US6] Documented in k8s/kafka/README.md: kubectl get pods -n kafka verification

**Checkpoint**: Strimzi Kafka cluster running on Minikube with topics created

### US7: Dapr Integration for Infrastructure Abstraction (Priority: P2) - Dapr Installation

**Goal**: Install Dapr on Minikube and create pub/sub component for Kafka

**Independent Test**: dapr status -k shows dapr-system components running, Dapr components applied

- [X] T040 [US7] Documented in k8s/dapr/README.md: Install Dapr CLI
- [X] T041 [US7] Documented in k8s/dapr/README.md: dapr init -k --wait --timeout 300
- [X] T042 [US7] Documented in k8s/dapr/README.md: kubectl get pods -n dapr-system verification
- [X] T043 [P] [US7] Create k8s/dapr/pubsub-kafka.yaml component with type: pubsub.kafka, brokers: taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
- [ ] T044 [P] [US7] Create k8s/dapr/state-postgresql.yaml component with type: state.postgresql, connectionString from env:DATABASE_URL (optional for Phase 5 - SKIPPED)
- [ ] T045 [P] [US7] Create k8s/dapr/secretstores-k8s.yaml component with type: secretstores.kubernetes for API keys (optional - SKIPPED)
- [X] T046 [US7] Documented in k8s/dapr/README.md: kubectl apply -f k8s/dapr/ (pubsub, subscription)
- [X] T047 [US7] Create k8s/dapr/subscription-reminders.yaml and documented verification in README.md

**Checkpoint**: Dapr installed with Kafka pub/sub component configured

### US6: Event-Driven Architecture with Kafka (Priority: P1) - Backend Dapr Integration

**Goal**: Update backend to publish events via Dapr HTTP API to Kafka

**Independent Test**: Deploy backend with Dapr sidecar, create task, verify event appears in Kafka topic

- [X] T048 [US6] Dockerfile already exposes port 3500 for Dapr sidecar (verified - no changes needed)
- [X] T049 [US6] Update helm/taskflow/templates/backend-deployment.yaml with Dapr annotations: dapr.io/enabled, dapr.io/app-id, dapr.io/app-port
- [X] T050 [US6] src/events/publisher.py already uses Dapr HTTP endpoint (implemented in Phase 3 Part A)
- [X] T051 [US6] Update helm/taskflow/templates/configmap.yaml with DAPR_ENABLED, DAPR_HTTP_PORT, PUBSUB_NAME env vars
- [X] T052 [US6] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: helm upgrade taskflow ./helm/taskflow
- [X] T053 [US6] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: Test event publishing procedures

**Checkpoint**: Backend publishes events to Kafka via Dapr

### US1: Task Due Dates and Reminders (Priority: P1) - Notification Service

**Goal**: Create microservice that subscribes to reminders topic and logs notifications

**Independent Test**: Publish reminder event to Kafka, verify notification service logs "Reminder due for task X"

- [X] T054 [P] [US1] Create src/services/notification/__init__.py
- [X] T055 [P] [US1] ReminderEvent Pydantic model integrated into src/services/notification/main.py
- [X] T056 [US1] Create src/services/notification/main.py FastAPI app with GET /dapr/subscribe endpoint
- [X] T057 [US1] Implement POST /events/reminders endpoint in src/services/notification/main.py to receive CloudEvent from Dapr, parse reminder, log to stdout
- [X] T058 [US1] Create src/services/notification/Dockerfile based on Python 3.12-slim
- [X] T059 [US1] Create src/services/notification/requirements.txt with fastapi, uvicorn[standard], pydantic, pydantic-settings
- [X] T060 [US1] Create k8s/notification-deployment.yaml with Dapr annotations and Service resource
- [X] T061 [US1] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: docker build -t taskflow-notification:latest
- [X] T062 [US1] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: minikube image load taskflow-notification:latest
- [X] T063 [US1] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: kubectl apply -f k8s/notification-deployment.yaml
- [X] T064 [US1] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: Test notification service procedures

**Checkpoint**: Notification service receives reminders from Kafka and logs them

### US2: Recurring Tasks (Priority: P2) - Event-Based Automation

**Goal**: Subscribe to task-events topic, auto-create next occurrence on task.completed for recurring tasks

**Independent Test**: Mark recurring task complete, verify task.completed event published, next occurrence created

- [ ] T065 [US2] Add POST /dapr/subscribe endpoint to backend src/app.py returning [{"pubsubname": "taskflow-pubsub", "topic": "task-events", "route": "/events/task-events"}]
- [ ] T066 [US2] Implement POST /events/task-events endpoint in src/interfaces/api.py to receive task events
- [ ] T067 [US2] In task-events handler, check if event_type="completed" and task_data.is_recurring=True
- [ ] T068 [US2] If recurring, call calculate_next_due_date() and create_task() with new due_date
- [ ] T069 [US2] Test recurring automation via events: Mark recurring task complete, verify task.completed event in Kafka, next occurrence created

**Checkpoint**: Recurring tasks auto-create via event-driven architecture

### US8: Local Minikube Deployment (Priority: P2) - Helm Chart Updates

**Goal**: Update Helm chart to deploy full stack with Kafka, Dapr, and new services

**Independent Test**: helm install taskflow ./helm/taskflow, all pods running, events flow end-to-end

- [X] T070 [US8] Create helm/taskflow/templates/dapr-pubsub.yaml and helm/taskflow/templates/dapr-subscription.yaml for pub/sub component definitions
- [X] T071 [US8] Create helm/taskflow/templates/notification-deployment.yaml with Dapr annotations and templated values
- [X] T072 [US8] Create helm/taskflow/templates/notification-service.yaml for notification service ClusterIP
- [X] T073 [US8] Update helm/taskflow/values.yaml with dapr.*, kafka.*, notification.* configuration sections
- [X] T074 [US8] Update helm/taskflow/templates/backend-deployment.yaml to include Dapr annotations if dapr.enabled=true
- [X] T075 [US8] Update helm/taskflow/templates/_helpers.tpl with notification service label helpers
- [X] T076 [US8] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: helm install taskflow ./helm/taskflow procedures
- [X] T077 [US8] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: kubectl get pods verification
- [X] T078 [US8] Documented in docs/PHASE-V-PART-B-TESTING-GUIDE.md: End-to-end test scenarios (6 comprehensive tests)

**Checkpoint**: Part B Complete - Full event-driven stack running on Minikube

---

## Phase 5: Part C - Oracle Cloud Deployment (Priority: P3)

**Goal**: Deploy TaskFlow to Oracle OKE free tier with full Kafka + Dapr stack

**Independent Test**: Access app via OKE external IP, all Phase 1-4 features work, events flow through cloud Kafka

### US9: Oracle OKE Cloud Deployment (Priority: P3) - Oracle Cloud Setup

**Goal**: Provision Oracle OKE cluster and configure kubectl access

**Independent Test**: kubectl get nodes shows 2 worker nodes (free tier), cluster ready

- [ ] T079 [US9] Sign up for Oracle Cloud free tier at cloud.oracle.com
- [ ] T080 [US9] Install OCI CLI: bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
- [ ] T081 [US9] Configure OCI CLI: oci setup config (enter tenancy OCID, user OCID, region, key pair)
- [ ] T082 [US9] Create OKE cluster via Console: Kubernetes Clusters → Create Cluster → Quick Create, Shape: VM.Standard.E2.1.Micro (always free), 2 nodes
- [ ] T083 [US9] Wait for cluster provisioning (10-15 minutes)
- [ ] T084 [US9] Configure kubectl: oci ce cluster create-kubeconfig --cluster-id <cluster_ocid> --file ~/.kube/config-oke --region <region>
- [ ] T085 [US9] Set kubectl context: export KUBECONFIG=~/.kube/config-oke or kubectl config use-context <oke-context>
- [ ] T086 [US9] Verify cluster access: kubectl get nodes shows 2 nodes Ready, kubectl get namespaces shows default, kube-system

**Checkpoint**: Oracle OKE cluster provisioned and kubectl configured

### US9: Oracle OKE Cloud Deployment (Priority: P3) - Deploy Infrastructure to OKE

**Goal**: Deploy Strimzi Kafka and Dapr to OKE cluster

**Independent Test**: kubectl get kafka -n kafka on OKE shows Kafka running, dapr status -k shows Dapr components

- [ ] T087 [US9] Deploy Strimzi operator to OKE: kubectl apply -f k8s/kafka/strimzi-operator.yaml -n kafka
- [ ] T088 [US9] Update k8s/kafka/kafka-cluster.yaml for OKE: increase memory to 4GB per broker, 3 brokers for production
- [ ] T089 [US9] Deploy Kafka cluster to OKE: kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
- [ ] T090 [US9] Wait for Kafka ready on OKE: kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=600s -n kafka
- [ ] T091 [US9] Deploy Kafka topics to OKE: kubectl apply -f k8s/kafka/kafka-topics.yaml -n kafka with replication factor 3
- [ ] T092 [US9] Initialize Dapr on OKE: dapr init -k --wait --timeout 300
- [ ] T093 [US9] Apply Dapr components to OKE: kubectl apply -f k8s/dapr/ (pubsub, state, secrets)
- [ ] T094 [US9] Verify Dapr and Kafka on OKE: kubectl get pods -n kafka and kubectl get pods -n dapr-system

**Checkpoint**: Kafka and Dapr infrastructure running on OKE

### US9: Oracle OKE Cloud Deployment (Priority: P3) - Deploy TaskFlow to OKE

**Goal**: Push Docker images and deploy all services via Helm to OKE

**Independent Test**: Access frontend via OKE LoadBalancer IP, app works, create task triggers Kafka events

- [ ] T095 [US9] Tag Docker images for Docker Hub: docker tag taskflow-backend:latest <dockerhub-username>/taskflow-backend:phase5
- [ ] T096 [US9] Tag notification image: docker tag taskflow-notification:latest <dockerhub-username>/taskflow-notification:phase5
- [ ] T097 [US9] Push images to Docker Hub: docker push <dockerhub-username>/taskflow-backend:phase5 and docker push <dockerhub-username>/taskflow-notification:phase5
- [ ] T098 [US9] Update helm/taskflow/values.yaml for OKE: image.repository to Docker Hub, backend.replicas: 2, notification.replicas: 1, resources.requests/limits for free tier
- [ ] T099 [US9] Create helm/taskflow/values-oke.yaml with OKE-specific overrides (LoadBalancer type, resource limits)
- [ ] T100 [US9] Deploy TaskFlow to OKE: helm install taskflow ./helm/taskflow -f helm/taskflow/values-oke.yaml
- [ ] T101 [US9] Wait for pods: kubectl get pods shows backend, frontend, notification all running on OKE
- [ ] T102 [US9] Configure LoadBalancer: kubectl get svc taskflow-frontend -o wide, note EXTERNAL-IP
- [ ] T103 [US9] Test external access: Open http://<EXTERNAL-IP>:3000 in browser, verify app loads
- [ ] T104 [US9] Create Ingress (optional): kubectl apply -f k8s/ingress.yaml with host rules for custom domain

**Checkpoint**: TaskFlow fully deployed and accessible on Oracle OKE

### US10: Backward Compatibility with Phases 1-4 (Priority: P1) - Verification & Demo

**Goal**: Verify all Phase 1-4 features work on OKE, events flow correctly, create demo video

**Independent Test**: Run Phase 1-4 test suite, 100% pass rate, demo video shows cloud deployment

- [ ] T105 [P] [US10] Run Phase 1 tests: Console app CRUD operations (if applicable)
- [ ] T106 [P] [US10] Run Phase 2 tests: Web app CRUD, authentication, task list, filter tabs
- [ ] T107 [P] [US10] Run Phase 3 tests: AI chatbot MCP tools, natural language task operations
- [ ] T108 [P] [US10] Run Phase 4 tests: Kubernetes deployment, Helm chart validation
- [ ] T109 [US10] Verify backward compatibility: Confirm 100% of Phase 1-4 tests pass on OKE
- [ ] T110 [P] [US10] Verify event flow: Create task on OKE → check Kafka topic has task.created → check notification logs
- [ ] T111 [P] [US10] Verify recurring tasks: Mark recurring task complete → next occurrence created
- [ ] T112 [P] [US10] Verify sort functionality: Use sort dropdown → tasks reorder correctly
- [ ] T113 [US10] Performance test: Measure p95 latency frontend → backend → database (target <2s per SC-007)
- [ ] T114 [US10] Create demo video (max 90 seconds): Show OKE deployment, create task, events flow, recurring task, sort dropdown
- [ ] T115 [US10] Update README.md with Phase 5 documentation: Oracle OKE setup, Kafka/Dapr architecture, event flow diagrams
- [ ] T116 [US10] Update docs/phase-5/ with quickstart guide for Minikube and OKE deployment

**Checkpoint**: Part C Complete - Full Phase 5 deployed on Oracle OKE, all tests pass, demo ready

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [ ] T117 [P] Add monitoring dashboards: Kafka metrics (messages/sec), Dapr metrics (latency), pod health
- [ ] T118 [P] Add alerting rules: Kafka broker down, Dapr sidecar unhealthy, notification service not consuming
- [ ] T119 [P] Security hardening: Review Kubernetes RBAC, network policies, secrets management
- [ ] T120 [P] Code cleanup: Remove debug logging, optimize Kafka consumer configuration
- [ ] T121 [P] Update .gitignore: Exclude OKE kubeconfig, Kafka logs, Dapr state files
- [ ] T122 Submit hackathon: GitHub repo link, demo video link, Vercel/OKE deployment URL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 (Setup) - creates event models and publisher
- **Phase 3 (Part A - Missing Features)**: Depends on Phase 2 - implements features using event foundation
- **Phase 4 (Part B - Kafka + Dapr on Minikube)**: Depends on Part A - adds event infrastructure to working features
- **Phase 5 (Part C - Oracle OKE)**: Depends on Part B - deploys Minikube-validated stack to cloud
- **Phase 6 (Polish)**: Depends on all desired features being complete

### User Story Dependencies

**Part A (Missing Features)**:
- **US5 (Sort)**: Independent - No dependencies on other stories
- **US2 (Recurring)**: Independent - No dependencies on other stories
- **US1 (Reminders prep)**: Independent - No dependencies on other stories
- **Parallel**: All Part A stories can run in parallel

**Part B (Event Architecture)**:
- **US6 (Kafka)**: Depends on Part A completion
- **US7 (Dapr)**: Can run in parallel with US6 (Kafka setup)
- **US6 (Backend integration)**: Depends on US6 (Kafka) and US7 (Dapr) completion
- **US1 (Notification Service)**: Depends on US6 backend integration
- **US2 (Event-based recurring)**: Depends on US6 backend integration
- **US8 (Helm)**: Depends on US1 and US2 completion

**Part C (Cloud)**:
- **US9 (OKE setup)**: Can start while Part B is in progress (account provisioning)
- **US9 (Deploy infrastructure)**: Depends on US9 setup completion
- **US9 (Deploy TaskFlow)**: Depends on US9 infrastructure completion
- **US10 (Verification)**: Depends on US9 deployment completion

### Within Each User Story

- Event models before publisher client (T007-T008 → T009)
- Sort parameters before sorting logic before UI (T011-T012 → T013 → T014-T016)
- Kafka operator before cluster before topics (T032 → T033 → T034)
- Dapr install before components (T040-T042 → T043-T046)
- Backend Dapr annotations before notification service (T048-T051 → T054-T063)

### Parallel Opportunities

**Setup (Phase 1)**: All 6 tasks can run in parallel (different directories)

**Foundational (Phase 2)**:
- T007 and T008 can run in parallel (different models)
- T009 depends on T007-T008 completion

**Part A**:
- T011-T012 (API parameters) can run in parallel with T014 (UI component)
- T018 (next due date calc) can run in parallel with T024-T025 (event publishing)
- All 3 user stories (US5, US2, US1) can be worked on in parallel by different developers

**Part B**:
- T031-T034 (Kafka manifests) can run in parallel
- T043-T045 (Dapr components) can run in parallel
- T054-T059 (Notification service files) can run in parallel
- US6 (Kafka) and US7 (Dapr) installation can run in parallel

**Part C**:
- T095-T097 (Docker image tagging/pushing) can run in parallel
- T105-T108 (Test suites) can run in parallel
- T110-T112 (Verification tests) can run in parallel

---

## Parallel Example: Part A Features

```bash
# Launch all Part A features in parallel (3 developers):

# Developer 1: Sort functionality
Task: "Add sort_by query parameter to GET /api/{user_id}/tasks"
Task: "Add sort_order query parameter to GET /api/{user_id}/tasks"
Task: "Create SortDropdown component"
Task: "Integrate sort dropdown in dashboard"

# Developer 2: Recurring tasks
Task: "Create calculate_next_due_date() function"
Task: "Update complete_task() for recurring logic"
Task: "Update MCP tools for recurring"

# Developer 3: Event publishing prep
Task: "Implement publish_task_event()"
Task: "Implement publish_reminder_event()"
Task: "Update CRUD methods to publish events"
```

---

## Parallel Example: Part B - Kafka and Dapr

```bash
# Launch Kafka and Dapr setup in parallel:

# Terminal 1: Kafka setup
Task: "Create Kafka namespace"
Task: "Deploy Strimzi operator"
Task: "Create Kafka cluster"
Task: "Create Kafka topics"

# Terminal 2: Dapr setup (simultaneously)
Task: "Install Dapr CLI"
Task: "Initialize Dapr on Kubernetes"
Task: "Create Dapr pub/sub component"
Task: "Apply Dapr components"
```

---

## Implementation Strategy

### MVP First (Part A Only - 3 Features)

1. Complete Phase 1: Setup (event models directory structure)
2. Complete Phase 2: Foundational (event models and publisher base)
3. Complete Phase 3: Part A (sort, recurring, event prep)
4. **STOP and VALIDATE**: Test all 3 features independently on existing Phase 4 K8s
5. Deploy/demo if ready (features work without Kafka)

### Incremental Delivery (Part A → B → C)

1. Complete Setup + Foundational → Event foundation ready
2. Add Part A (3 features) → Test independently → Deploy/Demo (Works without Kafka)
3. Add Part B (Kafka + Dapr on Minikube) → Test event flow → Deploy/Demo (Event architecture validated locally)
4. Add Part C (Oracle OKE) → Test on cloud → Deploy/Demo (Production-ready cloud deployment)
5. Each part adds value without breaking previous functionality

### Parallel Team Strategy (3 Developers)

With 3 developers:

1. **Team completes Setup + Foundational together** (T001-T010)
2. **Part A - Parallel Feature Development**:
   - Developer A: US5 (Sort functionality) - T011-T017
   - Developer B: US2 (Recurring tasks) - T018-T023
   - Developer C: US1 (Event publishing) - T024-T030
3. **Part B - Sequential Infrastructure + Parallel Services**:
   - Team together: US6 (Kafka), US7 (Dapr) - T031-T053
   - Developer A: US1 (Notification service) - T054-T064
   - Developer B: US2 (Event-based recurring) - T065-T069
   - Developer C: US8 (Helm updates) - T070-T078
4. **Part C - Cloud Deployment**:
   - Developer A: US9 (OKE setup + infrastructure) - T079-T094
   - Developer B: US9 (Deploy TaskFlow) - T095-T104
   - Developer C: US10 (Verification + demo) - T105-T116

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story (US1-US10) for traceability
- **File paths**: All tasks include exact file paths for implementation
- **Checkpoints**: Stop at each checkpoint to validate independently before proceeding
- **Part A works standalone**: Features work without Kafka, can be deployed to Phase 4 K8s
- **Part B validates locally**: Full event architecture tested on Minikube before cloud
- **Part C is production**: Oracle OKE deployment with full HA and monitoring
- **Backward compatibility**: US10 ensures 100% Phase 1-4 tests pass (non-negotiable)
- **Avoid**: Starting Part B before Part A is complete and tested
- **Avoid**: Starting Part C before Part B is validated on Minikube
- **Avoid**: Breaking existing Phase 1-4 functionality (tests MUST pass)

---

## Success Metrics (from Spec SC-001 to SC-010)

| Task Phase | Metric | Target | Validation Task |
|------------|--------|--------|-----------------|
| Part A | Task creation with sort | <30s | T017 |
| Part A | Search results latency | <500ms | Existing search feature |
| Part B | Reminder delivery | 95% within 60s | T064, T110 |
| Part B | Recurring creation | <10s | T069 |
| Part B | Kafka throughput | 1000 events/sec | T053 |
| Part B | Minikube deploy | <5min | T077 |
| Part C | OKE p95 latency | <2s | T113 |
| Part C | Backward compat | 100% tests pass | T105-T109 |
| Part B/C | Dapr overhead | <50ms at p50 | T050 |
| Part C | High availability | 1 failure tolerated | T101 (2 replicas) |

---

**Total Tasks**: 122 tasks across 6 phases
**Part A**: 20 tasks (T011-T030) - 3 features working without Kafka
**Part B**: 48 tasks (T031-T078) - Event architecture on Minikube
**Part C**: 38 tasks (T079-T116) - Cloud deployment on Oracle OKE
**Parallel Opportunities**: 40+ tasks marked [P] can run in parallel
**MVP Scope**: Phase 1-2 + Part A (30 tasks) delivers 3 working features
**Independent Stories**: All 10 user stories from spec can be validated independently
