# TaskFlow Helm Chart

This Helm chart deploys the TaskFlow Todo application to Kubernetes with a single command.

## Prerequisites

- Kubernetes cluster (Docker Desktop K8s or Minikube)
- Helm 3.x installed ([Installation guide](https://helm.sh/docs/intro/install/))
- Docker images built locally:
  - `taskflow-backend:latest`
  - `taskflow-frontend:latest`

## Installation

### 1. Install Helm (if not already installed)

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Windows
choco install kubernetes-helm
```

### 2. Configure Secrets

Create a `values-secrets.yaml` file with your sensitive values:

```yaml
secrets:
  databaseUrl: "postgresql://user:password@host:5432/db"
  jwtSecretKey: "your-secret-key-here"
  openaiApiKey: "sk-..."
  googleClientId: "your-google-client-id"
  googleClientSecret: "your-google-client-secret"
  githubClientId: "your-github-client-id"
  githubClientSecret: "your-github-client-secret"
```

**⚠️ Important**: Add `values-secrets.yaml` to `.gitignore` - never commit secrets!

### 3. Install the Chart

```bash
# From project root
helm install taskflow ./helm/taskflow -f ./helm/taskflow/values-secrets.yaml
```

Or with inline values:

```bash
helm install taskflow ./helm/taskflow \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.jwtSecretKey="your-secret" \
  --set secrets.openaiApiKey="sk-..."
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n taskflow

# Check pods are running
kubectl get pods -n taskflow

# Check services
kubectl get svc -n taskflow

# Get LoadBalancer IP/hostname
kubectl get svc frontend-service -n taskflow
```

### 5. Access the Application

```bash
# On Docker Desktop (LoadBalancer uses localhost)
open http://localhost

# On Minikube
minikube service frontend-service -n taskflow
```

## Configuration

### Customizing Values

Override default values using `--set` or a custom values file:

```bash
# Scale backend to 2 replicas
helm upgrade taskflow ./helm/taskflow --set backend.replicaCount=2

# Use different image tags
helm upgrade taskflow ./helm/taskflow \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0

# Change resource limits
helm upgrade taskflow ./helm/taskflow \
  --set backend.resources.limits.memory=1Gi \
  --set backend.resources.limits.cpu=1000m
```

### Available Values

See `values.yaml` for all configurable parameters:

- `namespace.name`: Namespace to deploy to (default: `taskflow`)
- `backend.replicaCount`: Number of backend replicas (default: `1`)
- `backend.image.repository`: Backend image repository
- `backend.image.tag`: Backend image tag (default: `latest`)
- `backend.resources`: CPU and memory limits/requests
- `frontend.replicaCount`: Number of frontend replicas (default: `1`)
- `frontend.image.repository`: Frontend image repository
- `frontend.image.tag`: Frontend image tag (default: `latest`)
- `frontend.resources`: CPU and memory limits/requests
- `config.*`: Non-sensitive configuration values
- `secrets.*`: Sensitive values (should be provided via secure method)

## Testing

### 1. Lint the Chart

```bash
helm lint ./helm/taskflow
```

### 2. Dry Run (Preview Resources)

```bash
helm install taskflow ./helm/taskflow --dry-run --debug
```

### 3. Template Rendering

```bash
# Render templates locally
helm template taskflow ./helm/taskflow

# Render with custom values
helm template taskflow ./helm/taskflow -f values-secrets.yaml
```

### 4. Install and Test

```bash
# Install
helm install taskflow ./helm/taskflow -f values-secrets.yaml

# Run tests (if test hooks defined)
helm test taskflow

# Check status
helm status taskflow

# List all releases
helm list -n taskflow
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade taskflow ./helm/taskflow -f values-secrets.yaml

# Upgrade specific components
helm upgrade taskflow ./helm/taskflow --set backend.image.tag=v1.1.0

# Rollback if needed
helm rollback taskflow 1
```

## Uninstalling

```bash
# Remove the release
helm uninstall taskflow

# Delete namespace (if desired)
kubectl delete namespace taskflow
```

## Troubleshooting

### View Rendered Manifests

```bash
helm get manifest taskflow
```

### Check Values

```bash
helm get values taskflow
```

### View History

```bash
helm history taskflow
```

### Common Issues

**Issue**: Pods stuck in `ImagePullBackOff`
- **Solution**: Ensure images are built locally and `imagePullPolicy: Never` is set

**Issue**: Secrets not found
- **Solution**: Verify you provided secrets via `values-secrets.yaml` or `--set`

**Issue**: Namespace already exists
- **Solution**: The chart creates the namespace - delete it first or use a different name

**Issue**: LoadBalancer external IP pending
- **Solution**: On Docker Desktop, use `localhost`. On Minikube, use `minikube service`

## Advanced Usage

### Using with CI/CD

```bash
# GitHub Actions example
- name: Deploy with Helm
  run: |
    helm upgrade --install taskflow ./helm/taskflow \
      --set backend.image.tag=${{ github.sha }} \
      --set frontend.image.tag=${{ github.sha }} \
      --set secrets.databaseUrl=${{ secrets.DATABASE_URL }} \
      --set secrets.jwtSecretKey=${{ secrets.JWT_SECRET }} \
      --wait --timeout 5m
```

### Using with Different Environments

```bash
# Development
helm install taskflow ./helm/taskflow -f values-dev.yaml

# Staging
helm install taskflow ./helm/taskflow -f values-staging.yaml

# Production
helm install taskflow ./helm/taskflow -f values-prod.yaml
```

## Architecture

```
┌─────────────────────────────────────┐
│         Namespace: taskflow         │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐  ┌──────────────┐│
│  │   Backend    │  │   Frontend   ││
│  │  Deployment  │  │  Deployment  ││
│  │  (1 replica) │  │  (1 replica) ││
│  └──────┬───────┘  └──────┬───────┘│
│         │                 │        │
│  ┌──────▼───────┐  ┌──────▼───────┐│
│  │   Backend    │  │   Frontend   ││
│  │   Service    │  │   Service    ││
│  │  (ClusterIP) │  │(LoadBalancer)││
│  └──────────────┘  └──────────────┘│
│         │                 │        │
│  ┌──────▼─────────────────▼───────┐│
│  │       ConfigMap & Secrets      ││
│  └────────────────────────────────┘│
└─────────────────────────────────────┘
```

## Chart Structure

```
helm/taskflow/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
├── .helmignore            # Files to ignore
├── README.md              # This file
└── templates/
    ├── _helpers.tpl       # Template helpers
    ├── namespace.yaml     # Namespace resource
    ├── configmap.yaml     # ConfigMap resource
    ├── secrets.yaml       # Secret resource
    ├── backend-deployment.yaml   # Backend Deployment
    ├── backend-service.yaml      # Backend Service
    ├── frontend-deployment.yaml  # Frontend Deployment
    └── frontend-service.yaml     # Frontend Service
```

## Contributing

When updating the chart:

1. Increment `version` in `Chart.yaml` for chart changes
2. Increment `appVersion` in `Chart.yaml` for application changes
3. Update this README with any new configuration options
4. Test with `helm lint` and `helm template`
5. Verify installation with `helm install --dry-run`

## License

MIT
