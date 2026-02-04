# Quickstart Guide: Local Kubernetes Deployment

**Feature**: 004-k8s-deployment
**Purpose**: Step-by-step guide for deploying TaskFlow to local Kubernetes cluster
**Audience**: Developers setting up Phase IV deployment
**Time**: 15-20 minutes (first time)

---

## Prerequisites

### Required Software

1. **Docker Desktop 4.0+** with Kubernetes enabled
   ```bash
   docker --version  # Should show 20.0+ or higher
   docker info | grep -i kubernetes  # Should show "Kubernetes: enabled"
   ```

2. **kubectl CLI** (bundled with Docker Desktop)
   ```bash
   kubectl version --client  # Should show v1.28+
   ```

3. **Git repository cloned**
   ```bash
   cd hackathon-todo
   git status  # Should show clean working tree
   ```

4. **.env file configured** with all secrets
   ```bash
   ls -la .env  # Should exist with proper permissions
   # Required variables:
   # - DATABASE_URL (Neon PostgreSQL)
   # - JWT_SECRET_KEY
   # - OPENAI_API_KEY
   # - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
   # - GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
   ```

### Enable Kubernetes in Docker Desktop

**Windows/Linux (WSL2)**:
1. Open Docker Desktop
2. Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for green indicator (may take 2-3 minutes)

**macOS**:
1. Docker Desktop → Preferences
2. Kubernetes tab
3. Enable Kubernetes
4. Apply & Restart

**Verify**:
```bash
kubectl cluster-info
# Expected: "Kubernetes control plane is running at https://kubernetes.docker.internal:6443"

kubectl get nodes
# Expected: 1 node in "Ready" status
```

---

## Quick Start (5 Commands)

### Step 1: Verify Kubernetes

```bash
# Check cluster is running
kubectl cluster-info

# Should output:
# Kubernetes control plane is running at https://kubernetes.docker.internal:6443
# CoreDNS is running at https://kubernetes.docker.internal:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

### Step 2: Build Docker Images

```bash
# Build both backend and frontend images (takes 5-8 minutes)
bash scripts/build-images.sh

# Or build manually:
docker build -t taskflow-backend:latest .
docker build -t taskflow-frontend:latest ./frontend

# Verify images built successfully
docker images | grep taskflow
# Expected:
# taskflow-backend    latest   <image-id>   <timestamp>   <size<500MB>
# taskflow-frontend   latest   <image-id>   <timestamp>   <size<300MB>
```

### Step 3: Generate Kubernetes Secrets

```bash
# Generate secrets from .env file (base64 encodes sensitive values)
bash scripts/generate-secrets.sh

# Verify secrets.yaml created (never commit this file!)
ls -la k8s/secrets.yaml
```

### Step 4: Deploy to Kubernetes

```bash
# Apply all manifests in order (takes 2-3 minutes)
bash scripts/deploy-k8s.sh

# Or deploy manually:
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Wait for pods to become ready
kubectl wait --for=condition=ready pod -l app=taskflow-backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=taskflow-frontend --timeout=300s
```

### Step 5: Access the Application

```bash
# Get LoadBalancer IP (on Docker Desktop, this will be 'localhost')
kubectl get svc -n taskflow frontend-service

# Expected output:
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# frontend-service   LoadBalancer   10.96.123.45    localhost     80:30123/TCP   2m

# Open browser to:
http://localhost
```

**Success!** TaskFlow UI should load with all Phase I-III features accessible via Kubernetes.

---

## Verification Commands

### Check Pod Status

```bash
# View all pods in taskflow namespace
kubectl get pods -n taskflow

# Expected output:
# NAME                                   READY   STATUS    RESTARTS   AGE
# backend-deployment-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
# frontend-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          5m

# Check pod details (health probes, resource usage)
kubectl describe pod -n taskflow -l app=taskflow-backend
```

### Check Logs

```bash
# Backend logs (FastAPI + MCP server)
kubectl logs -n taskflow -l app=taskflow-backend --tail=50

# Frontend logs (Next.js server)
kubectl logs -n taskflow -l app=taskflow-frontend --tail=50

# Follow logs in real-time
kubectl logs -n taskflow -l app=taskflow-backend -f
```

### Test Backend Health (Internal)

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-backend -o jsonpath='{.items[0].metadata.name}')

# Test health endpoint from inside the pod
kubectl exec -n taskflow $BACKEND_POD -- curl -s http://localhost:7860/health

# Expected output:
# {"status":"healthy","timestamp":"2026-02-03T10:30:00Z"}
```

### Test Frontend Access (External)

```bash
# Test from host machine
curl -I http://localhost

# Expected:
# HTTP/1.1 200 OK
# Content-Type: text/html; charset=utf-8

# Or open in browser:
open http://localhost  # macOS
xdg-open http://localhost  # Linux
start http://localhost  # Windows
```

### Monitor Resource Usage

```bash
# View CPU and memory usage
kubectl top pods -n taskflow

# Expected output:
# NAME                                  CPU(cores)   MEMORY(bytes)
# backend-deployment-xxx-xxx            150m         280Mi
# frontend-deployment-xxx-xxx           80m          220Mi

# Should be well below limits (500Mi backend, 512Mi frontend)
```

### Check Health Probes

```bash
# View probe status
kubectl describe pod -n taskflow -l app=taskflow-backend | grep -A 5 "Liveness\|Readiness\|Startup"

# Expected: All probes passing
# Liveness:       http-get http://:7860/health delay=30s timeout=5s period=10s #success=1 #failure=3
# Readiness:      http-get http://:7860/health delay=10s timeout=5s period=5s #success=1 #failure=3
# Startup:        http-get http://:7860/health delay=0s timeout=5s period=5s #success=1 #failure=30
```

---

## End-to-End Testing

### 1. Test Phase I Console (Local)

```bash
# Verify console app still works (not in Kubernetes)
cd backend
uv run todo list

# Expected: Console output with task list or "No tasks found"
```

### 2. Test Phase II Web UI (via Kubernetes)

1. Open browser: `http://localhost`
2. Verify homepage loads with navigation and branding
3. Click "Sign In" → Sign in with Google or GitHub
4. Create a new task: "Test K8s deployment"
5. Verify task appears in task list
6. Mark task as complete
7. Delete task
8. Verify all CRUD operations work

### 3. Test Phase III Chatbot (via Kubernetes)

1. Navigate to chatbot page (if separate) or chatbot widget
2. Send test message: "Create a task: Buy groceries"
3. Verify chatbot responds with confirmation
4. Check task list to confirm task was created
5. Verify MCP server integration works through Kubernetes

### 4. Test Backend-Frontend Communication

```bash
# Get frontend pod name
FRONTEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-frontend -o jsonpath='{.items[0].metadata.name}')

# Test frontend can reach backend via ClusterIP service
kubectl exec -n taskflow $FRONTEND_POD -- wget -qO- http://backend-service:8000/health

# Expected:
# {"status":"healthy","timestamp":"..."}
```

### 5. Monitor for Stability (10 minutes)

```bash
# Watch pods for restarts (should remain stable)
watch kubectl get pods -n taskflow

# Expected: RESTARTS column should stay at 0
# If restarts occur, check logs and describe pod for events
```

---

## Troubleshooting

### Issue: Pods Stuck in "Pending"

**Symptoms**:
```bash
kubectl get pods -n taskflow
# NAME                           READY   STATUS    RESTARTS   AGE
# backend-deployment-xxx-xxx     0/1     Pending   0          5m
```

**Diagnosis**:
```bash
kubectl describe pod -n taskflow <pod-name> | grep -A 10 Events
```

**Common Causes**:
- **Insufficient resources**: Docker Desktop resource limits too low
  - **Fix**: Docker Desktop → Settings → Resources → Increase Memory to 4GB+
- **Image pull error**: Image not found locally
  - **Fix**: Verify `imagePullPolicy: Never` in deployments, rebuild images

### Issue: Pods Stuck in "ImagePullBackOff"

**Symptoms**:
```bash
kubectl get pods -n taskflow
# NAME                           READY   STATUS             RESTARTS   AGE
# backend-deployment-xxx-xxx     0/1     ImagePullBackOff   0          2m
```

**Diagnosis**:
```bash
kubectl describe pod -n taskflow <pod-name> | grep -A 5 "Failed to pull image"
```

**Fix**:
```bash
# Verify images exist locally
docker images | grep taskflow

# If images missing, rebuild:
bash scripts/build-images.sh

# Verify imagePullPolicy in deployments:
kubectl get deployment -n taskflow backend-deployment -o yaml | grep imagePullPolicy
# Should show: imagePullPolicy: Never
```

### Issue: Pods Crashing (CrashLoopBackOff)

**Symptoms**:
```bash
kubectl get pods -n taskflow
# NAME                           READY   STATUS             RESTARTS   AGE
# backend-deployment-xxx-xxx     0/1     CrashLoopBackOff   5          10m
```

**Diagnosis**:
```bash
# Check logs for errors
kubectl logs -n taskflow <pod-name> --previous

# Check events
kubectl describe pod -n taskflow <pod-name> | grep -A 10 Events
```

**Common Causes**:
- **Missing environment variables**: Secret or ConfigMap not applied
  - **Fix**: `kubectl apply -f k8s/configmap.yaml && kubectl apply -f k8s/secrets.yaml`
- **Database connection failed**: DATABASE_URL incorrect or Neon unreachable
  - **Fix**: Verify DATABASE_URL in .env, regenerate secrets
- **Health probe failing**: /health endpoint not responding
  - **Fix**: Increase `initialDelaySeconds` in deployment, test endpoint locally first

### Issue: Health Probes Failing

**Symptoms**:
```bash
kubectl describe pod -n taskflow <pod-name> | grep Unhealthy
# Warning  Unhealthy  2m  kubelet  Liveness probe failed: HTTP probe failed with statuscode: 500
```

**Diagnosis**:
```bash
# Test health endpoint manually
kubectl exec -n taskflow <pod-name> -- curl -v http://localhost:7860/health
```

**Fixes**:
- **Slow startup**: Increase `initialDelaySeconds` or `failureThreshold` in deployment
- **Database dependency**: Remove database check from health endpoint (keep it fast)
- **Port mismatch**: Verify probe uses correct port (7860 backend, 3000 frontend)

### Issue: LoadBalancer Pending (External IP)

**Symptoms**:
```bash
kubectl get svc -n taskflow frontend-service
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# frontend-service   LoadBalancer   10.96.123.45    <pending>     80:30123/TCP   5m
```

**Expected Behavior on Docker Desktop**:
- LoadBalancer services are supported natively
- External IP resolves to `localhost` automatically
- May take 30-60 seconds to provision

**Fix**:
```bash
# Wait a bit longer (up to 2 minutes)
kubectl get svc -n taskflow frontend-service -w

# If still pending after 5 minutes, restart Docker Desktop
# Or use NodePort as alternative:
kubectl patch svc -n taskflow frontend-service -p '{"spec":{"type":"NodePort"}}'
kubectl get svc -n taskflow frontend-service
# Access via: http://localhost:<NodePort>
```

### Issue: Frontend Cannot Reach Backend

**Symptoms**:
- Frontend loads but API calls fail
- Browser console shows network errors

**Diagnosis**:
```bash
# Test from frontend pod to backend service
FRONTEND_POD=$(kubectl get pod -n taskflow -l app=taskflow-frontend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n taskflow $FRONTEND_POD -- wget -qO- http://backend-service:8000/health

# If this fails, backend service or deployment has issues
```

**Fixes**:
- **Backend not ready**: Check `kubectl get pods -n taskflow`, wait for backend Running
- **Service misconfigured**: Verify backend service selector matches backend pod labels
- **Network policy**: Not applicable in Docker Desktop (no network policies by default)

---

## Cleanup

### Soft Cleanup (Remove Deployments, Keep Namespace)

```bash
kubectl delete deployment -n taskflow --all
kubectl delete svc -n taskflow --all
kubectl delete configmap -n taskflow --all
kubectl delete secret -n taskflow --all

# Namespace remains, can redeploy quickly
```

### Full Cleanup (Remove Everything)

```bash
# Delete entire namespace (removes all resources)
kubectl delete namespace taskflow

# Remove local Docker images (optional)
docker rmi taskflow-backend:latest taskflow-frontend:latest

# Keep .env and source code
```

### Reset for Fresh Deployment

```bash
# Full cleanup
kubectl delete namespace taskflow
docker rmi taskflow-backend:latest taskflow-frontend:latest

# Remove generated secrets (regenerate from .env)
rm -f k8s/secrets.yaml

# Start fresh from Step 2
```

---

## Performance Benchmarks

### Build Times (Expected)

| Task | Duration | Notes |
|------|----------|-------|
| Backend image build | 3-5 minutes | First build (no cache) |
| Backend image rebuild | 30-60 seconds | With layer cache |
| Frontend image build | 2-3 minutes | First build (no cache) |
| Frontend image rebuild | 20-40 seconds | With layer cache |
| Total build time | 5-8 minutes | First time, both images |

### Deployment Times (Expected)

| Task | Duration | Notes |
|------|----------|-------|
| Namespace creation | <1 second | Instant |
| ConfigMap/Secret apply | <1 second | Instant |
| Backend pod startup | 30-60 seconds | Includes startup probe |
| Frontend pod startup | 20-40 seconds | Faster than backend |
| LoadBalancer provisioning | 10-30 seconds | Docker Desktop |
| Total deployment time | 1-2 minutes | End-to-end |

### Resource Usage (Observed)

| Resource | Backend | Frontend | Total |
|----------|---------|----------|-------|
| CPU (idle) | 50-100m | 20-50m | 70-150m |
| Memory (idle) | 200-250Mi | 150-200Mi | 350-450Mi |
| CPU (load) | 200-400m | 100-200m | 300-600m |
| Memory (load) | 280-350Mi | 220-280Mi | 500-630Mi |
| Disk (images) | <500MB | <300MB | <800MB |

---

## Next Steps

1. **Test all features**: Run through End-to-End Testing checklist
2. **Monitor stability**: Watch pods for 10 minutes, ensure no restarts
3. **Optimize images** (optional): Review Dockerfile layers, reduce size further
4. **Automate deployment**: Use scripts for faster deployments
5. **Bonus: Helm Chart**: Deploy with single `helm install` command (Phase VI)
6. **Phase V**: Deploy to cloud (DigitalOcean DOKS, GKE, AKS, EKS)

---

**Status**: Quickstart guide complete
**Success Metric**: First-time deployment in <20 minutes
**Support**: See troubleshooting section or check logs with `kubectl logs`
