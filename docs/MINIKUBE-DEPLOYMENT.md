# Minikube Deployment Guide

This guide shows how to deploy TaskFlow to Minikube as an alternative to Docker Desktop Kubernetes.

## Table of Contents

- [Why Minikube?](#why-minikube)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Starting Minikube](#starting-minikube)
- [Loading Docker Images](#loading-docker-images)
- [Deploying TaskFlow](#deploying-taskflow)
- [Accessing Services](#accessing-services)
- [Differences vs Docker Desktop](#differences-vs-docker-desktop)
- [Troubleshooting](#troubleshooting)

## Why Minikube?

Minikube is a great choice for local Kubernetes development when:

- You don't have Docker Desktop (Linux users, licensing concerns)
- You want multiple cluster profiles for testing
- You need specific Kubernetes versions
- You want to test different container runtimes (Docker, containerd, CRI-O)
- You need VM-based isolation

## Prerequisites

- **System Requirements**:
  - 2 CPUs or more
  - 2GB of free memory
  - 20GB of free disk space
  - Container or virtual machine manager (Docker, QEMU, Hyperkit, Hyper-V, KVM, Parallels, Podman, VirtualBox, or VMware)

- **Required Tools**:
  - kubectl ([installation guide](https://kubernetes.io/docs/tasks/tools/))
  - Minikube ([installation guide](https://minikube.sigs.k8s.io/docs/start/))

## Installation

### Install Minikube

#### macOS

```bash
# Using Homebrew
brew install minikube

# Or using curl
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube
```

#### Linux

```bash
# x86-64
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# ARM64
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-arm64
sudo install minikube-linux-arm64 /usr/local/bin/minikube
```

#### Windows

```powershell
# Using Chocolatey
choco install minikube

# Or using winget
winget install Kubernetes.minikube
```

### Verify Installation

```bash
minikube version
```

Expected output:

```
minikube version: v1.32.0
commit: 8220a6eb95f0a4d75f7f2d7b14cef975f050512d
```

## Starting Minikube

### Basic Start

```bash
# Start with default driver
minikube start
```

### Recommended Configuration for TaskFlow

```bash
# Start with more resources and specific Kubernetes version
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=4096 \
  --kubernetes-version=v1.28.3 \
  --addons=dashboard \
  --addons=metrics-server
```

### Driver Options

Minikube supports multiple drivers:

```bash
# Docker (recommended - most compatible)
minikube start --driver=docker

# Podman
minikube start --driver=podman

# VirtualBox
minikube start --driver=virtualbox

# QEMU (KVM on Linux)
minikube start --driver=qemu
```

### Verify Cluster

```bash
# Check status
minikube status

# Get cluster info
kubectl cluster-info

# View nodes
kubectl get nodes
```

Expected output:

```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

## Loading Docker Images

**Critical Step**: Minikube runs in its own environment (VM or container), so it can't access images built on your host machine directly.

### Method 1: Load Images Directly (Recommended)

```bash
# Build images first (if not already built)
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend

# Load images into Minikube
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest
```

### Method 2: Use Minikube Docker Daemon

```bash
# Point your shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Now build images - they'll be available in Minikube
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend

# Verify images are in Minikube
minikube image ls | grep taskflow

# To revert back to host Docker daemon
eval $(minikube docker-env -u)
```

### Verify Images Loaded

```bash
# List images in Minikube
minikube image ls | grep taskflow
```

Expected output:

```
docker.io/library/taskflow-backend:latest
docker.io/library/taskflow-frontend:latest
```

## Deploying TaskFlow

### Option 1: Using kubectl (Raw Manifests)

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Set default namespace
kubectl config set-context --current --namespace=taskflow

# 3. Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# 4. Generate and apply secrets
bash scripts/generate-secrets.sh
kubectl apply -f k8s/secrets.yaml

# 5. Deploy backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# 6. Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 7. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=taskflow-backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=taskflow-frontend --timeout=300s
```

### Option 2: Using Helm Chart

```bash
# Install with Helm (if Helm is installed)
helm install taskflow ./helm/taskflow -f values-secrets.yaml
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n taskflow

# Check pod logs
kubectl logs -l app=taskflow-backend -n taskflow
kubectl logs -l app=taskflow-frontend -n taskflow

# Check events
kubectl get events -n taskflow --sort-by='.lastTimestamp'
```

## Accessing Services

### LoadBalancer Services on Minikube

Minikube doesn't have a real LoadBalancer. Use `minikube service` to expose services:

```bash
# Get frontend service URL
minikube service frontend-service -n taskflow

# This will open the application in your default browser
# And provide the URL like: http://192.168.49.2:30635
```

### Alternative: Port Forwarding

```bash
# Forward frontend service to localhost
kubectl port-forward -n taskflow service/frontend-service 8080:80

# Access at http://localhost:8080
```

### Get Service URLs Programmatically

```bash
# Get frontend URL
minikube service frontend-service -n taskflow --url

# Get all service URLs
minikube service list -n taskflow
```

### Minikube Dashboard

```bash
# Launch Kubernetes dashboard
minikube dashboard

# Or get the URL without launching
minikube dashboard --url
```

## Differences vs Docker Desktop

### Key Differences

| Feature | Docker Desktop K8s | Minikube |
|---------|-------------------|----------|
| **Installation** | Built into Docker Desktop | Separate installation |
| **VM/Container** | Uses Docker Desktop VM | Creates its own VM/container |
| **LoadBalancer** | Uses `localhost` | Requires `minikube service` |
| **Image Access** | Direct access to Docker images | Requires `minikube image load` |
| **Performance** | Faster (shared kernel) | Slightly slower (separate VM) |
| **Isolation** | Less isolated | More isolated |
| **Multi-Cluster** | Single cluster only | Multiple profiles supported |
| **Addons** | Limited | Rich addon ecosystem |

### Configuration Adjustments

#### 1. ImagePullPolicy

Ensure deployments use `imagePullPolicy: Never` for local images:

```yaml
# Already configured in k8s/backend-deployment.yaml and k8s/frontend-deployment.yaml
spec:
  containers:
  - name: backend
    image: taskflow-backend:latest
    imagePullPolicy: Never  # Critical for Minikube
```

#### 2. LoadBalancer Access

**Docker Desktop**:
```bash
# Access via localhost
open http://localhost
```

**Minikube**:
```bash
# Use minikube service
minikube service frontend-service -n taskflow

# Or port forward
kubectl port-forward -n taskflow service/frontend-service 8080:80
```

#### 3. Host Path Volumes (if using)

**Docker Desktop**: Can mount host paths directly

**Minikube**: Requires mounting into Minikube first:

```bash
minikube mount /host/path:/minikube/path
```

## Troubleshooting

### Issue: Minikube Won't Start

```bash
# Check status and logs
minikube status
minikube logs

# Delete and recreate cluster
minikube delete
minikube start --driver=docker
```

### Issue: Images Not Found

```bash
# Verify images loaded
minikube image ls | grep taskflow

# Reload images if missing
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest

# Verify imagePullPolicy is Never
kubectl get deployment backend-deployment -n taskflow -o yaml | grep imagePullPolicy
```

### Issue: Pods Stuck in ImagePullBackOff

```bash
# Check pod events
kubectl describe pod -l app=taskflow-backend -n taskflow

# Common causes:
# 1. Image not loaded into Minikube
# 2. imagePullPolicy not set to Never
# 3. Wrong image name/tag

# Solution:
minikube image load taskflow-backend:latest
kubectl rollout restart deployment/backend-deployment -n taskflow
```

### Issue: Can't Access Frontend

```bash
# Get service URL
minikube service frontend-service -n taskflow --url

# Check service
kubectl get svc frontend-service -n taskflow

# Check pod logs
kubectl logs -l app=taskflow-frontend -n taskflow

# Port forward as alternative
kubectl port-forward -n taskflow service/frontend-service 8080:80
```

### Issue: Insufficient Resources

```bash
# Stop Minikube
minikube stop

# Delete and recreate with more resources
minikube delete
minikube start --cpus=4 --memory=4096
```

### Issue: Slow Performance

```bash
# Try different driver
minikube start --driver=virtualbox  # or docker, qemu, etc.

# Enable more CPUs
minikube start --cpus=4

# Use faster storage
minikube start --disk-size=50g --base-image=gcr.io/k8s-minikube/kicbase-builds:v0.0.40
```

## Advanced Usage

### Multiple Clusters

```bash
# Create production-like cluster
minikube start -p production --cpus=4 --memory=8192

# Create staging cluster
minikube start -p staging --cpus=2 --memory=4096

# Switch between profiles
minikube profile production
kubectl get pods -A

minikube profile staging
kubectl get pods -A

# List all profiles
minikube profile list
```

### Enable Addons

```bash
# Enable metrics server for resource monitoring
minikube addons enable metrics-server

# Enable ingress for HTTP routing
minikube addons enable ingress

# Enable registry for private images
minikube addons enable registry

# List all addons
minikube addons list
```

### Persistent Volumes

```bash
# Minikube provides hostPath storage by default
kubectl get storageclass

# Use PersistentVolumeClaim in your deployment
```

### SSH into Minikube

```bash
# SSH into the Minikube node
minikube ssh

# Check Docker images inside Minikube
docker images | grep taskflow

# Exit
exit
```

## Cleanup

### Stop Cluster (Keep Data)

```bash
minikube stop
```

### Delete Cluster (Remove All Data)

```bash
minikube delete
```

### Delete Specific Profile

```bash
minikube delete -p production
```

### Remove All Minikube Data

```bash
minikube delete --all --purge
```

## Performance Comparison

### Build and Deploy Time

| Step | Docker Desktop K8s | Minikube |
|------|-------------------|----------|
| Image build | 5-10 min | 5-10 min |
| Image load | Instant (same daemon) | 1-2 min (`minikube image load`) |
| Pod startup | 1-2 min | 1-2 min |
| Total | ~6-12 min | ~7-14 min |

### Resource Usage

| Metric | Docker Desktop K8s | Minikube |
|--------|-------------------|----------|
| Memory overhead | ~2GB | ~1-2GB (driver dependent) |
| Disk space | Shared with Docker | Separate VM disk (~10GB) |
| CPU impact | Low (shared kernel) | Medium (VM overhead) |

## Minikube Best Practices

1. **Use Docker Driver**: Most compatible and fastest

   ```bash
   minikube start --driver=docker
   ```

2. **Allocate Sufficient Resources**: Don't starve the cluster

   ```bash
   minikube start --cpus=4 --memory=4096
   ```

3. **Load Images After Build**: Always reload after rebuilding

   ```bash
   docker build -t taskflow-backend:latest -f Dockerfile.k8s .
   minikube image load taskflow-backend:latest
   ```

4. **Use imagePullPolicy: Never**: For local images

5. **Access via minikube service**: For LoadBalancer services

6. **Enable Addons**: metrics-server, dashboard for better visibility

7. **Use Profiles**: Separate dev/staging/test environments

8. **Regular Cleanup**: Delete old profiles and images

## Recommended Workflow

```bash
# 1. Start Minikube
minikube start --driver=docker --cpus=4 --memory=4096

# 2. Build images
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend

# 3. Load images to Minikube
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest

# 4. Deploy with kubectl
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
bash scripts/generate-secrets.sh
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 5. Access application
minikube service frontend-service -n taskflow

# 6. Monitor
kubectl get pods -n taskflow -w
minikube dashboard

# 7. Stop when done
minikube stop
```

## Next Steps

- Review [Phase IV Testing Guide](./PHASE-IV-TESTING-GUIDE.md) for comprehensive testing
- See [Helm Chart README](../helm/taskflow/README.md) for Helm-based deployment
- Check [AI DevOps Tools](./AI-DEVOPS-TOOLS.md) for AI-assisted workflows

## Resources

- [Minikube Official Docs](https://minikube.sigs.k8s.io/docs/)
- [Minikube Handbook](https://minikube.sigs.k8s.io/docs/handbook/)
- [Kubernetes Local Dev Guide](https://kubernetes.io/docs/tasks/tools/)
