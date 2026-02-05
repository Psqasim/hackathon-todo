# Phase V Part B - Testing Guide
## Kafka + Dapr + Notification Service on Minikube

This guide provides step-by-step instructions for deploying and testing the complete event-driven architecture on Minikube.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Strimzi Kafka Deployment](#strimzi-kafka-deployment)
4. [Dapr Installation](#dapr-installation)
5. [Backend Deployment with Dapr](#backend-deployment-with-dapr)
6. [Notification Service Deployment](#notification-service-deployment)
7. [End-to-End Testing](#end-to-end-testing)
8. [Troubleshooting](#troubleshooting)
9. [Cleanup](#cleanup)

---

## Prerequisites

### Required Tools

- **Minikube** v1.32+ (with Docker driver)
- **kubectl** v1.28+
- **Helm** v3.12+
- **Docker** v24.0+
- **Dapr CLI** v1.14+

### System Requirements

- **CPU**: Minimum 4 cores
- **RAM**: Minimum 8GB (12GB recommended)
- **Disk**: 20GB free space

### Verify Installation

```bash
# Check Minikube version
minikube version

# Check kubectl version
kubectl version --client

# Check Helm version
helm version

# Check Docker version
docker --version
```

---

## Environment Setup

### 1. Start Minikube

Start Minikube with sufficient resources:

```bash
# Start with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected output:**
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

### 2. Enable Required Addons

```bash
# Enable metrics-server for resource monitoring
minikube addons enable metrics-server

# Enable ingress (optional, for external access)
minikube addons enable ingress
```

### 3. Set kubectl Context

```bash
# Ensure kubectl is using minikube context
kubectl config use-context minikube

# Verify context
kubectl config current-context
# Output: minikube
```

---

## Strimzi Kafka Deployment

### 1. Create Kafka Namespace

```bash
# Create namespace for Kafka
kubectl create namespace kafka

# Verify namespace
kubectl get namespace kafka
```

### 2. Install Strimzi Operator

Install the Strimzi operator using the official release manifests:

```bash
# Install Strimzi operator v0.43.0
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready (30-60 seconds)
kubectl wait deployment/strimzi-cluster-operator \
  --for=condition=Available \
  --timeout=300s \
  -n kafka

# Verify operator is running
kubectl get pods -n kafka
```

**Expected output:**
```
NAME                                        READY   STATUS    RESTARTS   AGE
strimzi-cluster-operator-7d96cbff4b-xxxxx   1/1     Running   0          1m
```

### 3. Deploy Kafka Cluster

```bash
# Apply Kafka cluster manifest
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# Watch Kafka cluster provisioning (takes 3-5 minutes)
kubectl get kafka -n kafka -w

# Wait for Kafka to be ready
kubectl wait kafka/taskflow-kafka \
  --for=condition=Ready \
  --timeout=600s \
  -n kafka
```

**Expected output:**
```
NAME             DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS   READY   WARNINGS
taskflow-kafka   1                        1                     True
```

### 4. Verify Kafka Pods

```bash
# Check all Kafka-related pods
kubectl get pods -n kafka

# Expected pods:
# - taskflow-kafka-zookeeper-0 (Zookeeper)
# - taskflow-kafka-kafka-0 (Kafka broker)
# - taskflow-kafka-entity-operator-* (Topic/User operator)
# - strimzi-cluster-operator-* (Strimzi operator)
```

### 5. Create Kafka Topics

```bash
# Apply topics manifest
kubectl apply -f k8s/kafka/topics.yaml

# Verify topics created
kubectl get kafkatopics -n kafka
```

**Expected topics:**
```
NAME          CLUSTER          PARTITIONS   REPLICATION FACTOR   READY
task-events   taskflow-kafka   3            1                    True
reminders     taskflow-kafka   1            1                    True
```

### 6. Test Kafka Connectivity

```bash
# Test producing messages to task-events topic
kubectl run kafka-producer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-producer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events

# Type a test message and press Ctrl+C to exit
# Example: {"event_type":"test","task_id":1}
```

```bash
# Test consuming messages from task-events topic
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# You should see the test message you produced earlier
# Press Ctrl+C to exit
```

**Checkpoint:** ✅ Kafka cluster is running and topics are accessible

---

## Dapr Installation

### 1. Install Dapr CLI

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
```

**Windows (PowerShell as Administrator):**
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Verify installation:**
```bash
dapr --version
# Expected: CLI version: 1.14.0+
```

### 2. Initialize Dapr on Kubernetes

```bash
# Initialize Dapr in Kubernetes cluster
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
# Check Dapr system pods
kubectl get pods -n dapr-system

# All pods should be Running
```

### 4. Deploy Dapr Components

```bash
# Ensure taskflow namespace exists
kubectl get namespace taskflow || kubectl create namespace taskflow

# Apply Dapr pub/sub component
kubectl apply -f k8s/dapr/pubsub-kafka.yaml

# Apply Dapr subscription (for notification service)
kubectl apply -f k8s/dapr/subscription-reminders.yaml

# Verify components
kubectl get components -n taskflow
```

**Expected output:**
```
NAME              SCOPES   VERSION   AGE
taskflow-pubsub            v1        1m
```

```bash
# Verify subscription
kubectl get subscriptions -n taskflow
```

**Expected output:**
```
NAME                     AGE
reminders-subscription   1m
```

**Checkpoint:** ✅ Dapr is installed and components are configured

---

## Backend Deployment with Dapr

### 1. Build Backend Docker Image

```bash
# Build backend image with Kubernetes-specific Dockerfile
docker build -t taskflow-backend:latest -f Dockerfile.k8s .

# Load image into Minikube
minikube image load taskflow-backend:latest

# Verify image is loaded
minikube image ls | grep taskflow-backend
```

### 2. Update Helm Values for Dapr

Create a `values-dapr.yaml` file with Dapr enabled:

```yaml
# values-dapr.yaml
dapr:
  enabled: true
  pubsubName: taskflow-pubsub
  logLevel: info

kafka:
  bootstrapServer: taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092

notification:
  enabled: false  # Will enable after backend is running
```

### 3. Deploy Backend with Helm

```bash
# Deploy backend with Dapr enabled
helm upgrade --install taskflow ./helm/taskflow \
  -f helm/taskflow/values-dapr.yaml \
  --set secrets.databaseUrl="<your-database-url>" \
  --set secrets.jwtSecretKey="<your-jwt-secret>" \
  --set secrets.openaiApiKey="<your-openai-key>" \
  --namespace taskflow \
  --create-namespace

# Wait for backend to be ready
kubectl wait deployment/backend-deployment \
  --for=condition=Available \
  --timeout=300s \
  -n taskflow
```

### 4. Verify Backend Pod has Dapr Sidecar

```bash
# Check backend pod has 2 containers (app + daprd)
kubectl get pods -n taskflow

# Get container names for backend pod
kubectl get pod -l app=taskflow-backend -n taskflow \
  -o jsonpath='{.items[0].spec.containers[*].name}'

# Expected: backend daprd
```

### 5. Check Dapr Sidecar Logs

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -l app=taskflow-backend -n taskflow -o jsonpath='{.items[0].metadata.name}')

# View Dapr sidecar logs
kubectl logs $BACKEND_POD -c daprd -n taskflow

# Look for successful Dapr initialization and component loading
```

**Expected log messages:**
- "Dapr sidecar is up and running"
- "component loaded. name: taskflow-pubsub"
- "app is subscribed to the following topics"

### 6. Test Event Publishing

Access the backend and create a task to trigger event publishing:

```bash
# Port-forward to backend service
kubectl port-forward svc/backend-service 8000:8000 -n taskflow

# In another terminal, create a task via API
curl -X POST http://localhost:8000/api/<user-id>/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "title": "Test Event Publishing",
    "description": "Testing Kafka events via Dapr",
    "due_date": "2024-12-31T23:59:59Z"
  }'
```

### 7. Verify Event in Kafka

```bash
# Consume from task-events topic to verify event was published
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# You should see a "task.created" event
# Press Ctrl+C to exit
```

**Checkpoint:** ✅ Backend is publishing events to Kafka via Dapr

---

## Notification Service Deployment

### 1. Build Notification Service Image

```bash
# Build notification service image
docker build -t taskflow-notification:latest \
  -f src/services/notification/Dockerfile \
  src/services/notification/

# Load image into Minikube
minikube image load taskflow-notification:latest

# Verify image is loaded
minikube image ls | grep taskflow-notification
```

### 2. Update Helm Values to Enable Notification Service

Update `values-dapr.yaml`:

```yaml
# values-dapr.yaml
dapr:
  enabled: true
  pubsubName: taskflow-pubsub
  logLevel: info

kafka:
  bootstrapServer: taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092

notification:
  enabled: true  # Enable notification service
  replicas: 1
  image: taskflow-notification
  tag: latest
  imagePullPolicy: Never
```

### 3. Deploy Notification Service via Helm

```bash
# Upgrade Helm release to include notification service
helm upgrade --install taskflow ./helm/taskflow \
  -f helm/taskflow/values-dapr.yaml \
  --set secrets.databaseUrl="<your-database-url>" \
  --set secrets.jwtSecretKey="<your-jwt-secret>" \
  --set secrets.openaiApiKey="<your-openai-key>" \
  --namespace taskflow

# Wait for notification service to be ready
kubectl wait deployment/notification-service \
  --for=condition=Available \
  --timeout=300s \
  -n taskflow
```

### 4. Verify Notification Service Pod

```bash
# Check notification service pod has 2 containers (app + daprd)
kubectl get pods -n taskflow

# Get container names for notification pod
kubectl get pod -l app=notification-service -n taskflow \
  -o jsonpath='{.items[0].spec.containers[*].name}'

# Expected: notification daprd
```

### 5. Check Notification Service Logs

```bash
# Get notification pod name
NOTIF_POD=$(kubectl get pod -l app=notification-service -n taskflow -o jsonpath='{.items[0].metadata.name}')

# View application logs
kubectl logs $NOTIF_POD -c notification -n taskflow -f

# Expected log messages:
# - "TaskFlow Notification Service starting up..."
# - "Notification Service ready to receive events"
```

### 6. Check Dapr Subscription Registration

```bash
# View Dapr sidecar logs for notification service
kubectl logs $NOTIF_POD -c daprd -n taskflow

# Look for:
# - "app is subscribed to the following topics: [reminders]"
# - "subscription initialized"
```

**Checkpoint:** ✅ Notification service is deployed and subscribed to reminders topic

---

## End-to-End Testing

### Test 1: Task Creation Event Flow

**Goal:** Verify task creation publishes event to Kafka

```bash
# 1. Create a task via API
curl -X POST http://localhost:8000/api/<user-id>/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "title": "E2E Test Task",
    "description": "Testing event-driven architecture",
    "due_date": "2024-12-31T23:59:59Z"
  }'

# 2. Check task-events topic for event
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# Expected: CloudEvent with event_type="created"
```

**Success Criteria:**
- ✅ Task created successfully via API
- ✅ Event appears in task-events topic
- ✅ Event contains task_id, user_id, event_type="created"

### Test 2: Reminder Event Flow

**Goal:** Verify reminder event is published and consumed by notification service

```bash
# 1. Create a task with due_date (triggers reminder event)
curl -X POST http://localhost:8000/api/<user-id>/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "title": "Reminder Test Task",
    "description": "Task to test reminders",
    "due_date": "2024-12-31T14:00:00Z"
  }'

# 2. Check reminders topic
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic reminders \
  --from-beginning

# 3. Check notification service logs for reminder processing
kubectl logs $NOTIF_POD -c notification -n taskflow -f

# Expected log output:
# ╔══════════════════════════════════════════════════════════╗
# ║              🔔 TASK REMINDER NOTIFICATION               ║
# ╠══════════════════════════════════════════════════════════╣
# ║ Task ID:    <task-id>                                    ║
# ║ Title:      Reminder Test Task                           ║
# ║ User:       <user-id>                                    ║
# ║ Due At:     2024-12-31T14:00:00Z                         ║
# ║ Remind At:  2024-12-31T13:00:00Z                         ║
# ╚══════════════════════════════════════════════════════════╝
```

**Success Criteria:**
- ✅ Reminder event appears in reminders topic
- ✅ Notification service logs show reminder notification
- ✅ Reminder event contains task details

### Test 3: Task Update Event Flow

**Goal:** Verify task updates publish events

```bash
# 1. Update a task
curl -X PUT http://localhost:8000/api/<user-id>/tasks/<task-id> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "title": "Updated Task Title",
    "description": "Updated description"
  }'

# 2. Check task-events topic
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# Expected: CloudEvent with event_type="updated"
```

**Success Criteria:**
- ✅ Task updated successfully
- ✅ Update event appears in Kafka
- ✅ Event contains updated task data

### Test 4: Task Completion Event Flow

**Goal:** Verify task completion publishes events

```bash
# 1. Complete a task
curl -X PATCH http://localhost:8000/api/<user-id>/tasks/<task-id>/complete \
  -H "Authorization: Bearer <your-jwt-token>"

# 2. Check task-events topic
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# Expected: CloudEvent with event_type="completed"
```

**Success Criteria:**
- ✅ Task marked as completed
- ✅ Completion event appears in Kafka
- ✅ Event contains task_id and completion status

### Test 5: Dapr Dashboard (Optional)

View event flow in Dapr dashboard:

```bash
# Start Dapr dashboard
dapr dashboard -k -p 9999

# Access at http://localhost:9999
# Navigate to:
# - Applications: See taskflow-backend and notification-service
# - Components: See taskflow-pubsub component
# - Subscriptions: See reminders subscription
```

### Test 6: Full Stack Integration

**Goal:** Test complete flow from frontend to notification

```bash
# 1. Port-forward frontend
kubectl port-forward svc/taskflow-frontend 3000:80 -n taskflow

# 2. Access frontend at http://localhost:3000

# 3. Create a task with due date via UI

# 4. Monitor backend logs
kubectl logs -f deployment/backend-deployment -c backend -n taskflow

# 5. Monitor notification service logs
kubectl logs -f deployment/notification-service -c notification -n taskflow

# 6. Verify event flow:
#    Frontend → Backend → Dapr → Kafka → Dapr → Notification Service
```

**Success Criteria:**
- ✅ Task created via frontend
- ✅ Backend publishes event to Kafka
- ✅ Notification service receives and logs reminder
- ✅ No errors in any component logs

---

## Troubleshooting

### Issue 1: Kafka Pods Stuck in Pending

**Symptoms:**
- Kafka or Zookeeper pods in Pending state
- Error: "Insufficient CPU" or "Insufficient memory"

**Solution:**
```bash
# Check resource availability
kubectl describe pod taskflow-kafka-kafka-0 -n kafka

# Increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=12288

# Redeploy Kafka
kubectl delete kafka taskflow-kafka -n kafka
kubectl apply -f k8s/kafka/kafka-cluster.yaml
```

### Issue 2: Dapr Sidecar Not Injected

**Symptoms:**
- Pod has only 1 container instead of 2
- No daprd sidecar

**Solution:**
```bash
# Check Dapr annotations
kubectl get pod <pod-name> -n taskflow -o yaml | grep dapr.io

# Verify dapr-sidecar-injector is running
kubectl get pods -n dapr-system

# Restart deployment to trigger injection
kubectl rollout restart deployment/<deployment-name> -n taskflow
```

### Issue 3: Events Not Publishing to Kafka

**Symptoms:**
- No events in Kafka topics
- Backend logs show no event publishing

**Solution:**
```bash
# Check Dapr pub/sub component
kubectl describe component taskflow-pubsub -n taskflow

# Check Dapr sidecar logs
kubectl logs <backend-pod> -c daprd -n taskflow

# Test Dapr connection
kubectl exec -it <backend-pod> -c backend -n taskflow -- \
  curl http://localhost:3500/v1.0/metadata

# Verify Kafka connectivity from backend pod
kubectl exec -it <backend-pod> -c backend -n taskflow -- \
  nc -zv taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local 9092
```

### Issue 4: Notification Service Not Receiving Events

**Symptoms:**
- Events in Kafka but not in notification logs
- No subscription errors

**Solution:**
```bash
# Check subscription registration
kubectl get subscriptions -n taskflow
kubectl describe subscription reminders-subscription -n taskflow

# Verify /dapr/subscribe endpoint
kubectl exec -it <notification-pod> -c notification -n taskflow -- \
  curl http://localhost:8001/dapr/subscribe

# Check Dapr subscription logs
kubectl logs <notification-pod> -c daprd -n taskflow | grep subscribe

# Manually publish test event
dapr publish --publish-app-id notification-service \
  --pubsub taskflow-pubsub \
  --topic reminders \
  --data '{"task_id":1,"user_id":"test","title":"Test","due_at":"2024-12-31T23:59:59Z"}'
```

### Issue 5: Backend Can't Connect to Database

**Symptoms:**
- Backend pod CrashLoopBackOff
- Logs show database connection errors

**Solution:**
```bash
# Check database URL secret
kubectl get secret taskflow-secrets -n taskflow -o yaml

# Verify DATABASE_URL is correct
kubectl exec -it <backend-pod> -c backend -n taskflow -- env | grep DATABASE_URL

# Test database connectivity
kubectl run pg-test -ti --rm=true --restart=Never \
  --image=postgres:15 -- \
  psql "<database-url>"
```

### Issue 6: Kafka Topics Not Creating

**Symptoms:**
- KafkaTopic resources exist but topics not in Kafka

**Solution:**
```bash
# Check entity operator logs
kubectl logs deployment/taskflow-kafka-entity-operator -c topic-operator -n kafka

# Verify topic operator is running
kubectl get pods -n kafka | grep entity-operator

# Recreate topics
kubectl delete -f k8s/kafka/topics.yaml
kubectl apply -f k8s/kafka/topics.yaml

# List topics directly in Kafka
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

---

## Cleanup

### Remove Notification Service

```bash
# Disable notification service in Helm
helm upgrade --install taskflow ./helm/taskflow \
  -f helm/taskflow/values-dapr.yaml \
  --set notification.enabled=false \
  --namespace taskflow
```

### Remove Dapr Components

```bash
# Delete Dapr components
kubectl delete -f k8s/dapr/subscription-reminders.yaml
kubectl delete -f k8s/dapr/pubsub-kafka.yaml

# Uninstall Dapr from cluster
dapr uninstall -k
```

### Remove Kafka Cluster

```bash
# Delete Kafka topics
kubectl delete -f k8s/kafka/topics.yaml

# Delete Kafka cluster
kubectl delete -f k8s/kafka/kafka-cluster.yaml

# Delete Strimzi operator
kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Delete Kafka namespace
kubectl delete namespace kafka
```

### Remove TaskFlow Deployment

```bash
# Uninstall Helm release
helm uninstall taskflow -n taskflow

# Delete namespace
kubectl delete namespace taskflow
```

### Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# (Optional) Delete Minikube cluster completely
minikube delete
```

---

## Success Metrics

Upon completing this testing guide, you should have:

- ✅ **Kafka Cluster**: 1 broker + 1 zookeeper running in kafka namespace
- ✅ **Kafka Topics**: task-events (3 partitions) and reminders (1 partition)
- ✅ **Dapr**: Installed with pub/sub component and subscription configured
- ✅ **Backend**: Deployed with Dapr sidecar, publishing events to Kafka
- ✅ **Notification Service**: Deployed with Dapr sidecar, consuming reminder events
- ✅ **Event Flow**: Task CRUD operations trigger events → Kafka → Notification logs
- ✅ **Zero Errors**: All pods running, no CrashLoopBackOff, all health checks passing

---

## Next Steps

After successful testing on Minikube:

1. **Phase V Part C**: Deploy to Oracle OKE cloud
2. **Scaling**: Increase Kafka brokers to 3, add replication
3. **Monitoring**: Add Prometheus + Grafana for metrics
4. **Alerting**: Configure alerts for Kafka lag and Dapr errors
5. **Production**: Replace ephemeral storage with persistent volumes

---

## Additional Resources

- [Strimzi Quickstart](https://strimzi.io/quickstarts/)
- [Dapr Kubernetes Guide](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

---

**Document Version**: 1.0.0
**Last Updated**: 2024-02-05
**Phase**: V - Part B (Minikube Deployment)
