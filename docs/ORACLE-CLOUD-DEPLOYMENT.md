# Oracle Cloud OKE Deployment Guide

This guide covers deploying the TaskFlow application to Oracle Cloud Infrastructure (OCI) Kubernetes Engine (OKE) with Kafka and Dapr.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Accessing the Application](#accessing-the-application)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Prerequisites

### Required Tools

1. **OCI CLI** - Oracle Cloud command-line interface
   ```bash
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
   ```

2. **kubectl** - Kubernetes command-line tool
   ```bash
   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

3. **Helm** - Kubernetes package manager (v3.20+)
   ```bash
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

4. **Docker** - For building and pushing images
   ```bash
   # Install Docker Desktop or Docker Engine
   # Verify with: docker --version
   ```

### Oracle Cloud Account

1. **Free Tier Account**: Sign up at [cloud.oracle.com](https://cloud.oracle.com)
   - Provides: 4 OCPUs, 24GB RAM (Always Free)
   - Sufficient for 1-broker Kafka + TaskFlow services

2. **OCI Configuration**: Configure OCI CLI
   ```bash
   oci setup config
   ```
   You'll need:
   - Tenancy OCID
   - User OCID
   - Region (e.g., `me-abudhabi-1`)
   - API key pair (generated during setup)

### Docker Hub Account

Required for hosting container images publicly.

## Step-by-Step Deployment

### 1. Create OKE Cluster

**Via Oracle Console (Recommended)**:

1. Navigate to **Developer Services** → **Kubernetes Clusters (OKE)**
2. Click **Create Cluster** → **Quick Create**
3. Configure:
   - **Name**: `taskflow-cluster`
   - **Kubernetes Version**: v1.34+ (latest stable)
   - **Shape**: `VM.Standard.E2.1.Micro` (Always Free tier)
   - **Number of Nodes**: 2
   - **Networking**: Use default VCN and subnets
4. Click **Create Cluster** and wait 10-15 minutes for provisioning

**Verify Cluster**:
```bash
# Get cluster OCID from console, then:
oci ce cluster create-kubeconfig \
  --cluster-id <your-cluster-ocid> \
  --file ~/.kube/config-oke \
  --region <your-region> \
  --token-version 2.0.0

export KUBECONFIG=~/.kube/config-oke
kubectl get nodes
```

Expected output:
```
NAME          STATUS   ROLES   AGE   VERSION
10.0.10.153   Ready    node    5m    v1.34.2
10.0.10.227   Ready    node    5m    v1.34.2
```

### 2. Deploy Kafka with Strimzi

Create namespaces:
```bash
kubectl create namespace kafka
kubectl create namespace taskflow
```

Install Strimzi Kafka operator:
```bash
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

Deploy Kafka cluster (KRaft mode, 1 broker):
```bash
kubectl apply -f k8s/kafka/kafka-cluster-kraft.yaml
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=600s -n kafka
```

Create Kafka topics:
```bash
kubectl apply -f k8s/kafka/topics.yaml
```

Verify Kafka:
```bash
kubectl get pods -n kafka
# Expected: strimzi-cluster-operator, taskflow-kafka-pool-0, entity-operator all Running
```

### 3. Deploy Dapr

Add Dapr Helm repository and install:
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm upgrade --install dapr dapr/dapr \
  --version=1.16 \
  --namespace dapr-system \
  --create-namespace \
  --wait \
  --timeout 300s
```

Verify Dapr:
```bash
kubectl get pods -n dapr-system
# Expected: dapr-operator, dapr-sentry, dapr-sidecar-injector, dapr-placement-server, dapr-scheduler-server (3 replicas) all Running
```

Apply Dapr components:
```bash
kubectl apply -f k8s/dapr/pubsub-kafka.yaml -n taskflow
kubectl apply -f k8s/dapr/subscription-reminders.yaml -n taskflow
```

### 4. Build and Push Docker Images

Login to Docker Hub:
```bash
export DOCKER_USERNAME="<your-dockerhub-username>"
export DOCKER_TOKEN="<your-dockerhub-token>"

echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USERNAME" --password-stdin
```

Build images:
```bash
docker build -t $DOCKER_USERNAME/taskflow-backend:latest -f Dockerfile.k8s .
docker build -t $DOCKER_USERNAME/taskflow-frontend:latest -f frontend/Dockerfile frontend/
docker build -t $DOCKER_USERNAME/taskflow-notification:latest -f src/services/notification/Dockerfile src/services/notification/
```

Push images:
```bash
docker push $DOCKER_USERNAME/taskflow-backend:latest
docker push $DOCKER_USERNAME/taskflow-frontend:latest
docker push $DOCKER_USERNAME/taskflow-notification:latest
```

### 5. Create Kubernetes Secrets

Create secrets from `.env` file:
```bash
kubectl create secret generic taskflow-secrets \
  --namespace taskflow \
  --from-env-file=.env
```

**Optional**: If your Docker images are private, create image pull secret:
```bash
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=$DOCKER_USERNAME \
  --docker-password=$DOCKER_TOKEN \
  --namespace=taskflow
```

### 6. Create OKE Helm Values

Create `helm/taskflow/values-oke.yaml`:
```yaml
# Oracle OKE specific values
global:
  environment: production

imagePullSecrets:
  - name: dockerhub-secret  # Only if using private images

backend:
  image:
    repository: docker.io/<your-username>/taskflow-backend
    tag: latest
    pullPolicy: Always
  replicas: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

frontend:
  image:
    repository: docker.io/<your-username>/taskflow-frontend
    tag: latest
    pullPolicy: Always
  replicas: 1
  service:
    type: LoadBalancer
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"

notification:
  enabled: true
  image: docker.io/<your-username>/taskflow-notification
  tag: latest
  imagePullPolicy: Always
  replicas: 1

dapr:
  enabled: true
  pubsubName: taskflow-pubsub

kafka:
  bootstrapServer: taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
```

**Important**: Use fully qualified image names (`docker.io/user/image`) to avoid "short name mode" errors in OKE.

### 7. Deploy TaskFlow with Helm

```bash
helm upgrade --install taskflow ./helm/taskflow \
  --namespace taskflow \
  -f helm/taskflow/values.yaml \
  -f helm/taskflow/values-oke.yaml \
  --wait \
  --timeout 10m
```

Verify deployment:
```bash
kubectl get pods -n taskflow
```

Expected output:
```
NAME                                   READY   STATUS    RESTARTS   AGE
backend-deployment-xxx-yyy             2/2     Running   0          2m
frontend-deployment-xxx-yyy            1/1     Running   0          2m
notification-service-xxx-yyy           2/2     Running   0          2m
```

Note: Backend and notification show `2/2` because Dapr sidecar is injected.

### 8. Get LoadBalancer External IP

```bash
kubectl get svc frontend-service -n taskflow
```

Wait for `EXTERNAL-IP` to be assigned (may take 2-3 minutes):
```
NAME               TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)        AGE
frontend-service   LoadBalancer   10.96.255.169   129.151.146.217   80:32136/TCP   5m
```

## Accessing the Application

Once the LoadBalancer has an external IP:

1. **Frontend**: Open `http://<EXTERNAL-IP>` in your browser
2. **Backend API**: Available at `http://<EXTERNAL-IP>/api` (via frontend proxy)

Example:
```
http://129.151.146.217
```

## Verification

### Check All Services

```bash
# TaskFlow pods
kubectl get pods -n taskflow

# Kafka pods
kubectl get pods -n kafka

# Dapr system
kubectl get pods -n dapr-system

# Services
kubectl get svc -n taskflow
```

### Test Event Flow

1. Create a task via the frontend
2. Check backend logs for event publishing:
   ```bash
   kubectl logs -n taskflow -l app=backend -c backend --tail=20
   ```
3. Check notification service logs for reminder events:
   ```bash
   kubectl logs -n taskflow -l app=notification -c notification --tail=20
   ```

### Check Kafka Topics

```bash
kubectl get kafkatopics -n kafka
```

Expected:
- `task-events` (3 partitions, replication 1)
- `reminders` (1 partition, replication 1)

## Troubleshooting

### Pods Not Starting

**Issue**: `ImagePullBackOff` error

**Cause**: Short name mode enforcing in OKE

**Fix**: Use fully qualified image names in `values-oke.yaml`:
```yaml
image:
  repository: docker.io/username/image  # NOT just username/image
```

### LoadBalancer Stuck in Pending

**Issue**: `EXTERNAL-IP` shows `<pending>` indefinitely

**Cause**: Oracle Cloud LoadBalancer provisioning delay or limit reached

**Fix**:
1. Wait up to 5 minutes
2. Check OCI Console → Networking → Load Balancers
3. Verify you haven't exceeded free tier limits (2 LoadBalancers max)

### Dapr Sidecar Not Injecting

**Issue**: Pods show `1/1` instead of `2/2` for backend/notification

**Cause**: Dapr annotations missing or Dapr not installed

**Fix**:
```bash
# Verify Dapr components
kubectl get components -n taskflow

# Check deployment annotations
kubectl get deployment backend-deployment -n taskflow -o yaml | grep dapr.io
```

### Kafka Connection Errors

**Issue**: Backend logs show "Failed to publish event"

**Cause**: Incorrect Kafka bootstrap server

**Fix**: Verify Kafka service name:
```bash
kubectl get svc -n kafka | grep bootstrap
# Should show: taskflow-kafka-kafka-bootstrap

# Update values-oke.yaml if needed:
kafka:
  bootstrapServer: taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
```

### Check Logs

Backend:
```bash
kubectl logs -n taskflow -l app=backend -c backend --tail=50 -f
```

Frontend:
```bash
kubectl logs -n taskflow -l app=frontend --tail=50 -f
```

Notification:
```bash
kubectl logs -n taskflow -l app=notification -c notification --tail=50 -f
```

Dapr sidecar:
```bash
kubectl logs -n taskflow -l app=backend -c daprd --tail=50 -f
```

## Cleanup

### Delete TaskFlow Application

```bash
helm uninstall taskflow --namespace taskflow
kubectl delete namespace taskflow
```

### Delete Kafka

```bash
kubectl delete -f k8s/kafka/kafka-cluster-kraft.yaml
kubectl delete namespace kafka
```

### Delete Dapr

```bash
helm uninstall dapr --namespace dapr-system
kubectl delete namespace dapr-system
```

### Delete OKE Cluster

**Via Console**:
1. Navigate to **Kubernetes Clusters (OKE)**
2. Select `taskflow-cluster`
3. Click **Delete** and confirm

**Via CLI**:
```bash
oci ce cluster delete --cluster-id <your-cluster-ocid>
```

**Note**: Deleting the cluster also deletes associated LoadBalancers and storage resources.

## Cost Optimization

### Oracle Free Tier Limits

- **Compute**: 4 OCPUs, 24GB RAM (Always Free)
- **LoadBalancers**: 2 total (50 Mbps each)
- **Block Storage**: 200GB total

### Minimize Costs

1. **Use 1 Kafka broker** (not 3) for development
2. **Set replica count to 1** for backend and frontend
3. **Delete cluster when not in use** - recreate from Helm charts
4. **Use ephemeral storage** for Kafka (no persistent volumes)

### Estimated Resource Usage

- **Kafka**: ~1.5GB RAM, 1 CPU
- **Dapr System**: ~512MB RAM, 0.5 CPU
- **TaskFlow Services**: ~768MB RAM, 0.8 CPU (3 pods)
- **Total**: ~2.8GB RAM, 2.3 CPU (within free tier)

## Next Steps

- [Phase V Part C Testing Guide](./PHASE-V-PART-C-TESTING-GUIDE.md)
- [Production Deployment Checklist](./production-checklist.md)
- [Monitoring with Prometheus and Grafana](./monitoring-setup.md)

## Support

- **Oracle Cloud Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Strimzi Docs**: https://strimzi.io/docs/
- **Dapr Docs**: https://docs.dapr.io/
- **TaskFlow Issues**: https://github.com/<your-org>/<repo>/issues
