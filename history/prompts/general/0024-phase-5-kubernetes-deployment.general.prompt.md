---
id: 0024
title: Phase 5 Kubernetes Deployment Testing
stage: general
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-advanced-cloud-kafka-dapr
user: ps_qasim
command: deployment-testing
labels: ["phase-5", "kubernetes", "kafka", "dapr", "deployment", "troubleshooting"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - k8s/kafka/kafka-cluster-kraft.yaml
  - k8s/dapr/subscription-reminders.yaml
  - helm/taskflow/templates/dapr-subscription.yaml
  - helm/taskflow/templates/backend-deployment.yaml
  - helm/taskflow/values.yaml
  - scripts/start-backend.sh
tests:
  - Manual Kubernetes deployment verification
  - Kafka cluster health check
  - Dapr component validation
  - Pod status verification
---

## Prompt

Deploy and test Phase 5 Part B infrastructure on Minikube/Docker Desktop Kubernetes. User provided comprehensive 8-step deployment guide with prerequisites, commands, expected results, and troubleshooting.

## Response

Successfully deployed majority of Phase 5 infrastructure to Docker Desktop Kubernetes with multiple manifest fixes:

**Deployed Components:**
- ✅ Kafka (Strimzi): Running with KRaft mode, 2 topics created
- ✅ Dapr: All 6 system components healthy
- ✅ Notification Service: Running (2/2 pods) with Dapr sidecar
- ✅ Frontend: Running (1/1 pods)
- ⚠️ Backend: CrashLoopBackOff - FastAPI not responding to health checks

**Manifest Fixes Applied:**
1. k8s/kafka/kafka-cluster-kraft.yaml - Created new file for KRaft mode (Kafka 4.1.1, no ZooKeeper)
2. k8s/dapr/subscription-reminders.yaml - Removed invalid scopes and bulkSubscribe fields
3. helm/taskflow/templates/dapr-subscription.yaml - Same fix
4. helm/taskflow/templates/backend-deployment.yaml - Fixed Dapr app-port (8000 → 7860)
5. helm/taskflow/values.yaml - Fixed maxMessageBytes format ("1024000" string) and initialOffset (newest)
6. scripts/start-backend.sh - Added FastAPI error logging

**Errors Resolved:**
- Kafka version 3.7.0 unsupported → Updated to 4.1.1
- ZooKeeper deprecated → Migrated to KRaft with KafkaNodePool CRD
- maxMessageBytes scientific notation → Fixed to plain string
- initialOffset "latest" invalid → Changed to "newest"
- Dapr subscription v2alpha1 invalid fields → Removed scopes/bulkSubscribe

**Tools Installed:**
- Helm 3.20.0 (to ~/.local/bin/)
- Dapr CLI (to ~/.dapr/)

## Outcome

- ✅ Impact: 75% deployment success - Kafka, Dapr, notification service, frontend operational
- ⚠️ Tests: Backend health check failing - requires further debugging
- 📁 Files: 6 files modified, 1 file created (kafka-cluster-kraft.yaml)
- 🔁 Next prompts: Debug backend FastAPI startup issue, verify end-to-end event flow
- 🧠 Reflection: Strimzi 0.46.0+ requires KRaft mode; Dapr v2alpha1 API simplified (no scopes); proper Helm metadata critical for namespace management

## Evaluation notes

- Failure modes observed: Backend FastAPI silent failure, Helm timeout on pod readiness
- Graders run and results: Manual verification - Kafka healthy, Dapr healthy, notification running
- Next experiment: Investigate FastAPI startup with direct container debugging or simplified health check
