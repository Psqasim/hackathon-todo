# Data Model: Infrastructure Entities for Kubernetes Deployment

**Feature**: 004-k8s-deployment
**Created**: 2026-02-03
**Purpose**: Define infrastructure entities, their attributes, relationships, and state transitions

---

## Overview

This document defines the **infrastructure entities** (not application data models) used in Phase IV Kubernetes deployment. These entities represent containerized artifacts, Kubernetes resources, and their orchestration.

---

## Entity Catalog

### 1. Docker Image (Backend)

**Description**: Container artifact containing FastAPI application, MCP server, Python runtime, and dependencies

**Attributes**:
```yaml
name: taskflow-backend
tag: latest
base_image: python:3.12-slim
size_constraint: <500MB
exposed_ports:
  - 7860  # FastAPI HTTP
  - 8001  # MCP server
layers:
  - builder:
      purpose: "Install dependencies with UV"
      includes: [pyproject.toml, uv.lock, .venv/]
  - runtime:
      purpose: "Run application"
      includes: [.venv/, src/, scripts/start-backend.sh]
user:
  name: appuser
  uid: 1000
  gid: 1000
security:
  run_as_non_root: true
  read_only_root_filesystem: false
entrypoint: ["sh", "scripts/start-backend.sh"]
```

**Relationships**:
- **Used by**: Backend Deployment (Kubernetes)
- **Depends on**: Base image `python:3.12-slim` (Docker Hub)
- **Contains**: Application source from `backend/src/`, dependencies from `pyproject.toml`

**Validation**:
- `docker images taskflow-backend:latest` shows size <500MB
- `docker run --rm taskflow-backend:latest id` returns `uid=1000(appuser)`
- `docker run -p 7860:7860 taskflow-backend:latest` responds to `http://localhost:7860/health`

**State Transitions**:
```
[Source Code] → [Build] → [Image Created] → [Pushed to Registry] → [Pulled by K8s]
                    ↓
              [Build Failed] → [Debug] → [Rebuild]
```

---

### 2. Docker Image (Frontend)

**Description**: Container artifact containing Next.js standalone output, static assets, and Node.js runtime

**Attributes**:
```yaml
name: taskflow-frontend
tag: latest
base_image: node:20-alpine
size_constraint: <300MB
exposed_ports:
  - 3000  # Next.js HTTP
layers:
  - dependencies:
      purpose: "Install npm dependencies"
      includes: [package.json, package-lock.json, node_modules/]
  - builder:
      purpose: "Build Next.js application"
      includes: [source_code, .next/]
  - runtime:
      purpose: "Run standalone server"
      includes: [.next/standalone/, .next/static/, public/]
user:
  name: nodejs
  uid: 1000
  gid: 1000
security:
  run_as_non_root: true
  read_only_root_filesystem: false
entrypoint: ["node", "server.js"]
environment:
  NEXT_PUBLIC_API_URL: "Injected from ConfigMap"
```

**Relationships**:
- **Used by**: Frontend Deployment (Kubernetes)
- **Depends on**: Base image `node:20-alpine` (Docker Hub)
- **Contains**: Next.js standalone bundle from `frontend/.next/standalone/`

**Validation**:
- `docker images taskflow-frontend:latest` shows size <300MB
- `docker run --rm taskflow-frontend:latest id` returns `uid=1000(nodejs)`
- `docker run -p 3000:3000 taskflow-frontend:latest` responds to `http://localhost:3000`

**State Transitions**:
```
[Source Code] → [npm ci] → [npm build] → [Standalone] → [Image Created] → [K8s Pull]
                    ↓             ↓
              [Deps Failed]  [Build Failed] → [Debug] → [Rebuild]
```

---

### 3. Namespace

**Description**: Kubernetes logical boundary isolating TaskFlow resources from other cluster workloads

**Attributes**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: taskflow
  labels:
    app: taskflow
    phase: "4"
    environment: local
```

**Relationships**:
- **Contains**: All TaskFlow Kubernetes resources (Deployments, Services, ConfigMaps, Secrets)
- **Isolates**: Resources from other namespaces (logical separation)
- **Enables**: Resource quotas, network policies, RBAC scopes (not used in Phase IV)

**Validation**:
- `kubectl get namespace taskflow` shows STATUS=Active
- `kubectl config view --minify | grep namespace` shows `namespace: taskflow`

**State Transitions**:
```
[YAML Applied] → [Active] → [Terminating] → [Deleted]
                    ↓
              [Error] → [Investigate] → [Recreate]
```

---

### 4. ConfigMap

**Description**: Kubernetes resource storing non-sensitive configuration as key-value pairs

**Attributes**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: taskflow-config
  namespace: taskflow
data:
  JWT_ALGORITHM: "HS256"
  JWT_EXPIRATION_DAYS: "7"
  BACKEND_URL: "http://backend-service:8000"
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
  MCP_BACKEND_URL: "http://localhost:8001"
  LOG_LEVEL: "info"
```

**Relationships**:
- **Referenced by**: Backend Deployment (envFrom), Frontend Deployment (env)
- **Injected as**: Environment variables in pods
- **Stored**: Plain text (not encoded)

**Validation**:
- `kubectl get configmap taskflow-config -o yaml` shows plain text values
- `kubectl exec <backend-pod> -- env | grep JWT_ALGORITHM` returns `HS256`

**State Transitions**:
```
[YAML Applied] → [Created] → [Referenced by Pods] → [Updated] → [Pods Restarted]
                    ↓
              [Deleted] → [Pods Fail] → [Recreate ConfigMap]
```

---

### 5. Secret

**Description**: Kubernetes resource storing sensitive credentials with base64 encoding

**Attributes**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: taskflow-secrets
  namespace: taskflow
type: Opaque
data:
  DATABASE_URL: "<base64-encoded Neon connection string>"
  JWT_SECRET_KEY: "<base64-encoded secret>"
  OPENAI_API_KEY: "<base64-encoded API key>"
  GOOGLE_CLIENT_ID: "<base64-encoded OAuth client ID>"
  GOOGLE_CLIENT_SECRET: "<base64-encoded OAuth secret>"
  GITHUB_CLIENT_ID: "<base64-encoded OAuth client ID>"
  GITHUB_CLIENT_SECRET: "<base64-encoded OAuth secret>"
```

**Relationships**:
- **Referenced by**: Backend Deployment (envFrom)
- **Injected as**: Environment variables in backend pods
- **Generated by**: `scripts/generate-secrets.sh` from `.env` file
- **Stored**: Base64-encoded (NOT encrypted by default)

**Validation**:
- `kubectl get secret taskflow-secrets -o yaml` shows base64 values
- `kubectl describe secret taskflow-secrets` hides values, shows keys only
- `kubectl exec <backend-pod> -- env | grep DATABASE_URL` shows decoded value

**State Transitions**:
```
[.env File] → [generate-secrets.sh] → [secrets.yaml] → [Applied] → [Mounted in Pods]
                                           ↓
                                    [Git Ignored] (security)
```

**Security Notes**:
- NEVER commit `k8s/secrets.yaml` to git
- Provide `k8s/secrets.yaml.example` with placeholders
- Base64 is encoding, not encryption (Kubernetes encrypts at rest if configured)

---

### 6. Backend Deployment

**Description**: Kubernetes resource managing backend pod lifecycle with replicas, health probes, and resource limits

**Attributes**:
```yaml
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
        imagePullPolicy: Never  # Use local image
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

**Relationships**:
- **Creates**: Backend Pods (replicas=1)
- **References**: Docker Image `taskflow-backend:latest`, ConfigMap `taskflow-config`, Secret `taskflow-secrets`
- **Managed by**: Kubernetes ReplicaSet (automatically created)
- **Selected by**: Backend Service (via label selector)

**Validation**:
- `kubectl get deployment backend-deployment` shows READY=1/1
- `kubectl get pods -l app=taskflow-backend` shows 1 pod Running
- `kubectl describe deployment backend-deployment` shows events, replica status

**State Transitions**:
```
[YAML Applied] → [ReplicaSet Created] → [Pod Scheduling] → [Image Pull] → [Container Creating]
                                                                ↓
                                                          [Container Running]
                                                                ↓
                                            [Startup Probe] → [Liveness Probe] → [Readiness Probe]
                                                  ↓                 ↓                   ↓
                                            [Failed] →      [Failed] →          [Failed] →
                                         [Restart Pod]  [Restart Container] [Remove from Endpoints]
```

---

### 7. Backend Service

**Description**: Kubernetes ClusterIP Service routing internal traffic to backend pods

**Attributes**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: taskflow
  labels:
    app: taskflow-backend
spec:
  type: ClusterIP  # Internal only
  selector:
    app: taskflow-backend
  ports:
  - name: http
    protocol: TCP
    port: 8000        # External port (within cluster)
    targetPort: 7860  # Container port
```

**Relationships**:
- **Routes to**: Backend Pods (selected by `app=taskflow-backend` label)
- **Accessed by**: Frontend Pods (via `http://backend-service:8000`)
- **Provides**: Stable DNS name (`backend-service.taskflow.svc.cluster.local`)
- **Load balances**: Across multiple backend replicas (if scaled)

**Validation**:
- `kubectl get svc backend-service` shows ClusterIP assigned
- `kubectl describe svc backend-service` shows Endpoints (pod IPs)
- `kubectl exec <frontend-pod> -- curl http://backend-service:8000/health` returns 200 OK

**State Transitions**:
```
[YAML Applied] → [Service Created] → [ClusterIP Assigned] → [Endpoints Discovered] → [Ready]
                                            ↓
                                    [No Endpoints] → [Pods Not Ready] → [Check Deployment]
```

---

### 8. Frontend Deployment

**Description**: Kubernetes resource managing frontend pod lifecycle with replicas, health probes, and resource limits

**Attributes**:
```yaml
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
          timeoutSeconds: 5
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
```

**Relationships**:
- **Creates**: Frontend Pods (replicas=1)
- **References**: Docker Image `taskflow-frontend:latest`, ConfigMap `taskflow-config`
- **Connects to**: Backend Service via `NEXT_PUBLIC_API_URL`
- **Selected by**: Frontend Service (via label selector)

**Validation**:
- `kubectl get deployment frontend-deployment` shows READY=1/1
- `kubectl get pods -l app=taskflow-frontend` shows 1 pod Running
- `kubectl logs -l app=taskflow-frontend` shows Next.js server started

**State Transitions**: (Same as Backend Deployment, see §6)

---

### 9. Frontend Service

**Description**: Kubernetes LoadBalancer Service routing external traffic to frontend pods

**Attributes**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: taskflow
  labels:
    app: taskflow-frontend
spec:
  type: LoadBalancer  # External access
  selector:
    app: taskflow-frontend
  ports:
  - name: http
    protocol: TCP
    port: 80          # External port (public)
    targetPort: 3000  # Container port
```

**Relationships**:
- **Routes to**: Frontend Pods (selected by `app=taskflow-frontend` label)
- **Accessed by**: Users via browser (external traffic)
- **Provides**: External IP (LoadBalancer) or `localhost` on Docker Desktop
- **Exposes**: TaskFlow UI to the internet (or local network)

**Validation**:
- `kubectl get svc frontend-service` shows EXTERNAL-IP (localhost on Docker Desktop)
- `curl http://localhost` (or LoadBalancer IP) returns HTML
- Browser access to `http://localhost` shows TaskFlow homepage

**State Transitions**:
```
[YAML Applied] → [Service Created] → [LoadBalancer Provisioning] → [External IP Assigned] → [Ready]
                                            ↓                              ↓
                                    [Pending] (waiting)              [localhost] (Docker Desktop)
```

**Docker Desktop Specifics**:
- LoadBalancer type is supported (unlike Minikube which needs Ingress)
- External IP resolves to `localhost` automatically
- No need for `kubectl port-forward` or Ingress controller

---

### 10. Health Probe

**Description**: Kubernetes mechanism for monitoring pod health via HTTP requests to designated endpoints

**Types and Purposes**:

#### Startup Probe
**Purpose**: Handle slow container initialization
**Behavior**: Disables liveness/readiness until first success
**Configuration**:
```yaml
startupProbe:
  httpGet:
    path: /health
    port: 7860
  periodSeconds: 5
  failureThreshold: 30  # Max 150 seconds
```
**State**: Unknown → Success (continue) | Failure (restart pod)

#### Liveness Probe
**Purpose**: Detect deadlocked or hung processes
**Behavior**: Restart container if probe fails repeatedly
**Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 7860
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3  # Restart after 3 failures
```
**State**: Success (continue) | Failure (restart container)

#### Readiness Probe
**Purpose**: Determine if pod should receive traffic
**Behavior**: Remove from Service endpoints if probe fails
**Configuration**:
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 7860
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3  # Remove after 3 failures
```
**State**: Success (add to endpoints) | Failure (remove from endpoints)

**Relationships**:
- **Embedded in**: Deployment specs (container level)
- **Executed by**: Kubelet (node agent)
- **Triggers**: Container restarts, endpoint removal, traffic routing

**State Transitions**:
```
[Pod Start] → [Startup Probe] → [First Success] → [Liveness & Readiness Begin]
                  ↓                                        ↓
            [Repeated Failures] →                   [Success] →
            [Restart Pod]                       [Add to Service Endpoints]
                                                        ↓
                                                [Liveness Failure] →
                                                [Restart Container]
                                                        ↓
                                                [Readiness Failure] →
                                                [Remove from Endpoints]
```

---

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      Namespace: taskflow                         │
│                                                                  │
│  ┌─────────────┐         ┌──────────────────────────────────┐  │
│  │ ConfigMap   │────────>│ Backend Deployment (replica=1)   │  │
│  │ (non-secret)│         │  - Image: taskflow-backend:latest│  │
│  └─────────────┘         │  - Resources: 256Mi-500Mi        │  │
│         │                │  - Probes: startup/live/ready    │  │
│         │                │  - SecurityContext: UID 1000     │  │
│  ┌─────────────┐         └────────────┬─────────────────────┘  │
│  │ Secret      │                      │                         │
│  │ (base64)    │──────────────────────┘                         │
│  └─────────────┘                      │                         │
│         │                              ▼                         │
│         │                      ┌───────────────┐                │
│         │                      │ Backend Pod   │                │
│         │                      │ (Running)     │                │
│         │                      └───────┬───────┘                │
│         │                              │                         │
│         │                              ▼                         │
│         │                      ┌───────────────────┐            │
│         │                      │ Backend Service   │            │
│         │                      │ (ClusterIP:8000)  │            │
│         │                      └─────────┬─────────┘            │
│         │                                │                       │
│         │                                │ http://backend-       │
│         │                                │ service:8000          │
│         │                                │                       │
│         │                                ▼                       │
│  ┌─────────────┐         ┌──────────────────────────────────┐  │
│  │ ConfigMap   │────────>│ Frontend Deployment (replica=1)  │  │
│  │ (API_URL)   │         │  - Image: taskflow-frontend:...  │  │
│  └─────────────┘         │  - Resources: 256Mi-512Mi        │  │
│                          │  - Probes: liveness/readiness    │  │
│                          │  - SecurityContext: UID 1000     │  │
│                          └────────────┬─────────────────────┘  │
│                                       │                         │
│                                       ▼                         │
│                               ┌───────────────┐                │
│                               │ Frontend Pod  │                │
│                               │ (Running)     │                │
│                               └───────┬───────┘                │
│                                       │                         │
│                                       ▼                         │
│                               ┌────────────────────┐           │
│                               │ Frontend Service   │           │
│                               │ (LoadBalancer:80)  │           │
│                               └────────┬───────────┘           │
│                                        │                        │
└────────────────────────────────────────┼────────────────────────┘
                                         │
                                         ▼
                                   ┌──────────┐
                                   │ Browser  │
                                   │ (User)   │
                                   └──────────┘
                                http://localhost

┌─────────────────────────────────────────────────────────────────┐
│                    Docker Images (Local)                        │
│                                                                 │
│  ┌───────────────────────────┐  ┌──────────────────────────┐  │
│  │ taskflow-backend:latest   │  │ taskflow-frontend:latest │  │
│  │ (python:3.12-slim)        │  │ (node:20-alpine)         │  │
│  │ Size: <500MB              │  │ Size: <300MB             │  │
│  │ UID: 1000 (appuser)       │  │ UID: 1000 (nodejs)       │  │
│  └───────────┬───────────────┘  └──────────┬───────────────┘  │
│              │                              │                  │
│              └──────────────┬───────────────┘                  │
│                             │                                  │
│                             ▼                                  │
│                      imagePullPolicy: Never                    │
│                      (use local images)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Relationships Summary

1. **Namespace** contains all Kubernetes resources (isolation boundary)
2. **ConfigMap** & **Secret** inject configuration into **Deployments** (envFrom, env)
3. **Deployments** create **Pods** (replica management)
4. **Pods** run **Docker Images** (container execution)
5. **Services** route traffic to **Pods** (label selectors)
6. **Backend Service** (ClusterIP) is internal-only, accessed by **Frontend Pods**
7. **Frontend Service** (LoadBalancer) is external-facing, accessed by **Users**
8. **Health Probes** monitor **Pods**, trigger restarts or endpoint changes

---

## Critical Constraints

| Constraint | Entity | Value | Enforcement |
|------------|--------|-------|-------------|
| Image Size | Backend Image | <500MB | Build fails if exceeded |
| Image Size | Frontend Image | <300MB | Build fails if exceeded |
| User UID | Both Images | 1000 | Dockerfile USER directive |
| Security Context | Both Deployments | runAsNonRoot: true | K8s admission controller |
| Resource Requests | Backend Pod | 256Mi/250m | K8s scheduler |
| Resource Limits | Backend Pod | 500Mi/500m | K8s OOMKiller/CPU throttle |
| Resource Requests | Frontend Pod | 256Mi/250m | K8s scheduler |
| Resource Limits | Frontend Pod | 512Mi/500m | K8s OOMKiller/CPU throttle |
| Startup Timeout | Backend Pod | 150s max | startupProbe.failureThreshold |
| Liveness Failure | Both Pods | 30s (3×10s) | Container restart |
| Readiness Failure | Both Pods | 15s (3×5s) | Remove from endpoints |

---

**Status**: Data model complete, defines all infrastructure entities
**Next**: Create contracts/ for API specifications
