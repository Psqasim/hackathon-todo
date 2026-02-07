# Dapr Installation and Configuration Guide

This directory contains Dapr components for TaskFlow event-driven architecture.

## Overview

- **Dapr Version**: 1.14+
- **Components**:
  - Pub/Sub (Kafka via Strimzi)
  - State Store (PostgreSQL - optional for Phase 5)
  - Secret Store (Kubernetes secrets)

## Prerequisites

- Kubernetes cluster running (Minikube or OKE)
- Kafka cluster deployed (see `/k8s/kafka/README.md`)
- kubectl configured

## Installation Steps

### 1. Install Dapr CLI

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
```

**Windows (PowerShell):**
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Verify installation:**
```bash
dapr --version
# Expected: CLI version: 1.14.0+
```

### 2. Initialize Dapr on Kubernetes

Initialize Dapr in your Kubernetes cluster:

```bash
# Initialize Dapr with default configuration
dapr init -k --wait --timeout 300

# Verify Dapr installation
dapr status -k
```

**Expected output:**
```
  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
  dapr-operator          dapr-system  True     Running  1         1.14.0   1m   2024-02-05 12:00.00
  dapr-sidecar-injector  dapr-system  True     Running  1         1.14.0   1m   2024-02-05 12:00.00
  dapr-sentry            dapr-system  True     Running  1         1.14.0   1m   2024-02-05 12:00.00
  dapr-placement-server  dapr-system  True     Running  1         1.14.0   1m   2024-02-05 12:00.00
```

### 3. Verify Dapr System Pods

```bash
kubectl get pods -n dapr-system

# Expected pods:
# - dapr-operator-*
# - dapr-sidecar-injector-*
# - dapr-sentry-*
# - dapr-placement-server-*
```

### 4. Deploy Dapr Components

Apply Dapr component manifests to the taskflow namespace:

```bash
# Ensure taskflow namespace exists
kubectl get namespace taskflow || kubectl create namespace taskflow

# Apply Dapr components
kubectl apply -f k8s/dapr/pubsub-kafka.yaml
kubectl apply -f k8s/dapr/subscription-reminders.yaml

# Optional: Apply state store if using Dapr state management
# kubectl apply -f k8s/dapr/state-postgresql.yaml

# Verify components
kubectl get components -n taskflow
```

**Expected components:**
```
NAME                TYPE           VERSION  AGE
taskflow-pubsub     pubsub.kafka   v1       1m
```

## Dapr Components

### 1. Pub/Sub (Kafka)

**File**: `pubsub-kafka.yaml`

Connects to Strimzi Kafka cluster for event publishing and subscription.

**Connection**: `taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092`

**Topics**:
- `task-events`: All task lifecycle events (created, updated, completed, deleted)
- `reminders`: Task reminder notifications

### 2. Subscriptions

**File**: `subscription-reminders.yaml`

Declarative subscription for the notification service to consume reminder events.

**Route**: `/events/reminders` on notification-service

## Using Dapr with TaskFlow

### Backend Service (Publisher)

The backend service publishes events to Kafka via Dapr HTTP API:

```python
import httpx

async def publish_event(topic: str, data: dict):
    dapr_url = "http://localhost:3500/v1.0/publish/taskflow-pubsub/{topic}"
    async with httpx.AsyncClient() as client:
        await client.post(dapr_url, json=data)
```

**Dapr Annotations** (already in Helm template):
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "taskflow-backend"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "info"
```

### Notification Service (Subscriber)

The notification service subscribes to topics via Dapr subscription endpoint:

```python
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "taskflow-pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]

@app.post("/events/reminders")
async def handle_reminder(event: dict):
    # Process reminder event
    pass
```

**Dapr Annotations**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "notification-service"
  dapr.io/app-port: "8001"
```

## Testing Dapr Components

### Test 1: Verify Component Registration

```bash
# Check Dapr components in taskflow namespace
kubectl get components -n taskflow

# Describe pub/sub component
kubectl describe component taskflow-pubsub -n taskflow
```

### Test 2: Check Dapr Sidecar Injection

Deploy a pod with Dapr annotations and verify sidecar injection:

```bash
# After deploying backend or notification service
kubectl get pods -n taskflow

# Check pod has 2 containers (app + daprd)
kubectl get pod <pod-name> -n taskflow -o jsonpath='{.spec.containers[*].name}'
# Expected: backend daprd (or notification daprd)
```

### Test 3: View Dapr Sidecar Logs

```bash
# View Dapr sidecar logs for backend
kubectl logs -f <backend-pod-name> -c daprd -n taskflow

# View Dapr sidecar logs for notification service
kubectl logs -f <notification-pod-name> -c daprd -n taskflow
```

### Test 4: Publish Event via Dapr CLI

```bash
# Publish test event to task-events topic
dapr publish --publish-app-id taskflow-backend \
  --pubsub taskflow-pubsub \
  --topic task-events \
  --data '{"event_type":"created","task_id":1,"user_id":"test@example.com"}'
```

### Test 5: Check Kafka Topic for Events

```bash
# Consume from task-events topic to verify Dapr published event
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning
```

## Monitoring Dapr

### View Dapr Dashboard (Optional)

```bash
# Install Dapr dashboard
dapr dashboard -k -p 9999

# Access at http://localhost:9999
```

### Check Dapr Metrics

Dapr exposes Prometheus metrics on port 9090 of each sidecar:

```bash
# Port-forward to access metrics
kubectl port-forward <pod-name> 9090:9090 -n taskflow

# Access metrics at http://localhost:9090/metrics
```

## Troubleshooting

### Issue: Dapr sidecar not injected

**Cause**: Missing Dapr annotations

**Solution**:
```yaml
# Ensure pod template has annotations
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "<app-name>"
    dapr.io/app-port: "<port>"
```

### Issue: Component not found

**Cause**: Component not applied to correct namespace

**Solution**:
```bash
# Components must be in same namespace as application
kubectl get components -n taskflow

# Re-apply if missing
kubectl apply -f k8s/dapr/pubsub-kafka.yaml
```

### Issue: Cannot connect to Kafka

**Cause**: Kafka cluster not accessible or wrong bootstrap server

**Solution**:
```bash
# Verify Kafka service
kubectl get svc -n kafka | grep bootstrap

# Test connectivity from taskflow namespace
kubectl run test-kafka -ti --rm=true --restart=Never \
  --image=busybox -n taskflow -- \
  nc -zv taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local 9092
```

### Issue: Events not publishing

**Cause**: Dapr sidecar errors or pub/sub component misconfiguration

**Solution**:
```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n taskflow

# Common errors:
# - "component not found" → Apply component to correct namespace
# - "connection refused" → Check Kafka cluster status
# - "authentication failed" → Verify Kafka credentials (if using auth)
```

### Issue: Subscription not working

**Cause**: Subscription route not accessible or app not responding

**Solution**:
```bash
# Check app logs
kubectl logs <notification-pod-name> -c notification -n taskflow

# Verify /dapr/subscribe endpoint
kubectl port-forward <notification-pod-name> 8001:8001 -n taskflow
curl http://localhost:8001/dapr/subscribe
```

## Scaling Considerations

### Development (Minikube)
- Dapr runs with default resource limits
- Suitable for testing and local development

### Production (OKE)
- Configure resource requests/limits for Dapr sidecars:

```yaml
annotations:
  dapr.io/sidecar-cpu-limit: "500m"
  dapr.io/sidecar-memory-limit: "256Mi"
  dapr.io/sidecar-cpu-request: "100m"
  dapr.io/sidecar-memory-request: "128Mi"
```

## Cleanup

Remove Dapr from Kubernetes:

```bash
# Delete Dapr components
kubectl delete -f k8s/dapr/pubsub-kafka.yaml
kubectl delete -f k8s/dapr/subscription-reminders.yaml

# Uninstall Dapr from cluster
dapr uninstall -k
```

## Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Pub/Sub Kafka](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Dapr CLI Reference](https://docs.dapr.io/reference/cli/)

## Next Steps

After Dapr is configured:
1. Update backend deployment with Dapr annotations (Helm chart)
2. Deploy notification service with Dapr sidecar
3. Test event publishing and subscription
4. Monitor event flow through Kafka and Dapr
