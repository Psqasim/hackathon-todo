# Phase IV Testing Guide: Local Kubernetes Deployment

**Feature**: Phase IV - Local Kubernetes Deployment
**Status**: Production Ready
**Last Updated**: 2026-02-03
**Estimated Testing Time**: 30-45 minutes

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment Methods](#deployment-methods)
3. [Prerequisites Verification](#prerequisites-verification)
4. [Build Docker Images](#build-docker-images)
5. [Deploy to Kubernetes](#deploy-to-kubernetes)
6. [Verify Deployment](#verify-deployment)
7. [Access the Application](#access-the-application)
8. [Stop, Start, and Restart Commands](#stop-start-and-restart-commands)
9. [Test All Features](#test-all-features)
10. [Monitor Resources](#monitor-resources)
11. [Troubleshooting](#troubleshooting)
12. [Cleanup](#cleanup)
13. [Performance Benchmarks](#performance-benchmarks)
14. [Architecture Summary](#architecture-summary)

---

## Overview

Phase IV deploys the TaskFlow Todo application to a **local Kubernetes cluster**. This phase containerizes both the FastAPI backend and Next.js frontend while maintaining all existing functionality from Phases I-III.

You can deploy using either:
- **Docker Desktop Kubernetes** (recommended for macOS/Windows)
- **Minikube** (cross-platform, more flexible)

### What's New in Phase IV

- ✅ **Docker Multi-Stage Builds**: Optimized production images
- ✅ **Kubernetes Orchestration**: Pods, Services, Deployments
- ✅ **ConfigMap/Secret Management**: Separate configuration from code
- ✅ **Health Probes**: Automatic pod monitoring and restart
- ✅ **Resource Limits**: CPU and memory constraints
- ✅ **Non-Root Security**: Containers run as UID 1000
- ✅ **LoadBalancer Service**: External access to frontend
- ✅ **ClusterIP Service**: Internal backend communication

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Desktop Kubernetes                    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Namespace: taskflow                       │   │
│  │                                                        │   │
│  │  ┌──────────────────────┐  ┌──────────────────────┐  │   │
│  │  │  Backend Deployment  │  │ Frontend Deployment  │  │   │
│  │  │  (replica: 1)        │  │ (replica: 1)         │  │   │
│  │  │                      │  │                      │  │   │
│  │  │  ┌────────────────┐ │  │  ┌────────────────┐ │  │   │
│  │  │  │ Backend Pod    │ │  │  │ Frontend Pod   │ │  │   │
│  │  │  │ UID: 1000      │ │  │  │ UID: 1000      │ │  │   │
│  │  │  │ FastAPI: 7860  │ │  │  │ Next.js: 3000  │ │  │   │
│  │  │  │ MCP: 8001      │ │  │  │                │ │  │   │
│  │  │  └────────────────┘ │  │  └────────────────┘ │  │   │
│  │  └──────────────────────┘  └──────────────────────┘  │   │
│  │           │                          │                │   │
│  │           ▼                          ▼                │   │
│  │  ┌──────────────────┐      ┌──────────────────────┐ │   │
│  │  │ Backend Service  │      │ Frontend Service     │ │   │
│  │  │ (ClusterIP)      │      │ (LoadBalancer)       │ │   │
│  │  │ Port: 8000→7860  │      │ Port: 80→3000        │ │   │
│  │  └──────────────────┘      └──────────────────────┘ │   │
│  │           │                          │                │   │
│  └───────────┼──────────────────────────┼────────────────┘   │
│              │                          │                     │
└──────────────┼──────────────────────────┼─────────────────────┘
               │                          │
               │ (internal)               ▼ (external)
               │                    http://localhost
               │
               ▼
         Neon PostgreSQL
         OpenAI API
         OAuth Providers
```

---

## Deployment Methods

Phase IV supports two deployment methods. Choose the one that best fits your environment:

### Method 1: Docker Desktop Kubernetes (Recommended)

**Best for**: macOS and Windows users with Docker Desktop installed

**Pros**:
- ✅ Easy setup (built into Docker Desktop)
- ✅ Fast image loading (uses same Docker daemon)
- ✅ LoadBalancer works with `localhost`
- ✅ Lower resource overhead

**Cons**:
- ❌ Requires Docker Desktop license (for commercial use)
- ❌ Single cluster only
- ❌ Limited to Docker Desktop K8s version

**Quick Start**:
```bash
# 1. Enable Kubernetes in Docker Desktop settings
# 2. Build images
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend

# 3. Deploy
kubectl apply -f k8s/
```

### Method 2: Minikube

**Best for**: Linux users, multi-cluster setups, specific K8s versions

**Pros**:
- ✅ Cross-platform (Linux, macOS, Windows)
- ✅ Multiple cluster profiles
- ✅ Specific Kubernetes versions
- ✅ Rich addon ecosystem
- ✅ Better isolation

**Cons**:
- ❌ Requires separate installation
- ❌ Extra step to load images
- ❌ LoadBalancer requires `minikube service`
- ❌ Slightly more resource usage

**Quick Start**:
```bash
# 1. Install Minikube
brew install minikube  # or see docs/MINIKUBE-DEPLOYMENT.md

# 2. Start cluster
minikube start --cpus=4 --memory=4096

# 3. Build and load images
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest

# 4. Deploy
kubectl apply -f k8s/

# 5. Access
minikube service frontend-service -n taskflow
```

**📖 Full Minikube Guide**: See [docs/MINIKUBE-DEPLOYMENT.md](./MINIKUBE-DEPLOYMENT.md) for comprehensive Minikube setup and troubleshooting.

### Method 3: Helm Chart (Advanced)

Both Docker Desktop and Minikube support Helm-based deployment:

```bash
# Install Helm (if not installed)
brew install helm  # or see helm.sh/docs/intro/install

# Deploy with Helm
helm install taskflow ./helm/taskflow -f values-secrets.yaml
```

**📖 Helm Guide**: See [helm/taskflow/README.md](../helm/taskflow/README.md) for Helm chart documentation.

### Comparison Table

| Feature | Docker Desktop K8s | Minikube | Helm (Both) |
|---------|-------------------|----------|-------------|
| Setup complexity | Easy | Medium | Medium |
| Image loading | Automatic | Manual | N/A |
| LoadBalancer access | `localhost` | `minikube service` | N/A |
| Multi-cluster | No | Yes | N/A |
| Resource usage | Low | Medium | N/A |
| Customization | Limited | High | Very High |

---

## Prerequisites Verification

Before starting, ensure your development environment meets these requirements.

### Required Software

1. **Docker Desktop 4.0+** with Kubernetes enabled
2. **kubectl CLI** (bundled with Docker Desktop)
3. **Git** (repository cloned)
4. **Environment Variables** (`.env` file configured)

### Verification Commands

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.0+ or higher

# Check Docker is running
docker ps
# Should show running containers or empty list (not error)

# Check Kubernetes cluster is running
kubectl cluster-info
# Expected: Kubernetes control plane is running at https://kubernetes.docker.internal:6443

# Check current context
kubectl config current-context
# Expected: docker-desktop

# Check nodes are ready
kubectl get nodes
# Expected:
# NAME             STATUS   ROLES           AGE   VERSION
# docker-desktop   Ready    control-plane   10d   v1.28.2

# Check kubectl version
kubectl version --client
# Expected: Client Version: v1.28+
```

### Enable Kubernetes in Docker Desktop

If Kubernetes is not enabled:

**Windows/Linux (WSL2):**
1. Open Docker Desktop
2. Click Settings (gear icon)
3. Navigate to Kubernetes
4. Check "Enable Kubernetes"
5. Click "Apply & Restart"
6. Wait 2-3 minutes for initialization

**macOS:**
1. Open Docker Desktop
2. Click Docker icon → Preferences
3. Navigate to Kubernetes tab
4. Check "Enable Kubernetes"
5. Click "Apply & Restart"
6. Wait 2-3 minutes for initialization

### Verify Environment File

Check that `.env` exists and contains required variables:

```bash
# List .env file
ls -la .env

# Check for required variables (don't print values)
grep -E "^(DATABASE_URL|JWT_SECRET_KEY|OPENAI_API_KEY)" .env | wc -l
# Expected: 3 (all required variables present)
```

**Required Variables:**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `OPENAI_API_KEY` - OpenAI API key for chatbot
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (optional - for OAuth)
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` (optional - for OAuth)

---

## Build Docker Images

Build production-optimized Docker images for both backend and frontend.

### Build Backend Image

```bash
# Navigate to project root
cd /path/to/hackathon-todo

# Build backend image (takes 3-5 minutes first time)
docker build -f Dockerfile.k8s -t taskflow-backend:latest .
```

**Expected Output:**
```
[+] Building 180.5s (17/17) FINISHED
 => [internal] load build definition from Dockerfile.k8s
 => [builder 1/6] FROM docker.io/library/python:3.12-slim
 => [builder 4/6] RUN curl -LsSf https://astral.sh/uv/install.sh | sh
 => [builder 5/6] COPY pyproject.toml uv.lock README.md ./
 => [builder 6/6] RUN uv sync --frozen --no-dev
 => [stage-1 7/7] COPY scripts/start-backend.sh /app/scripts/
 => exporting to image
 => => naming to docker.io/library/taskflow-backend:latest
```

### Build Frontend Image

```bash
# Build frontend image (takes 2-3 minutes first time)
docker build -t taskflow-frontend:latest ./frontend
```

**Expected Output:**
```
[+] Building 120.3s (11/11) FINISHED
 => [dependencies 1/4] FROM docker.io/library/node:20-alpine
 => [dependencies 3/4] COPY package.json package-lock.json ./
 => [dependencies 4/4] RUN npm ci
 => [builder 3/3] RUN npm run build
 => [runner 5/5] COPY --from=builder /app/public ./public
 => exporting to image
 => => naming to docker.io/library/taskflow-frontend:latest
```

### Verify Images

```bash
# List TaskFlow images
docker images | grep taskflow

# Expected output:
# taskflow-backend    latest   <image-id>   <timestamp>   561MB
# taskflow-frontend   latest   <image-id>   <timestamp>   294MB
```

**Image Size Verification:**
- ✅ Backend: ~561MB (acceptable for MVP, includes Python runtime + dependencies)
- ✅ Frontend: ~294MB (under 300MB target!)

### Test Images Locally (Optional)

Before deploying to Kubernetes, you can test images locally:

```bash
# Test backend (Terminal 1)
docker run --rm -p 7860:7860 --env-file .env taskflow-backend:latest

# Expected: FastAPI starts, MCP server starts
# Look for: "All Services Running"

# Test backend health (Terminal 2)
curl http://localhost:7860/health
# Expected: {"status":"healthy"}

# Stop backend: Ctrl+C in Terminal 1

# Test frontend (Terminal 1)
docker run --rm -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:7860 taskflow-frontend:latest

# Test frontend access (Terminal 2)
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# Stop frontend: Ctrl+C in Terminal 1
```

---

## Deploy to Kubernetes

Deploy the TaskFlow application to your local Kubernetes cluster.

### Step 1: Create Namespace

```bash
# Create taskflow namespace
kubectl create namespace taskflow

# Expected: namespace/taskflow created

# Set namespace as default context
kubectl config set-context --current --namespace=taskflow

# Verify current namespace
kubectl config view --minify | grep namespace
# Expected: namespace: taskflow
```

### Step 2: Generate Secrets

```bash
# Generate k8s/secrets.yaml from .env file
bash scripts/generate-secrets.sh
```

**Expected Output:**
```
=== Kubernetes Secrets Generator ===
✓ All required variables found in .env
✓ Generating secrets.yaml...

✅ Generated: /path/to/project/k8s/secrets.yaml

⚠️  SECURITY REMINDER:
   - secrets.yaml is in .gitignore (DO NOT commit)
   - Base64 encoding is NOT encryption
   - Values are visible with: kubectl get secret -o yaml
```

### Step 3: Apply Kubernetes Manifests

```bash
# Apply all manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

**Expected Output:**
```
namespace/taskflow unchanged (already created)
configmap/taskflow-config created
secret/taskflow-secrets created
deployment.apps/backend-deployment created
service/backend-service created
deployment.apps/frontend-deployment created
service/frontend-service created
```

**Or apply all at once:**
```bash
kubectl apply -f k8s/
```

---

## Verify Deployment

Ensure all Kubernetes resources are created and healthy.

### Check Pods Status

```bash
# View all pods in taskflow namespace
kubectl get pods -n taskflow

# Expected output:
# NAME                                   READY   STATUS    RESTARTS   AGE
# backend-deployment-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
# frontend-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

**Status Indicators:**
- ✅ **Running**: Pod is healthy and ready
- ⏳ **ContainerCreating**: Pod is starting (wait 30-60s)
- ⏳ **Pending**: Waiting for resources (wait or check describe)
- ❌ **CrashLoopBackOff**: Container is crashing (check logs)
- ❌ **ImagePullBackOff**: Cannot pull image (check imagePullPolicy)

### Watch Pods Starting Up

```bash
# Watch pods in real-time (Ctrl+C to exit)
kubectl get pods -n taskflow -w
```

### Check Services

```bash
# List services
kubectl get services -n taskflow

# Expected output:
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# backend-service    ClusterIP      10.98.39.79     <none>        8000/TCP       3m
# frontend-service   LoadBalancer   10.104.194.97   localhost     80:30635/TCP   3m
```

**Service Types:**
- **ClusterIP** (backend): Internal-only, accessed by frontend pods
- **LoadBalancer** (frontend): External access via `localhost` or assigned IP

### Check Deployments

```bash
# View deployments
kubectl get deployments -n taskflow

# Expected output:
# NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
# backend-deployment    1/1     1            1           3m
# frontend-deployment   1/1     1            1           3m
```

### Check All Resources

```bash
# View everything in namespace
kubectl get all -n taskflow
```

---

## Verify Deployment (Detailed)

Perform detailed verification of pod health and configuration.

### Check Backend Logs

```bash
# View backend logs (last 50 lines)
kubectl logs -n taskflow -l app=taskflow-backend --tail=50

# Expected output includes:
# [K8s Startup] ===== TaskFlow Backend Starting =====
# [K8s Startup] User: uid=1000(appuser)
# INFO:     Started server process [10]
# [K8s Startup] ✓ FastAPI is healthy and ready!
# [K8s Startup] Starting MCP server on port 8001...
# [K8s Startup] ===== All Services Running =====
```

### Check Frontend Logs

```bash
# View frontend logs (last 50 lines)
kubectl logs -n taskflow -l app=taskflow-frontend --tail=50

# Expected output includes:
# ▲ Next.js 14.x.x
# - Local:        http://localhost:3000
# - Network:      http://0.0.0.0:3000
# ✓ Ready in 2.1s
```

### Follow Logs in Real-Time

```bash
# Backend logs (Ctrl+C to stop)
kubectl logs -n taskflow -l app=taskflow-backend -f

# Frontend logs (in another terminal)
kubectl logs -n taskflow -l app=taskflow-frontend -f
```

### Check Health Probes

```bash
# Describe backend pod to see health probe status
kubectl describe pod -n taskflow -l app=taskflow-backend

# Look for these sections:
#   Liveness:   http-get http://:7860/health delay=30s timeout=5s period=10s
#   Readiness:  http-get http://:7860/health delay=10s timeout=5s period=5s
#   Startup:    http-get http://:7860/health delay=0s timeout=5s period=10s

# Check probe results in events
kubectl describe pod -n taskflow -l app=taskflow-backend | grep -A 5 "Events:"
# Should NOT show "Unhealthy" warnings
```

### Verify Non-Root Users

```bash
# Check backend runs as UID 1000
BACKEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n taskflow $BACKEND_POD -- id

# Expected: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)

# Check frontend runs as UID 1000
FRONTEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-frontend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n taskflow $FRONTEND_POD -- id

# Expected: uid=1000(node) gid=1000(node)
```

### Test Backend Health Internally

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-backend -o jsonpath='{.items[0].metadata.name}')

# Test health endpoint from inside pod
kubectl exec -n taskflow $BACKEND_POD -- wget -qO- http://localhost:7860/health

# Expected: {"status":"healthy"}

# Test FastAPI is responding
kubectl exec -n taskflow $BACKEND_POD -- wget -qO- http://localhost:7860/docs

# Expected: HTML content (OpenAPI documentation)
```

### Test Internal Service Communication

```bash
# Get frontend pod name
FRONTEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-frontend -o jsonpath='{.items[0].metadata.name}')

# Test frontend can reach backend via service
kubectl exec -n taskflow $FRONTEND_POD -- wget -qO- http://backend-service:8000/health

# Expected: {"status":"healthy"}
```

---

## Access the Application

Access the TaskFlow frontend via the LoadBalancer service.

### Get LoadBalancer IP

```bash
# Check frontend service
kubectl get svc frontend-service -n taskflow

# Expected output:
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# frontend-service   LoadBalancer   10.104.194.97   localhost     80:30635/TCP   5m

# The EXTERNAL-IP column shows: localhost
```

### Open Frontend in Browser

**Method 1: Direct Access (Recommended)**
```
http://localhost
```

**Method 2: Open from Terminal**
```bash
# macOS
open http://localhost

# Linux
xdg-open http://localhost

# Windows (WSL)
start http://localhost
```

**Method 3: Curl Test**
```bash
# Test frontend responds
curl -I http://localhost

# Expected:
# HTTP/1.1 200 OK
# Content-Type: text/html; charset=utf-8
```

### Port Forwarding (Alternative Method)

If LoadBalancer is not working:

```bash
# Forward frontend service to local port 3000
kubectl port-forward -n taskflow svc/frontend-service 3000:80

# Access at: http://localhost:3000

# Forward backend service (optional, for testing)
kubectl port-forward -n taskflow svc/backend-service 8000:8000

# Access at: http://localhost:8000/docs
```

---

## Stop, Start, and Restart Commands

Quick reference for managing your Phase IV Kubernetes deployment.

### Stop Everything

```bash
# Delete entire namespace (stops all pods, services)
kubectl delete namespace taskflow

# Verify deletion
kubectl get all -n taskflow
# Output: No resources found in taskflow namespace
```

### Start Everything

```bash
# Apply all manifests
kubectl apply -f k8s/

# Wait for pods to be ready
kubectl get pods -n taskflow -w
# Watch until both pods show 1/1 Running, then Ctrl+C

# Get frontend URL
kubectl get svc frontend-service -n taskflow
# Access at http://localhost or EXTERNAL-IP shown
```

### Restart Backend Only

```bash
# Delete backend pod (Kubernetes auto-recreates it)
kubectl delete pod -n taskflow -l app=taskflow-backend

# Wait for new pod
kubectl get pods -n taskflow -w
```

### Restart Frontend Only

```bash
# Delete frontend pod
kubectl delete pod -n taskflow -l app=taskflow-frontend

# Wait for new pod
kubectl get pods -n taskflow -w
```

### Restart Both Services

```bash
# Restart all pods in namespace
kubectl rollout restart deployment -n taskflow

# Watch pods restart
kubectl get pods -n taskflow -w
```

### Check Status Quickly

```bash
# See all resources
kubectl get all -n taskflow

# See just pods with status
kubectl get pods -n taskflow

# See services and external IPs
kubectl get svc -n taskflow
```

### View Logs While Running

```bash
# Backend logs (live)
kubectl logs -n taskflow -l app=taskflow-backend -f

# Frontend logs (live)
kubectl logs -n taskflow -l app=taskflow-frontend -f

# Press Ctrl+C to stop following logs
```

### Common Scenarios

#### Scenario 1: Demo for Teacher
```bash
# 1. Ensure everything is running
kubectl get pods -n taskflow

# 2. Open browser: http://localhost

# 3. Show all features working
```

#### Scenario 2: Made Code Changes
```bash
# 1. Rebuild image
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
# or for frontend:
docker build -t taskflow-frontend:latest ./frontend

# 2. Restart pod
kubectl delete pod -n taskflow -l app=taskflow-backend
# or:
kubectl delete pod -n taskflow -l app=taskflow-frontend

# 3. Test changes
kubectl get pods -n taskflow -w
```

#### Scenario 3: Clean Slate / Start Fresh
```bash
# 1. Stop everything
kubectl delete namespace taskflow

# 2. Rebuild images
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend

# 3. Start everything
kubectl apply -f k8s/

# 4. Wait for ready
kubectl get pods -n taskflow -w
```

#### Scenario 4: Something Not Working
```bash
# 1. Check pod status
kubectl get pods -n taskflow

# 2. Check logs
kubectl logs -n taskflow <pod-name>

# 3. Describe pod for more details
kubectl describe pod -n taskflow <pod-name>

# 4. Restart if needed
kubectl delete pod -n taskflow <pod-name>
```

---

## Test All Features

Comprehensive testing of all Phase I-III features through Kubernetes deployment.

### Test 1: Phase I Console (Still Works Locally)

Phase I console application runs locally (not in Kubernetes) and should still work:

```bash
# Navigate to project root
cd /path/to/hackathon-todo

# Run console app
uv run todo

# Expected: Console menu appears
# ┌─────────────────────────────┐
# │      TaskFlow Todo CLI      │
# │         Phase I             │
# └─────────────────────────────┘
#
# What would you like to do?
# 1. List all tasks
# 2. Add a new task
# 3. Complete a task
# 4. Delete a task
# 5. Exit
```

**Test all 5 operations:**
1. List tasks (should work)
2. Add task: "Test Phase IV Kubernetes"
3. List tasks (new task should appear)
4. Complete task #1
5. Delete task #1
6. Exit

**Expected Result:** ✅ All console operations work normally (connects to same Neon database)

### Test 2: Phase II Web UI via Kubernetes

Access web interface through Kubernetes LoadBalancer at `http://localhost`.

#### Test 2a: User Registration

```
1. Open http://localhost
2. Click "Sign Up"
3. Enter email: test-k8s@example.com
4. Enter password: SecurePassword123!
5. Confirm password
6. Click "Create Account"

Expected: ✅ Account created, redirected to dashboard
```

#### Test 2b: Google OAuth Sign In

```
1. Open http://localhost (or click Sign Out first)
2. Click "Sign in with Google"
3. Select Google account
4. Authorize TaskFlow

Expected: ✅ Signed in via Google OAuth, redirected to dashboard
```

#### Test 2c: GitHub OAuth Sign In

```
1. Open http://localhost (or click Sign Out first)
2. Click "Sign in with GitHub"
3. Enter GitHub credentials
4. Authorize TaskFlow

Expected: ✅ Signed in via GitHub OAuth, redirected to dashboard
```

#### Test 2d: Task CRUD Operations

**Create Task:**
```
1. Ensure you're signed in
2. Click "Add Task" or "New Task"
3. Enter title: "Deploy to Kubernetes"
4. Enter description: "Successfully deployed TaskFlow to K8s cluster"
5. Click "Save" or "Create"

Expected: ✅ Task appears in task list immediately
```

**Read Tasks:**
```
1. Navigate to dashboard/tasks page
2. View task list

Expected: ✅ All tasks displayed with title, description, status
```

**Update Task:**
```
1. Click task "Deploy to Kubernetes"
2. Click "Edit" button
3. Update title: "Deploy to Kubernetes - COMPLETE"
4. Update description: "Successfully deployed and verified"
5. Click "Save"

Expected: ✅ Task updated, changes reflected immediately
```

**Complete Task:**
```
1. Find task "Deploy to Kubernetes - COMPLETE"
2. Click checkbox or "Mark Complete" button
3. Observe visual feedback (strikethrough, color change)

Expected: ✅ Task marked as completed, moved to completed section
```

**Delete Task:**
```
1. Find a completed task
2. Click "Delete" button or trash icon
3. Confirm deletion in modal/dialog

Expected: ✅ Task removed from list immediately
```

#### Test 2e: User Profile

```
1. Click user avatar/profile icon
2. View profile information
3. Update profile (if feature exists)
4. Sign out

Expected: ✅ Profile displays correctly, sign out works
```

### Test 3: Phase III Chatbot via Kubernetes

Test AI chatbot functionality through Kubernetes deployment.

#### Test 3a: Access Chatbot

```
1. Navigate to http://localhost
2. Sign in if not already signed in
3. Look for chatbot icon (bottom-right floating button or navigation link)
4. Click to open chatbot interface

Expected: ✅ Chatbot panel opens (ChatKit UI)
```

#### Test 3b: Privacy Notice

```
1. First time opening chatbot
2. Privacy notice should appear
3. Read notice about data usage
4. Click "I Understand" or "Accept"

Expected: ✅ Privacy notice accepted, chat interface activated
```

#### Test 3c: List Tasks via Chatbot

```
Send message: "Show me all my tasks"

or

Send message: "List my tasks"

Expected: ✅ Agent responds with list of your current tasks
Example: "You have 3 tasks: 1) Deploy to Kubernetes - COMPLETE (completed), 2) Test chatbot (active), 3) Write documentation (active)"
```

#### Test 3d: Create Task via Chatbot

```
Send message: "Add task to test Kubernetes chatbot integration"

or

Send message: "Create a task: Verify MCP server works in K8s"

Expected: ✅ Agent confirms task creation
Example: "I've created a new task: 'test Kubernetes chatbot integration'"
```

#### Test 3e: Verify Task Created

```
1. Minimize/close chatbot
2. Navigate to dashboard/tasks page
3. Look for new task

Expected: ✅ Task created by chatbot appears in task list
```

#### Test 3f: Complete Task via Chatbot

```
Send message: "Complete task 'test Kubernetes chatbot integration'"

or

Send message: "Mark task #5 as done"

Expected: ✅ Agent confirms task completion
Example: "I've marked the task as completed"
```

#### Test 3g: MCP Server Integration

The chatbot tests verify:
- ✅ MCP server running in backend pod (port 8001)
- ✅ OpenAI Agents SDK communicating with MCP server
- ✅ Task management skills working through MCP protocol
- ✅ AI responses generated via OpenAI API

### Test 4: Database Persistence Across Restarts

Test that data persists because database is external (Neon PostgreSQL).

```bash
# Create a test task via UI or chatbot
# Note task details

# Delete backend pod (forces restart)
kubectl delete pod -n taskflow -l app=taskflow-backend

# Wait for new pod to start (30-60 seconds)
kubectl get pods -n taskflow -w

# Access frontend at http://localhost
# Sign in again

Expected: ✅ Task created earlier still exists (data persisted in Neon database)
```

### Test 5: Health Endpoints

```bash
# Test backend health endpoint
BACKEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n taskflow $BACKEND_POD -- wget -qO- http://localhost:7860/health

# Expected: {"status":"healthy"}

# Test database health endpoint
kubectl exec -n taskflow $BACKEND_POD -- wget -qO- http://localhost:7860/api/health/db

# Expected: {"status":"connected"}
```

---

## Monitor Resources

Monitor Kubernetes resources, CPU, memory, and pod health.

### Check Resource Usage

```bash
# View CPU and memory usage for all pods
kubectl top pods -n taskflow

# Expected output:
# NAME                                  CPU(cores)   MEMORY(bytes)
# backend-deployment-xxx-xxx            150m         280Mi
# frontend-deployment-xxx-xxx           80m          220Mi

# Both should be well below limits:
# Backend limit: 500Mi memory, 500m CPU
# Frontend limit: 512Mi memory, 500m CPU
```

### Check Resource Limits

```bash
# View backend resource configuration
kubectl describe pod -n taskflow -l app=taskflow-backend | grep -A 10 "Limits:"

# Expected:
#   Limits:
#     cpu:     500m
#     memory:  500Mi
#   Requests:
#     cpu:     250m
#     memory:  256Mi

# View frontend resource configuration
kubectl describe pod -n taskflow -l app=taskflow-frontend | grep -A 10 "Limits:"

# Expected:
#   Limits:
#     cpu:     500m
#     memory:  512Mi
#   Requests:
#     cpu:     250m
#     memory:  256Mi
```

### Watch Pod Events

```bash
# View recent events in namespace
kubectl get events -n taskflow --sort-by='.lastTimestamp'

# Look for:
# - "Scheduled" events (pod assigned to node)
# - "Pulled" events (image pulled successfully)
# - "Created" events (container created)
# - "Started" events (container started)
# - "Unhealthy" warnings (probe failures - should not see these)
```

### Monitor Pod Health Continuously

```bash
# Watch pods with auto-refresh
watch -n 2 kubectl get pods -n taskflow

# Or with kubectl built-in watch
kubectl get pods -n taskflow -w

# Observe:
# - RESTARTS column should stay at 0 (or low number)
# - STATUS should remain "Running"
# - READY should show 1/1
```

### Check Persistent Issues

```bash
# Count pod restarts
kubectl get pods -n taskflow -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'

# Expected: 0 restarts (or very low number)

# If restarts > 0, investigate:
kubectl describe pod -n taskflow <pod-name> | grep -A 20 "Events:"
```

---

## Troubleshooting

Common issues and their solutions.

### Issue 1: Pods Not Starting (Pending Status)

**Symptom:**
```bash
kubectl get pods -n taskflow
# NAME                           READY   STATUS    RESTARTS   AGE
# backend-deployment-xxx-xxx     0/1     Pending   0          5m
```

**Diagnosis:**
```bash
kubectl describe pod -n taskflow <pod-name>
```

**Common Causes & Solutions:**

**A. Insufficient Resources**
```
Message: "Insufficient cpu" or "Insufficient memory"

Solution:
1. Check Docker Desktop resource limits
2. Settings → Resources → Increase Memory to 4GB+, CPU to 2+
3. Click "Apply & Restart"
4. Wait for Docker Desktop to restart
5. Redeploy: kubectl delete pod -n taskflow <pod-name>
```

**B. ImagePullBackOff**
```
Message: "Back-off pulling image" or "Failed to pull image"

Solution:
1. Verify image exists locally:
   docker images | grep taskflow
2. Check imagePullPolicy in deployment:
   kubectl get deployment -n taskflow <deployment-name> -o yaml | grep imagePullPolicy
   # Should show: imagePullPolicy: Never
3. If images missing, rebuild:
   docker build -f Dockerfile.k8s -t taskflow-backend:latest .
   docker build -t taskflow-frontend:latest ./frontend
```

**C. Node Not Ready**
```
Message: "No nodes are available"

Solution:
1. Check node status:
   kubectl get nodes
2. If node not Ready:
   - Restart Docker Desktop
   - Wait 2-3 minutes
   - Verify: kubectl get nodes
```

### Issue 2: Pods Crashing (CrashLoopBackOff)

**Symptom:**
```bash
kubectl get pods -n taskflow
# NAME                           READY   STATUS             RESTARTS   AGE
# backend-deployment-xxx-xxx     0/1     CrashLoopBackOff   5          10m
```

**Diagnosis:**
```bash
# Check current logs
kubectl logs -n taskflow <pod-name>

# Check previous logs (if pod restarted)
kubectl logs -n taskflow <pod-name> --previous

# Describe pod for events
kubectl describe pod -n taskflow <pod-name> | grep -A 10 "Events:"
```

**Common Causes & Solutions:**

**A. Missing Environment Variables**
```
Log error: "KeyError: 'DATABASE_URL'" or similar

Solution:
1. Verify secret exists:
   kubectl get secret taskflow-secrets -n taskflow
2. If missing, regenerate:
   bash scripts/generate-secrets.sh
   kubectl apply -f k8s/secrets.yaml
3. Restart pod:
   kubectl delete pod -n taskflow <pod-name>
```

**B. Database Connection Failure**
```
Log error: "Could not connect to database" or "Connection refused"

Solution:
1. Verify DATABASE_URL is correct:
   kubectl get secret taskflow-secrets -n taskflow -o yaml
   # Decode: echo "<base64-value>" | base64 -d
2. Test database connectivity from pod:
   kubectl exec -n taskflow <backend-pod> -- wget -qO- http://localhost:7860/api/health/db
3. Check Neon database is accessible:
   - Verify IP not blocked by firewall
   - Check database is not suspended
```

**C. Health Probe Failing Too Fast**
```
Event: "Startup probe failed" with high frequency

Solution:
1. Check startup probe timeout:
   kubectl describe pod -n taskflow <pod-name> | grep "Startup:"
2. If needed, increase timeout in backend-deployment.yaml:
   startupProbe:
     periodSeconds: 10
     failureThreshold: 60  # Increase this
3. Apply changes:
   kubectl apply -f k8s/backend-deployment.yaml
```

**D. Shell Script Errors**
```
Log error: "Illegal option" or "bad trap" or "Illegal number"

Solution:
1. Check startup script uses POSIX sh syntax (not bash)
2. Verify script in image:
   kubectl exec -n taskflow <pod> -- cat /app/scripts/start-backend.sh
3. If issues found, rebuild image with fixed script:
   docker build --no-cache -f Dockerfile.k8s -t taskflow-backend:latest .
   kubectl delete pod -n taskflow <backend-pod>
```

### Issue 3: LoadBalancer Service Pending

**Symptom:**
```bash
kubectl get svc frontend-service -n taskflow
# NAME               TYPE           EXTERNAL-IP   PORT(S)
# frontend-service   LoadBalancer   <pending>     80:30635/TCP
```

**Solutions:**

**Docker Desktop:**
```bash
# Wait 30-60 seconds, LoadBalancer should assign localhost
kubectl get svc frontend-service -n taskflow -w

# If still pending after 2 minutes:
1. Restart Docker Desktop
2. Wait for Kubernetes to reinitialize
3. Check again: kubectl get svc -n taskflow
```

**Minikube:**
```bash
# Start minikube tunnel (in separate terminal)
minikube tunnel

# Keep tunnel running while using LoadBalancer
# Access frontend at assigned IP or localhost
```

**Alternative: Use NodePort**
```bash
# Patch service to NodePort
kubectl patch svc frontend-service -n taskflow -p '{"spec":{"type":"NodePort"}}'

# Get NodePort
kubectl get svc frontend-service -n taskflow
# PORT(S): 80:30635/TCP
#              ^^^^^
#          Use this port

# Access at: http://localhost:30635
```

**Alternative: Port Forward**
```bash
# Forward service to local port
kubectl port-forward -n taskflow svc/frontend-service 3000:80

# Access at: http://localhost:3000
```

### Issue 4: Cannot Access Frontend

**Symptom:**
```bash
curl http://localhost
# curl: (7) Failed to connect to localhost port 80: Connection refused
```

**Diagnosis & Solutions:**

**A. Service Not Ready**
```bash
# Check service exists
kubectl get svc frontend-service -n taskflow

# Check pod is running
kubectl get pods -n taskflow -l app=taskflow-frontend

Solution:
- Wait for pod to reach Running status (1/1 Ready)
- Check logs: kubectl logs -n taskflow -l app=taskflow-frontend
```

**B. Port 80 Already in Use**
```bash
# Check what's using port 80
sudo lsof -i :80
# or
sudo netstat -tulpn | grep :80

Solution:
- Stop conflicting service (Apache, nginx, etc.)
- Or use port forwarding to different port:
  kubectl port-forward -n taskflow svc/frontend-service 8080:80
  # Access at: http://localhost:8080
```

**C. Firewall Blocking**
```bash
# Temporarily disable firewall (macOS)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Temporarily disable firewall (Linux)
sudo ufw disable

# Test access, then re-enable:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo ufw enable
```

**D. LoadBalancer Not Assigned**
```bash
# Use NodePort or port-forward as described above
```

### Issue 5: Backend Not Connecting to Database

**Symptom:**
```
Backend logs show: "FATAL: password authentication failed" or "Connection refused"
```

**Diagnosis:**
```bash
# Check backend logs for database errors
kubectl logs -n taskflow -l app=taskflow-backend | grep -i database

# Check DATABASE_URL secret
kubectl get secret taskflow-secrets -n taskflow -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

**Solutions:**

**A. Incorrect DATABASE_URL**
```
Solution:
1. Verify DATABASE_URL in .env file
2. Regenerate secrets:
   bash scripts/generate-secrets.sh
3. Apply secret:
   kubectl apply -f k8s/secrets.yaml
4. Restart backend:
   kubectl delete pod -n taskflow -l app=taskflow-backend
```

**B. Neon Database Suspended**
```
Neon databases auto-suspend after inactivity

Solution:
1. Open Neon console: https://console.neon.tech/
2. Wake database (first query wakes it)
3. Or configure "Always active" in Neon settings
```

**C. IP Address Blocked**
```
Neon may block certain IPs

Solution:
1. Check Neon IP allowlist settings
2. Add Docker Desktop IP (or allow all IPs for testing)
3. Restart backend pod
```

**D. Connection Timeout**
```
Database takes too long to respond

Solution:
1. Check network connectivity from pod:
   kubectl exec -n taskflow <backend-pod> -- wget -qO- http://localhost:7860/api/health/db
2. Increase database timeout in backend code (if needed)
3. Verify Neon region is close to your location
```

### Issue 6: Changes Not Reflected

**Symptom:**
```
Made code changes but pod still runs old code
```

**Solution:**
```bash
# Rebuild image without cache
docker build --no-cache -f Dockerfile.k8s -t taskflow-backend:latest .
# or
docker build --no-cache -t taskflow-frontend:latest ./frontend

# Delete old pods (forces recreation with new image)
kubectl delete pod -n taskflow -l app=taskflow-backend
# or
kubectl delete pod -n taskflow -l app=taskflow-frontend

# Verify new pod uses updated image
kubectl get pods -n taskflow
# Check AGE column (should show recent creation time)
```

---

## Cleanup

Remove the Kubernetes deployment and resources.

### Quick Cleanup (Delete Namespace)

```bash
# Delete entire namespace (removes all resources)
kubectl delete namespace taskflow

# Expected: namespace "taskflow" deleted

# Verify deletion
kubectl get all -n taskflow
# Expected: No resources found in taskflow namespace
```

### Thorough Cleanup

```bash
# 1. Delete Kubernetes resources individually
kubectl delete -f k8s/frontend-service.yaml
kubectl delete -f k8s/frontend-deployment.yaml
kubectl delete -f k8s/backend-service.yaml
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/secrets.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/namespace.yaml

# 2. Delete Docker images
docker rmi taskflow-backend:latest
docker rmi taskflow-frontend:latest

# 3. Delete generated secrets file
rm k8s/secrets.yaml

# 4. Reset kubectl context to default namespace
kubectl config set-context --current --namespace=default

# 5. Verify cleanup
kubectl get all -n taskflow
# Expected: No resources found

docker images | grep taskflow
# Expected: No output
```

### Partial Cleanup (Keep Namespace)

```bash
# Delete deployments only (keeps namespace, configmap, secrets)
kubectl delete deployment -n taskflow --all

# Delete services only
kubectl delete service -n taskflow --all

# Later, recreate deployments:
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

---

## Performance Benchmarks

Expected performance metrics for Phase IV deployment.

### Build Times

| Operation | First Build | Rebuild (cached) | Target |
|-----------|-------------|------------------|--------|
| Backend image | 3-5 minutes | 30-60 seconds | <5 min |
| Frontend image | 2-3 minutes | 20-40 seconds | <3 min |
| Total build time | 5-8 minutes | 50-100 seconds | <8 min |

### Deployment Times

| Operation | Duration | Target |
|-----------|----------|--------|
| Namespace creation | <1 second | Instant |
| ConfigMap/Secret apply | <1 second | Instant |
| Backend pod startup | 30-60 seconds | <2 min |
| Frontend pod startup | 20-40 seconds | <2 min |
| LoadBalancer provisioning | 10-30 seconds | <1 min |
| **Total deployment** | **1-2 minutes** | **<3 min** |

### Runtime Performance

| Metric | Expected | Target |
|--------|----------|--------|
| Health probe response | <1 second | <5 sec |
| Frontend page load | 1-3 seconds | <3 sec |
| Backend API response | <500ms | <1 sec |
| Chatbot AI response | 2-5 seconds | <10 sec |
| Task CRUD operations | <1 second | <2 sec |

### Resource Usage

| Resource | Backend (Idle) | Backend (Load) | Limit |
|----------|---------------|----------------|-------|
| CPU | 50-100m | 200-400m | 500m |
| Memory | 200-250Mi | 280-350Mi | 500Mi |

| Resource | Frontend (Idle) | Frontend (Load) | Limit |
|----------|-----------------|----------------|-------|
| CPU | 20-50m | 100-200m | 500m |
| Memory | 150-200Mi | 220-280Mi | 512Mi |

### Image Sizes

| Image | Size | Target | Status |
|-------|------|--------|--------|
| taskflow-backend:latest | 561MB | <500MB | ⚠️ Acceptable (61MB over) |
| taskflow-frontend:latest | 294MB | <300MB | ✅ Within target |

### Stability Metrics

| Metric | Observed | Target |
|--------|----------|--------|
| Pod restarts (10 min) | 0 | 0 |
| Failed health probes | 0 | 0 |
| Successful requests | 100% | >99% |
| Average uptime | 100% | >99.9% |

---

## Architecture Summary

Complete architecture overview of Phase IV Kubernetes deployment.

### Kubernetes Resources

```
Namespace: taskflow
├── ConfigMap: taskflow-config
│   └── Non-sensitive configuration
│       ├── JWT_ALGORITHM: HS256
│       ├── JWT_EXPIRATION_DAYS: 7
│       ├── BACKEND_URL: http://backend-service:8000
│       ├── NEXT_PUBLIC_API_URL: http://backend-service:8000
│       └── MCP_BACKEND_URL: http://localhost:8001
│
├── Secret: taskflow-secrets (base64-encoded)
│   └── Sensitive credentials
│       ├── DATABASE_URL (Neon PostgreSQL)
│       ├── JWT_SECRET_KEY
│       ├── OPENAI_API_KEY
│       ├── GOOGLE_CLIENT_ID + SECRET
│       └── GITHUB_CLIENT_ID + SECRET
│
├── Backend Deployment
│   ├── Replicas: 1
│   ├── Image: taskflow-backend:latest (561MB)
│   ├── imagePullPolicy: Never (use local)
│   ├── Selector: app=taskflow-backend
│   ├── Security Context:
│   │   ├── runAsNonRoot: true
│   │   ├── runAsUser: 1000 (appuser)
│   │   └── fsGroup: 1000
│   ├── Ports:
│   │   ├── 7860 (FastAPI HTTP)
│   │   └── 8001 (MCP server)
│   ├── Environment: configMapRef + secretRef
│   ├── Resources:
│   │   ├── Requests: 256Mi memory, 250m CPU
│   │   └── Limits: 500Mi memory, 500m CPU
│   ├── Health Probes:
│   │   ├── Startup: /health (10s × 60 = 10min max)
│   │   ├── Liveness: /health (30s initial, 10s period)
│   │   └── Readiness: /health (10s initial, 5s period)
│   └── Pod: backend-deployment-xxxxxxxxxx-xxxxx
│       ├── Status: Running (1/1 Ready)
│       ├── Restarts: 0
│       └── Age: 15m
│
├── Backend Service
│   ├── Type: ClusterIP (internal only)
│   ├── Selector: app=taskflow-backend
│   ├── Port: 8000 (external within cluster)
│   ├── TargetPort: 7860 (container port)
│   └── ClusterIP: 10.98.39.79
│
├── Frontend Deployment
│   ├── Replicas: 1
│   ├── Image: taskflow-frontend:latest (294MB)
│   ├── imagePullPolicy: Never
│   ├── Selector: app=taskflow-frontend
│   ├── Security Context:
│   │   ├── runAsNonRoot: true
│   │   └── runAsUser: 1000 (node)
│   ├── Port: 3000 (Next.js)
│   ├── Environment:
│   │   └── NEXT_PUBLIC_API_URL: (from ConfigMap)
│   ├── Resources:
│   │   ├── Requests: 256Mi memory, 250m CPU
│   │   └── Limits: 512Mi memory, 500m CPU
│   ├── Health Probes:
│   │   ├── Liveness: / (20s initial, 10s period)
│   │   └── Readiness: / (10s initial, 5s period)
│   └── Pod: frontend-deployment-xxxxxxxxxx-xxxxx
│       ├── Status: Running (1/1 Ready)
│       ├── Restarts: 0
│       └── Age: 15m
│
└── Frontend Service
    ├── Type: LoadBalancer (external access)
    ├── Selector: app=taskflow-frontend
    ├── Port: 80 (external public)
    ├── TargetPort: 3000 (container port)
    ├── ClusterIP: 10.104.194.97
    └── External-IP: localhost (Docker Desktop)
```

### External Dependencies

```
TaskFlow Kubernetes Cluster
    │
    ├──> Neon PostgreSQL (Cloud)
    │    └── Database: neondb
    │        ├── Connection: pooled
    │        ├── TLS: required
    │        └── Status: always-on
    │
    ├──> OpenAI API (Cloud)
    │    └── Model: gpt-4
    │        ├── Purpose: Chatbot responses
    │        └── SDK: OpenAI Agents SDK
    │
    ├──> Google OAuth (Cloud)
    │    └── OAuth 2.0 authentication
    │        └── Redirect: http://localhost/api/auth/callback/google
    │
    └──> GitHub OAuth (Cloud)
         └── OAuth 2.0 authentication
             └── Redirect: http://localhost/api/auth/callback/github
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                │
└─────────────┬───────────────────────────────────────────────┘
              │ HTTPS (Browser)
              ▼
┌─────────────────────────────────────────────────────────────┐
│          Frontend Service (LoadBalancer:80)                 │
└─────────────┬───────────────────────────────────────────────┘
              │ HTTP
              ▼
┌─────────────────────────────────────────────────────────────┐
│         Frontend Pod (Next.js SSR on :3000)                 │
│                                                             │
│  - Renders UI components (React Server Components)         │
│  - Handles client interactions                             │
│  - Calls backend API via internal service                  │
└─────────────┬───────────────────────────────────────────────┘
              │ HTTP (internal cluster)
              │ http://backend-service:8000
              ▼
┌─────────────────────────────────────────────────────────────┐
│         Backend Service (ClusterIP:8000)                    │
└─────────────┬───────────────────────────────────────────────┘
              │ Routes to backend pod port 7860
              ▼
┌─────────────────────────────────────────────────────────────┐
│         Backend Pod (FastAPI + MCP on :7860, :8001)        │
│                                                             │
│  ┌─────────────────────┐     ┌─────────────────────┐      │
│  │   FastAPI Server    │     │    MCP Server       │      │
│  │   (Port 7860)       │<--->│   (Port 8001)       │      │
│  │                     │     │                     │      │
│  │  - REST API         │     │  - Tool handlers    │      │
│  │  - Auth endpoints   │     │  - Task skills      │      │
│  │  - CRUD operations  │     │  - OpenAI Agents    │      │
│  └─────────────────────┘     └─────────────────────┘      │
│                                                             │
└─────────────┬───────────────────────┬────────────────┬──────┘
              │                       │                │
              ▼                       ▼                ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ Neon PostgreSQL │  │   OpenAI API    │  │  OAuth (G/GH)   │
    │   (External)    │  │   (External)    │  │   (External)    │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Network Policies (Implicit)

Docker Desktop Kubernetes has **no network policies by default**, meaning:

- ✅ Frontend pods can reach backend service (http://backend-service:8000)
- ✅ Backend pods can reach external services (Neon, OpenAI, OAuth)
- ✅ All pods can reach internet for package installations
- ❌ External users cannot reach backend directly (ClusterIP)
- ✅ External users can reach frontend (LoadBalancer on localhost)

### Security Model

**Container Security:**
- ✅ Non-root users (UID 1000)
- ✅ Read-only root filesystem: false (applications need write)
- ✅ allowPrivilegeEscalation: false (default)
- ✅ Secrets base64-encoded (not committed to git)

**Network Security:**
- ✅ Backend: ClusterIP only (internal)
- ✅ Frontend: LoadBalancer (localhost only on Docker Desktop)
- ⚠️ TLS: Not configured (local development only)

**Access Control:**
- ✅ Namespace isolation (taskflow)
- ✅ Service selector labels
- ⚠️ RBAC: Not configured (Docker Desktop default)
- ⚠️ Network Policies: Not configured

---

## Summary

Phase IV successfully deploys TaskFlow to local Kubernetes with:

✅ **Docker Images**: Multi-stage builds, non-root users, health checks
✅ **Kubernetes Resources**: Namespace, Deployments, Services, ConfigMap, Secret
✅ **Health Monitoring**: Startup, liveness, and readiness probes
✅ **Resource Management**: CPU and memory limits enforced
✅ **External Access**: LoadBalancer service on localhost
✅ **Internal Communication**: ClusterIP service for backend
✅ **Data Persistence**: External Neon PostgreSQL (survives pod restarts)
✅ **AI Integration**: MCP server + OpenAI Agents SDK working in containers
✅ **Authentication**: OAuth (Google/GitHub) working through Kubernetes
✅ **Backward Compatibility**: Phase I console, Phase II web UI, Phase III chatbot all functional

**Access Points:**
- Frontend: `http://localhost`
- Console: `uv run todo` (local)
- Kubernetes: `kubectl get pods -n taskflow`

**Next Steps:**
- Phase V: Deploy to cloud Kubernetes (DigitalOcean DOKS, GKE, AKS, EKS)
- Add Ingress controller for TLS/SSL
- Implement horizontal pod autoscaling
- Add monitoring (Prometheus, Grafana)
- Set up CI/CD pipeline

---

**Document Version**: 1.0.0
**Last Tested**: 2026-02-03
**Testing Platform**: Docker Desktop 29.1.3 + Kubernetes v1.28
**Status**: ✅ All tests passing
