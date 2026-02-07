# Kafka Deployment Guide (Strimzi Operator)

This directory contains Kubernetes manifests for deploying Apache Kafka on Minikube using the Strimzi operator.

## Overview

- **Operator**: Strimzi Kafka Operator v0.43.0
- **Kafka Version**: 3.7.0
- **Cluster Setup**: Single-broker for development (ephemeral storage)
- **Topics**: `task-events` (3 partitions), `reminders` (1 partition)

## Prerequisites

- Minikube running with at least 4GB RAM
- kubectl configured to use Minikube context
- Minimum 2 CPU cores available

## Installation Steps

### 1. Install Strimzi Operator

Install the Strimzi operator using the official release manifests:

```bash
# Create kafka namespace
kubectl create namespace kafka

# Install Strimzi operator (v0.43.0)
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Verify operator is running
kubectl get pods -n kafka
# Expected output: strimzi-cluster-operator-xxxxx Running
```

**Alternative: Using local manifests**

If you prefer to use local manifests:

```bash
# Download Strimzi operator manifests
curl -L https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.43.0/strimzi-cluster-operator-0.43.0.yaml \
  -o k8s/kafka/strimzi-operator.yaml

# Apply operator
kubectl apply -f k8s/kafka/namespace.yaml
kubectl apply -f k8s/kafka/strimzi-operator.yaml -n kafka
```

### 2. Deploy Kafka Cluster

Deploy the Kafka cluster (1 broker, 1 zookeeper):

```bash
# Apply Kafka cluster manifest
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# Wait for Kafka cluster to be ready (may take 3-5 minutes)
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=600s -n kafka

# Check cluster status
kubectl get kafka -n kafka
# Expected output: taskflow-kafka Ready
```

**Verify pods are running:**

```bash
kubectl get pods -n kafka

# Expected pods:
# - taskflow-kafka-zookeeper-0        (Zookeeper)
# - taskflow-kafka-kafka-0            (Kafka broker)
# - taskflow-kafka-entity-operator-*  (Topic/User operator)
```

### 3. Create Kafka Topics

Create the required topics for TaskFlow:

```bash
# Apply topics manifest
kubectl apply -f k8s/kafka/topics.yaml

# Verify topics created
kubectl get kafkatopics -n kafka

# Expected topics:
# - task-events  (3 partitions, replication: 1)
# - reminders    (1 partition, replication: 1)
```

**Check topic details:**

```bash
# Describe task-events topic
kubectl describe kafkatopic task-events -n kafka

# Describe reminders topic
kubectl describe kafkatopic reminders -n kafka
```

### 4. Get Kafka Connection String

The Kafka bootstrap server is accessible within the cluster at:

```
taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
```

This connection string is used by:
- Backend application (via Dapr pub/sub component)
- Notification service (via Dapr subscription)

## Testing Kafka Cluster

### Test 1: Produce Messages

```bash
# Start a producer pod
kubectl run kafka-producer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-producer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events

# Type test messages and press Ctrl+C to exit
```

### Test 2: Consume Messages

```bash
# Start a consumer pod
kubectl run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# Press Ctrl+C to exit
```

### Test 3: List Topics

```bash
# List all topics
kubectl run kafka-topics -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.7.0 \
  --rm=true --restart=Never -n kafka -- \
  bin/kafka-topics.sh \
  --bootstrap-server taskflow-kafka-kafka-bootstrap:9092 \
  --list
```

## Monitoring

### View Kafka Broker Logs

```bash
kubectl logs -f taskflow-kafka-kafka-0 -n kafka
```

### View Zookeeper Logs

```bash
kubectl logs -f taskflow-kafka-zookeeper-0 -n kafka
```

### View Entity Operator Logs

```bash
# Topic operator logs
kubectl logs -f deployment/taskflow-kafka-entity-operator -c topic-operator -n kafka

# User operator logs
kubectl logs -f deployment/taskflow-kafka-entity-operator -c user-operator -n kafka
```

## Troubleshooting

### Issue: Kafka pod stuck in Pending

**Cause**: Insufficient resources in Minikube

**Solution**:
```bash
# Stop Minikube
minikube stop

# Start with more resources
minikube start --cpus=4 --memory=8192
```

### Issue: Kafka pod in CrashLoopBackOff

**Cause**: Storage issues or configuration errors

**Solution**:
```bash
# Check pod events
kubectl describe pod taskflow-kafka-kafka-0 -n kafka

# Check logs
kubectl logs taskflow-kafka-kafka-0 -n kafka

# If needed, delete and recreate
kubectl delete kafka taskflow-kafka -n kafka
kubectl apply -f k8s/kafka/kafka-cluster.yaml
```

### Issue: Topics not creating

**Cause**: Entity operator not running

**Solution**:
```bash
# Check entity operator status
kubectl get pods -n kafka | grep entity-operator

# Restart entity operator if needed
kubectl rollout restart deployment/taskflow-kafka-entity-operator -n kafka
```

### Issue: Cannot connect to Kafka from other pods

**Cause**: DNS resolution or network policy issues

**Solution**:
```bash
# Test DNS resolution from another pod
kubectl run -ti test-dns --image=busybox --rm=true --restart=Never -- \
  nslookup taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local

# Check Kafka service
kubectl get svc -n kafka
```

## Scaling for Production (OKE)

For Oracle OKE deployment, update `kafka-cluster.yaml`:

```yaml
spec:
  kafka:
    replicas: 3  # Change from 1 to 3
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: persistent-claim  # Change from ephemeral
      size: 20Gi
      class: oci-bv  # Oracle block volume
```

Then update topics to use replication factor 3:

```yaml
spec:
  replicas: 3  # Change from 1 to 3
```

## Cleanup

Remove Kafka cluster and operator:

```bash
# Delete topics
kubectl delete -f k8s/kafka/topics.yaml

# Delete Kafka cluster
kubectl delete -f k8s/kafka/kafka-cluster.yaml

# Delete operator
kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Delete namespace
kubectl delete namespace kafka
```

## Resources

- [Strimzi Documentation](https://strimzi.io/docs/operators/latest/overview.html)
- [Kafka Configuration Reference](https://kafka.apache.org/documentation/#configuration)
- [Strimzi GitHub](https://github.com/strimzi/strimzi-kafka-operator)

## Next Steps

After Kafka is running:
1. Install Dapr (see `/k8s/dapr/README.md`)
2. Deploy Dapr pub/sub component (see `/k8s/dapr/pubsub-kafka.yaml`)
3. Deploy backend with Dapr annotations
4. Deploy notification service
