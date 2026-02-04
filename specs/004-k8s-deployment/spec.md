# Feature Specification: Local Kubernetes Deployment

**Feature Branch**: `004-k8s-deployment`
**Created**: 2026-02-03
**Status**: Draft
**Input**: User description: "Deploy the TaskFlow application to a local Kubernetes cluster using Docker containers and Kubernetes orchestration, maintaining all functionality from Phases I-III"

## Overview

Deploy the TaskFlow Todo application to a local Kubernetes cluster, containerizing both the FastAPI backend and Next.js frontend while maintaining all existing functionality from Phases I-III (console app, web application, and AI chatbot). This deployment will use Docker multi-stage builds, Kubernetes manifests, and follow cloud-native best practices for production-ready container orchestration.

**Current State:**
- Phase I: Console application running locally (unchanged)
- Phase II: Web application on Vercel (frontend) + Hugging Face Spaces (backend)
- Phase III: AI Chatbot with OpenAI ChatKit, Agents SDK, and MCP
- Database: Neon PostgreSQL (cloud-hosted, unchanged)

**Target State:**
- Phase I: Console application (local, unchanged)
- Phase II/III: Kubernetes cluster (local on Docker Desktop/Minikube)
  - Backend Pod: FastAPI + MCP server
  - Frontend Pod: Next.js standalone
  - Services: LoadBalancer (frontend), ClusterIP (backend)
- Database: Neon PostgreSQL (external, unchanged)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build Production Docker Images (Priority: P1)

As a developer, I can build optimized, production-ready Docker images for both backend and frontend services using multi-stage builds, ensuring small image sizes, fast startup times, and secure execution with non-root users.

**Why this priority**: Foundation for all deployment - without working container images, Kubernetes deployment is impossible. Multi-stage builds ensure production-ready artifacts.

**Independent Test**: Build both images successfully, run them locally with `docker run`, verify they start without errors, respond to health checks, and function identically to the development versions.

**Acceptance Scenarios**:

1. **Given** backend Dockerfile with multi-stage build, **When** `docker build -t taskflow-backend:latest .` is executed, **Then** image builds successfully in under 5 minutes, final image size is under 500MB, contains only runtime dependencies, runs as non-root user (UID 1000)

2. **Given** frontend Dockerfile with multi-stage build and standalone output, **When** `docker build -t taskflow-frontend:latest ./frontend` is executed, **Then** image builds successfully, final image is under 300MB, includes only standalone artifacts and static files, runs as non-root user

3. **Given** backend image running with `docker run -p 7860:7860`, **When** accessing `http://localhost:7860/health`, **Then** returns `{"status": "healthy"}` with 200 status code

4. **Given** frontend image running with `docker run -p 3000:3000`, **When** accessing `http://localhost:3000`, **Then** homepage loads successfully with all UI components visible

5. **Given** both images built, **When** inspecting with `docker images`, **Then** both images use Alpine or slim base images, show recent build timestamp, and have proper tags

---

### User Story 2 - Configure Local Kubernetes Cluster (Priority: P1)

As a developer, I can set up and verify a local Kubernetes cluster using Docker Desktop's built-in Kubernetes support, creating a dedicated namespace for the TaskFlow application.

**Why this priority**: Kubernetes cluster is required before any deployments can occur. Local setup with Docker Desktop provides the simplest path for development and testing.

**Independent Test**: Run `kubectl get nodes` to verify cluster is running, create `taskflow` namespace, set it as default context, confirm with `kubectl config view --minify`.

**Acceptance Scenarios**:

1. **Given** Docker Desktop installed with Kubernetes enabled, **When** running `kubectl cluster-info`, **Then** output shows "Kubernetes control plane is running at https://kubernetes.docker.internal:6443"

2. **Given** cluster is running, **When** executing `kubectl get nodes`, **Then** output shows at least one node in "Ready" status

3. **Given** cluster is ready, **When** running `kubectl create namespace taskflow`, **Then** namespace "taskflow" is created successfully

4. **Given** taskflow namespace exists, **When** running `kubectl config set-context --current --namespace=taskflow`, **Then** current context is set to use taskflow namespace

5. **Given** namespace is set, **When** running `kubectl config view --minify | grep namespace`, **Then** output confirms "namespace: taskflow"

---

### User Story 3 - Deploy Backend to Kubernetes (Priority: P1)

As a developer, I can deploy the FastAPI backend with MCP server to Kubernetes using a Deployment and ClusterIP Service, with proper configuration management via ConfigMap and Secret, health probes, and resource limits.

**Why this priority**: Backend must be running before frontend can connect to it. Includes all critical Kubernetes patterns: ConfigMap, Secret, health checks, resource management.

**Independent Test**: Apply backend manifests, verify pod is running with `kubectl get pods`, check logs show no errors, exec into pod and curl health endpoint internally, verify backend is accessible from within cluster.

**Acceptance Scenarios**:

1. **Given** backend manifests (deployment, service, configmap, secret), **When** running `kubectl apply -f k8s/backend-*.yaml`, **Then** all resources are created without errors

2. **Given** backend deployment created, **When** running `kubectl get pods -l app=taskflow-backend`, **Then** shows 1 pod in "Running" status within 2 minutes

3. **Given** backend pod running, **When** checking `kubectl logs <pod-name>`, **Then** logs show FastAPI and MCP server started successfully on ports 7860 and 8001

4. **Given** backend pod ready, **When** running `kubectl exec <pod-name> -- curl http://localhost:7860/health`, **Then** returns `{"status": "healthy"}`

5. **Given** backend service created, **When** running `kubectl get svc backend-service`, **Then** shows ClusterIP service with port 8000 targeting port 7860

6. **Given** backend deployment, **When** checking `kubectl describe pod <pod-name>`, **Then** shows liveness probe passing, readiness probe passing, resource requests 256Mi/250m CPU and limits 500Mi/500m CPU

7. **Given** ConfigMap and Secret applied, **When** inspecting pod environment with `kubectl exec <pod-name> -- env`, **Then** shows DATABASE_URL, JWT_SECRET_KEY, and other configuration variables loaded correctly

---

### User Story 4 - Deploy Frontend to Kubernetes (Priority: P2)

As a developer, I can deploy the Next.js frontend to Kubernetes with a LoadBalancer Service for external access, configured to communicate with the backend ClusterIP service, with health checks and resource limits.

**Why this priority**: Completes the full-stack deployment, making the application accessible to users. Depends on backend being operational first for proper functionality.

**Independent Test**: Apply frontend manifests, verify pod running, access via LoadBalancer external IP, confirm homepage loads, test task creation flow end-to-end through UI.

**Acceptance Scenarios**:

1. **Given** frontend manifests applied, **When** running `kubectl get pods -l app=taskflow-frontend`, **Then** shows 1 pod in "Running" status within 2 minutes

2. **Given** frontend service created, **When** running `kubectl get svc frontend-service`, **Then** shows LoadBalancer service with external IP assigned (or localhost on Docker Desktop)

3. **Given** LoadBalancer IP available, **When** accessing `http://<external-ip>` in browser, **Then** TaskFlow homepage loads with navigation, branding, and UI components visible

4. **Given** frontend accessible, **When** user signs in and creates a task via UI, **Then** task is created successfully and appears in task list, confirming frontend-to-backend communication works

5. **Given** frontend pod running, **When** checking `kubectl describe pod <frontend-pod>`, **Then** shows liveness and readiness probes passing, resource limits configured (256Mi/250m CPU requests, 512Mi/500m CPU limits)

---

### User Story 5 - Manage Configuration with Kubernetes Resources (Priority: P3)

As a developer, I can manage application configuration separately from code using Kubernetes ConfigMaps for non-sensitive settings and Secrets for sensitive credentials, with proper base64 encoding and environment variable injection into pods.

**Why this priority**: Enables environment-specific configuration without rebuilding images. Best practice for cloud-native applications. Can be implemented alongside deployment setup.

**Independent Test**: Update ConfigMap with new backend URL, verify pod picks up change after restart, update Secret with new JWT key, confirm backend uses new value, test that sensitive values are not visible in pod describe output.

**Acceptance Scenarios**:

1. **Given** ConfigMap with backend URL, JWT algorithm, expiration settings, **When** running `kubectl get configmap taskflow-config -o yaml`, **Then** shows all non-sensitive configuration values in plain text

2. **Given** Secret with DATABASE_URL, JWT_SECRET_KEY, OAuth credentials, **When** running `kubectl get secret taskflow-secrets -o yaml`, **Then** shows all values base64 encoded, not visible in plain text

3. **Given** backend deployment referencing ConfigMap, **When** running `kubectl exec <backend-pod> -- env | grep JWT_ALGORITHM`, **Then** shows value from ConfigMap (e.g., "HS256")

4. **Given** backend deployment referencing Secret, **When** running `kubectl exec <backend-pod> -- env | grep DATABASE_URL`, **Then** shows decoded value matching Neon connection string

5. **Given** ConfigMap updated with new value, **When** restarting pod with `kubectl rollout restart deployment taskflow-backend`, **Then** new pod picks up updated configuration value

6. **Given** Secret created, **When** running `kubectl describe secret taskflow-secrets`, **Then** output shows field names but not actual secret values

---

### User Story 6 - Deploy with Helm Chart (Priority: P4) [BONUS]

As a developer, I can deploy the entire TaskFlow stack using a single Helm command, with customizable values for different environments, making deployment repeatable and version-controlled.

**Why this priority**: Bonus feature that simplifies deployment workflow and demonstrates cloud-native packaging. Nice-to-have but not critical for basic functionality.

**Independent Test**: Run `helm install taskflow ./helm/taskflow`, verify all resources created, test application works, run `helm upgrade` with different values, confirm changes applied, run `helm uninstall` and verify clean removal.

**Acceptance Scenarios**:

1. **Given** Helm chart created with Chart.yaml and values.yaml, **When** running `helm lint ./helm/taskflow`, **Then** reports no errors or warnings

2. **Given** chart structure complete, **When** running `helm install taskflow ./helm/taskflow`, **Then** all Kubernetes resources (namespace, deployments, services, configmap, secrets) are created in single operation

3. **Given** application installed via Helm, **When** accessing frontend via LoadBalancer, **Then** application functions identically to manual manifest deployment

4. **Given** Helm release installed, **When** running `helm upgrade taskflow ./helm/taskflow --set backend.replicas=2`, **Then** backend scales to 2 replicas automatically

5. **Given** Helm release running, **When** running `helm uninstall taskflow`, **Then** all resources are removed cleanly, namespace can be deleted without orphaned resources

---

### Edge Cases

- **What happens when backend pod crashes?** Kubernetes automatically restarts the pod due to restart policy, liveness probe detects failure and triggers restart, service continues routing to healthy pods if multiple replicas exist
- **How does the system handle database connection failures?** Backend health check may fail if database is unreachable, readiness probe removes pod from service endpoints until connection is restored, frontend shows appropriate error messages to users
- **What happens if ConfigMap or Secret is deleted while pods are running?** Running pods continue using loaded values from memory, new pods cannot start due to missing configuration, deployment shows degraded state
- **How are image updates rolled out?** Change image tag in deployment manifest, apply with `kubectl apply`, Kubernetes performs rolling update with zero downtime, old pods remain until new pods pass readiness checks
- **What happens when Docker Desktop Kubernetes is restarted?** All pods are recreated, PersistentVolumes are preserved (if used), external database connection is re-established, LoadBalancer IPs may change

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide multi-stage Dockerfiles that build production-ready container images with minimal size (backend under 500MB, frontend under 300MB)
- **FR-002**: Backend Docker image MUST expose ports 7860 (FastAPI) and 8001 (MCP server) and start both services on container launch
- **FR-003**: Frontend Docker image MUST use Next.js standalone output mode to minimize deployment size and dependencies
- **FR-004**: Both container images MUST run as non-root users (UID 1000) for security compliance
- **FR-005**: System MUST provide Kubernetes manifests organized in k8s/ directory with separate files for each resource type (namespace, configmap, secrets, deployments, services)
- **FR-006**: Backend deployment MUST include HTTP liveness probe on `/health` endpoint with initialDelaySeconds: 30, periodSeconds: 10
- **FR-007**: Backend deployment MUST include HTTP readiness probe on `/health` endpoint with initialDelaySeconds: 10, periodSeconds: 5
- **FR-008**: Backend deployment MUST include HTTP startup probe on `/health` endpoint with failureThreshold: 30, periodSeconds: 5 to handle slow startup
- **FR-009**: Frontend deployment MUST include HTTP liveness probe on `/` endpoint with initialDelaySeconds: 20, periodSeconds: 10
- **FR-010**: Frontend deployment MUST include HTTP readiness probe on `/` endpoint with initialDelaySeconds: 10, periodSeconds: 5
- **FR-011**: System MUST define resource requests (backend: 256Mi memory/250m CPU, frontend: 256Mi memory/250m CPU) for proper scheduling
- **FR-012**: System MUST define resource limits (backend: 500Mi memory/500m CPU, frontend: 512Mi memory/500m CPU) to prevent resource exhaustion
- **FR-013**: Backend service MUST be type ClusterIP on port 8000 targeting container port 7860 for internal-only access
- **FR-014**: Frontend service MUST be type LoadBalancer on port 80 targeting container port 3000 for external user access
- **FR-015**: System MUST provide ConfigMap containing non-sensitive configuration (backend URL, JWT algorithm, JWT expiration, MCP backend URL)
- **FR-016**: System MUST provide Secret with base64-encoded sensitive data (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY, OAuth credentials)
- **FR-017**: All pods MUST inject ConfigMap and Secret values as environment variables
- **FR-018**: Backend deployment MUST set security context with runAsNonRoot: true, runAsUser: 1000, fsGroup: 1000
- **FR-019**: System MUST use imagePullPolicy: Never for local images to avoid pulling from remote registries
- **FR-020**: Deployments MUST use label selectors (app=taskflow-backend, app=taskflow-frontend) for service routing
- **FR-021**: All Kubernetes resources MUST be deployed to the `taskflow` namespace
- **FR-022**: Backend MUST expose `/health` endpoint returning `{"status": "healthy"}` with 200 status code when operational
- **FR-023**: System MUST support building images with `docker build -t taskflow-backend:latest .` and `docker build -t taskflow-frontend:latest ./frontend`
- **FR-024**: System MUST support deploying with sequential `kubectl apply -f k8s/*.yaml` commands
- **FR-025**: System MUST maintain all Phase I-III functionality: console app works locally, web UI accessible via Kubernetes, chatbot operational through Kubernetes deployment
- **FR-026**: System MUST connect to external Neon PostgreSQL database without requiring in-cluster database deployment
- **FR-027** [BONUS]: System MUST provide Helm chart structure with Chart.yaml, values.yaml, templates/ directory, and NOTES.txt
- **FR-028** [BONUS]: Helm chart MUST support customization via values (image tags, replica counts, resource limits, configuration values)
- **FR-029** [BONUS]: Helm chart MUST support deployment with single command `helm install taskflow ./helm/taskflow`

### Key Entities

- **Docker Image (Backend)**: Container artifact containing FastAPI application, MCP server, Python runtime, virtual environment with dependencies, runs as appuser (UID 1000), exposes ports 7860 and 8001
- **Docker Image (Frontend)**: Container artifact containing Next.js standalone output, static files, Node.js runtime, runs as nodejs user (UID 1000), exposes port 3000
- **Namespace**: Kubernetes logical boundary named `taskflow` containing all application resources, enables isolation and organization
- **Deployment (Backend)**: Kubernetes resource managing backend pod lifecycle with 1 replica, health probes, resource limits, security context, image pull policy
- **Deployment (Frontend)**: Kubernetes resource managing frontend pod lifecycle with 1 replica, health probes, resource limits, pointing to backend service
- **Service (Backend)**: ClusterIP service routing internal traffic on port 8000 to backend pods on port 7860, not externally accessible
- **Service (Frontend)**: LoadBalancer service routing external traffic on port 80 to frontend pods on port 3000, provides external IP or localhost
- **ConfigMap**: Kubernetes resource storing non-sensitive configuration as key-value pairs (BACKEND_URL, JWT_ALGORITHM, JWT_EXPIRATION_DAYS, MCP_BACKEND_URL)
- **Secret**: Kubernetes resource storing base64-encoded sensitive data (DATABASE_URL for Neon, JWT_SECRET_KEY, OPENAI_API_KEY, OAuth client IDs and secrets)
- **Health Probe**: Kubernetes mechanism for monitoring pod health via HTTP requests to designated endpoints, triggers restarts or traffic removal on failure
- **Resource Limit**: Kubernetes constraint defining minimum guaranteed resources (requests) and maximum allowed resources (limits) for CPU and memory
- **Helm Chart** [BONUS]: Package containing Chart.yaml metadata, values.yaml defaults, templates/ with parameterized manifests, enables versioned deployments

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend Docker image builds successfully in under 5 minutes with final size under 500MB
- **SC-002**: Frontend Docker image builds successfully in under 3 minutes with final size under 300MB
- **SC-003**: Kubernetes cluster shows at least one node in "Ready" state within 30 seconds of `kubectl get nodes` command
- **SC-004**: Backend pod reaches "Running" status within 2 minutes of applying deployment manifest
- **SC-005**: Frontend pod reaches "Running" status within 2 minutes of applying deployment manifest
- **SC-006**: Backend health endpoint (`/health`) returns 200 status code when accessed from within cluster
- **SC-007**: Frontend homepage loads successfully within 3 seconds when accessed via LoadBalancer IP
- **SC-008**: Users can complete full task creation workflow (sign in, create task, view task list) through Kubernetes-deployed frontend within 30 seconds
- **SC-009**: All health probes (liveness, readiness, startup) pass consistently without pod restarts during 10-minute observation period
- **SC-010**: Backend can successfully connect to external Neon PostgreSQL database and execute queries
- **SC-011**: Configuration changes in ConfigMap are reflected in pod environment variables after pod restart within 1 minute
- **SC-012**: Secret values are base64-encoded and not visible in plain text when using `kubectl describe secret` command
- **SC-013**: Both containers run as non-root users (verified with `kubectl exec <pod> -- id` showing UID 1000)
- **SC-014**: Resource limits prevent pods from consuming more than specified CPU and memory (500Mi backend, 512Mi frontend)
- **SC-015** [BONUS]: Helm chart installation completes successfully and deploys all resources with single `helm install` command in under 3 minutes
- **SC-016** [BONUS]: Helm chart uninstallation removes all resources cleanly with single `helm uninstall` command

## Assumptions

1. **Local Development Environment**: Developers are using Docker Desktop with Kubernetes enabled on Windows (WSL2), macOS, or Linux systems
2. **Docker Desktop Version**: Docker Desktop 4.0+ provides built-in Kubernetes support (no separate Minikube installation required)
3. **External Database**: Neon PostgreSQL database is already provisioned and accessible from local development environment (no firewall restrictions)
4. **Environment Variables Available**: Developers have access to `.env` files containing DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY, and OAuth credentials from previous phases
5. **Existing Codebase**: Phases I-III are already implemented and functional (console app, web app with Better Auth, chatbot with MCP)
6. **kubectl Installed**: kubectl CLI tool is available (bundled with Docker Desktop Kubernetes)
7. **Helm Optional**: Helm 3+ is installed for bonus Helm chart feature, but not required for core functionality
8. **Network Connectivity**: Local machine can reach external services (Neon database, OpenAI API) without proxy restrictions
9. **Resource Availability**: Local machine has sufficient resources (minimum 4GB RAM, 2 CPU cores available for Kubernetes)
10. **Port Availability**: Ports 80, 3000, 7860, 8000, 8001 are available on localhost for service access
11. **Image Registry**: Using local Docker images (imagePullPolicy: Never) to avoid external registry setup
12. **No Persistent Volumes**: Application is stateless, all persistent data stored in external Neon database (no PersistentVolumeClaims needed)
13. **Single Replica**: Initial deployment uses 1 replica per service for simplicity (scalability not required for Phase IV)
14. **LoadBalancer Support**: Docker Desktop Kubernetes provides LoadBalancer service support via localhost (simpler than Ingress controller)

## Dependencies

### External Dependencies
- **Docker Desktop**: Required for local Kubernetes cluster, provides docker engine for building images
- **Neon PostgreSQL**: External database dependency (unchanged from Phase II-III), must remain accessible
- **OpenAI API**: Required for chatbot functionality (Phase III feature), accessed via OPENAI_API_KEY in Secret
- **GitHub/Google OAuth**: Required for user authentication (Phase II feature), credentials stored in Secret

### Internal Dependencies
- **Phase I Codebase**: Console application must remain functional (no changes required)
- **Phase II Codebase**: FastAPI backend, Next.js frontend, SQLModel models, Better Auth configuration
- **Phase III Codebase**: MCP server implementation, OpenAI Agents SDK integration, ChatKit UI components
- **Project Configuration**: `.env` files with valid credentials, `pyproject.toml` with dependencies, `package.json` with Next.js configuration

### Technical Dependencies
- **Base Images**: `python:3.12-slim` for backend, `node:20-alpine` for frontend (pulled from Docker Hub on first build)
- **Build Tools**: UV package manager for Python dependencies, npm for Node.js dependencies
- **Health Check Requirement**: Backend `/health` endpoint must be implemented before deployment (add if missing)
- **Next.js Configuration**: `output: 'standalone'` must be set in `next.config.js` for optimal Docker image size

### Tooling Dependencies
- **kubectl**: CLI tool for Kubernetes operations (bundled with Docker Desktop)
- **Docker CLI**: For building images and running containers (bundled with Docker Desktop)
- **Helm** [BONUS]: Package manager for Kubernetes, optional for bonus feature

## Out of Scope (Phase IV)

The following items are explicitly excluded from Phase IV requirements:

- **Remote Kubernetes Deployment**: Cloud deployment (DigitalOcean DOKS, GKE, AKS, EKS) deferred to Phase V
- **Persistent Volumes**: No StatefulSets or PersistentVolumeClaims needed (database is external)
- **Ingress Controller**: Using LoadBalancer instead of Ingress for simplicity in local environment
- **Horizontal Pod Autoscaling (HPA)**: Fixed replica count of 1, no autoscaling based on metrics
- **Service Mesh**: No Istio, Linkerd, or similar service mesh implementations
- **CI/CD Pipelines**: GitHub Actions or other automation deferred to Phase V
- **Monitoring and Logging**: No Prometheus, Grafana, ELK stack, or distributed tracing setup
- **Database Migration in Cluster**: Neon database remains external, no in-cluster PostgreSQL deployment
- **Multi-Environment Configuration**: Single environment (local), no separate dev/staging/production configurations
- **TLS/SSL Certificates**: No HTTPS setup, using HTTP for local development
- **Network Policies**: No Kubernetes NetworkPolicies for traffic restrictions
- **Pod Security Policies**: Basic security context only (runAsNonRoot), no advanced pod security standards
- **Custom Operators**: No custom Kubernetes operators or CRDs
- **GitOps Tools**: No ArgoCD, Flux, or similar GitOps deployment workflows
- **Backup and Disaster Recovery**: No backup strategies for Kubernetes resources or database

## Technical Constraints

1. **Kubernetes Version**: Must work with Kubernetes v1.28+ (Docker Desktop default version)
2. **Image Architecture**: Images must support amd64 architecture (ARM64/M1 Mac compatibility is bonus)
3. **Startup Time**: Backend must start and pass startup probe within 5 minutes (failureThreshold: 30 × periodSeconds: 5 = 150 seconds max)
4. **Memory Limits**: Backend limited to 500Mi, frontend to 512Mi to fit in typical development machine constraints
5. **Single Namespace**: All resources must be deployed to `taskflow` namespace (no cross-namespace dependencies)
6. **Environment Variable Limit**: ConfigMap and Secret combined must not exceed 1MB total size (Kubernetes limit)
7. **Label Naming**: All labels must follow Kubernetes naming conventions (alphanumeric, dash, dot, underscore only)
8. **Port Conflicts**: Services must use non-conflicting ports (avoid 80 if Apache/nginx already running on host)
9. **File Path Limits**: Docker build context must not include large directories (.git, node_modules must be in .dockerignore)
10. **Health Check Timeout**: Probes must complete within timeoutSeconds: 5 to avoid false failures

## Non-Functional Requirements

1. **Reliability**: Pods must automatically restart on failure (default Kubernetes behavior), maintain service availability during pod restarts
2. **Security**: Containers must run as non-root users, secrets must be base64-encoded, sensitive values not logged or exposed in plain text
3. **Performance**: Application must perform identically to local development (no noticeable latency increase from containerization)
4. **Maintainability**: Kubernetes manifests must be human-readable YAML, clearly commented, organized by resource type in separate files
5. **Portability**: Docker images must be reproducible across different machines, multi-stage builds must use explicit versions for base images
6. **Documentation**: README must include clear setup instructions, deployment commands, troubleshooting steps, verification commands
7. **Observability**: Logs must be accessible via `kubectl logs`, pod status visible via `kubectl get pods`, events visible via `kubectl describe`
8. **Scalability**: While single replica initially, deployment structure must support scaling via `kubectl scale deployment` without code changes
9. **Configuration Management**: Secrets must not be committed to git, ConfigMap values must be environment-appropriate, sensitive values in .env.example should show format but not actual values
10. **Resource Efficiency**: Images should use Alpine or slim variants to minimize size, multi-stage builds must exclude development dependencies from final images
