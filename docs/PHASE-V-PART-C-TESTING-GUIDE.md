# Phase V Part C - Oracle OKE Testing Guide

This guide provides comprehensive testing procedures for validating the TaskFlow deployment on Oracle Cloud OKE.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Infrastructure Verification](#infrastructure-verification)
- [Functional Testing](#functional-testing)
- [Event-Driven Architecture Testing](#event-driven-architecture-testing)
- [Performance Testing](#performance-testing)
- [Backward Compatibility Testing](#backward-compatibility-testing)
- [Logs and Monitoring](#logs-and-monitoring)

## Prerequisites

- TaskFlow deployed to Oracle OKE (following [ORACLE-CLOUD-DEPLOYMENT.md](./ORACLE-CLOUD-DEPLOYMENT.md))
- `kubectl` configured with OKE context
- External IP address for frontend service

## Infrastructure Verification

### 1. Verify OKE Cluster

```bash
kubectl get nodes
```

**Expected**:
```
NAME          STATUS   ROLES   AGE   VERSION
10.0.10.153   Ready    node    1h    v1.34.2
10.0.10.227   Ready    node    1h    v1.34.2
```

✅ **Pass Criteria**: 2 nodes in Ready status

### 2. Verify Namespaces

```bash
kubectl get namespaces
```

**Expected**:
```
NAME           STATUS   AGE
default        Active   1h
kafka          Active   45m
taskflow       Active   30m
dapr-system    Active   40m
```

✅ **Pass Criteria**: All required namespaces present

### 3. Verify Kafka Cluster

```bash
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

**Expected**:
```
NAME             READY
taskflow-kafka   True

NAME                                              READY   STATUS    RESTARTS   AGE
strimzi-cluster-operator-xxx                      1/1     Running   0          45m
taskflow-kafka-taskflow-kafka-pool-0              1/1     Running   0          44m
taskflow-kafka-entity-operator-xxx                2/2     Running   0          44m
```

✅ **Pass Criteria**:
- Kafka cluster status: `Ready=True`
- All pods: `Running` status

### 4. Verify Kafka Topics

```bash
kubectl get kafkatopics -n kafka
```

**Expected**:
```
NAME          CLUSTER          PARTITIONS   REPLICATION   READY
task-events   taskflow-kafka   3            1             True
reminders     taskflow-kafka   1            1             True
```

✅ **Pass Criteria**:
- `task-events`: 3 partitions, Ready
- `reminders`: 1 partition, Ready

### 5. Verify Dapr System

```bash
kubectl get pods -n dapr-system
```

**Expected**:
```
NAME                                    READY   STATUS    RESTARTS   AGE
dapr-operator-xxx                       1/1     Running   0          40m
dapr-sentry-xxx                         1/1     Running   0          40m
dapr-sidecar-injector-xxx               1/1     Running   0          40m
dapr-placement-server-0                 1/1     Running   0          40m
dapr-scheduler-server-0                 1/1     Running   0          40m
dapr-scheduler-server-1                 1/1     Running   0          40m
dapr-scheduler-server-2                 1/1     Running   0          40m
```

✅ **Pass Criteria**: All pods `Running`, 7 total pods

### 6. Verify Dapr Components

```bash
kubectl get components -n taskflow
kubectl get subscriptions -n taskflow
```

**Expected**:
```
NAME               AGE
taskflow-pubsub    30m

NAME                     AGE
reminders-subscription   30m
```

✅ **Pass Criteria**:
- `taskflow-pubsub` component present
- `reminders-subscription` subscription present

### 7. Verify TaskFlow Pods

```bash
kubectl get pods -n taskflow
```

**Expected**:
```
NAME                                   READY   STATUS    RESTARTS   AGE
backend-deployment-xxx                 2/2     Running   0          30m
frontend-deployment-xxx                1/1     Running   0          30m
notification-service-xxx               2/2     Running   0          30m
```

✅ **Pass Criteria**:
- Backend: `2/2` (app + Dapr sidecar)
- Frontend: `1/1`
- Notification: `2/2` (app + Dapr sidecar)
- All pods: `Running` status, 0 restarts

### 8. Verify Services

```bash
kubectl get svc -n taskflow
```

**Expected**:
```
NAME                        TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)
backend-service             ClusterIP      10.96.x.x       <none>            8000/TCP
frontend-service            LoadBalancer   10.96.x.x       129.151.146.217   80:xxxxx/TCP
notification-service        ClusterIP      10.96.x.x       <none>            8001/TCP
notification-service-dapr   ClusterIP      None            <none>            80/TCP,50001/TCP,50002/TCP,9090/TCP
taskflow-backend-dapr       ClusterIP      None            <none>            80/TCP,50001/TCP,50002/TCP,9090/TCP
```

✅ **Pass Criteria**:
- Frontend: `LoadBalancer` with `EXTERNAL-IP` assigned
- Backend: `ClusterIP` on port 8000
- Notification: `ClusterIP` on port 8001
- Dapr headless services present

## Functional Testing

### 1. Access Frontend

Open browser to: `http://<EXTERNAL-IP>`

**Expected**:
- ✅ Page loads within 3 seconds
- ✅ Login/signup page displayed
- ✅ No console errors (check browser DevTools)

### 2. User Authentication

**Test Case**: Sign up new user

1. Click "Sign Up"
2. Enter email and password
3. Submit form

**Expected**:
- ✅ Successful signup
- ✅ Redirect to dashboard
- ✅ No error messages

### 3. Create Task

**Test Case**: Create a simple task

```
Title: "Test task on OKE"
Description: "Verifying cloud deployment"
```

**Expected**:
- ✅ Task appears in task list
- ✅ Task saved to database
- ✅ Response time < 2 seconds (per SC-007)

### 4. Sort Functionality (Phase 5 Part A)

**Test Case**: Sort tasks by different criteria

1. Create 3 tasks with different priorities (low, medium, high)
2. Click sort dropdown
3. Select "Sort by Priority"

**Expected**:
- ✅ Dropdown appears with options: Due Date, Priority, Created, Title
- ✅ Tasks reorder immediately (high → medium → low)
- ✅ Sort preference persists on page refresh

### 5. Recurring Tasks (Phase 5 Part A)

**Test Case**: Create recurring task

1. Create task with:
   ```
   Title: "Weekly standup"
   Recurrence: Weekly
   Due Date: Tomorrow at 10:00 AM
   ```
2. Mark task as complete

**Expected**:
- ✅ Original task marked complete
- ✅ New task created with due_date = +7 days
- ✅ Toast notification: "Next occurrence created for [date]"
- ✅ New task creation time < 10 seconds (per SC-004)

### 6. Due Date and Priority (Phase 5 Part A)

**Test Case**: Create task with due date and priority

1. Create task with:
   ```
   Title: "Important deadline"
   Due Date: 2026-02-14 17:00
   Priority: High
   ```

**Expected**:
- ✅ Task displays due date with clock icon
- ✅ Task badge color: red (high priority)
- ✅ Due date stored in correct timezone

## Event-Driven Architecture Testing

### 1. Task Event Publishing

**Test Case**: Verify task.created event published to Kafka

1. Create a new task via frontend
2. Check backend logs:
   ```bash
   kubectl logs -n taskflow -l app=backend -c backend --tail=20
   ```

**Expected Log Output**:
```
INFO: Publishing event: task.created for task_id=123
INFO: Event published successfully to topic: task-events
```

✅ **Pass Criteria**:
- Event published within 100ms
- No error messages
- Event visible in backend logs

### 2. Reminder Event Flow

**Test Case**: Verify reminder event published for task with due_date

1. Create task with due_date = 1 hour from now
2. Check backend logs:
   ```bash
   kubectl logs -n taskflow -l app=backend -c backend --tail=20
   ```
3. Wait for reminder time (or set due_date to 1 minute for faster testing)
4. Check notification service logs:
   ```bash
   kubectl logs -n taskflow -l app=notification -c notification --tail=20
   ```

**Expected Backend Log**:
```
INFO: Publishing reminder event: task_id=123, remind_at=2026-02-07T11:00:00Z
INFO: Reminder event published to topic: reminders
```

**Expected Notification Log** (after reminder time):
```
INFO: Received reminder event: task_id=123, title="Test task", due_at=2026-02-07T12:00:00Z
INFO: Reminder logged: Task "Test task" due in 1 hour
```

✅ **Pass Criteria**:
- Reminder event published when task created
- Notification service receives event from Kafka
- 95% of reminders delivered within 60s (per SC-003)

### 3. Dapr Pub/Sub Integration

**Test Case**: Verify Dapr is publishing to Kafka

1. Create task
2. Check Dapr sidecar logs:
   ```bash
   kubectl logs -n taskflow -l app=backend -c daprd --tail=30
   ```

**Expected**:
```
INFO: Published message to topic 'task-events' via pubsub 'taskflow-pubsub'
INFO: Message acknowledged by broker
```

✅ **Pass Criteria**:
- Dapr logs show successful publish
- Dapr overhead < 50ms at p50 (per SC-009)

### 4. End-to-End Event Flow

**Test Case**: Complete event flow from frontend → backend → Kafka → notification

1. Open browser DevTools → Network tab
2. Create task with due_date
3. Monitor:
   - Frontend: POST /api/tasks request completes
   - Backend: Event published to Kafka
   - Notification: Event received from Kafka

**Expected Timeline**:
```
T+0ms:    Frontend sends POST /api/tasks
T+200ms:  Backend responds 201 Created
T+250ms:  Backend publishes task.created event
T+300ms:  Backend publishes reminder event
T+350ms:  Dapr confirms publish to Kafka
T+400ms:  Notification service receives event (at reminder time)
```

✅ **Pass Criteria**:
- Complete flow < 500ms (excluding reminder delivery)
- No errors in any component
- Events arrive in correct order

## Performance Testing

### 1. Task Creation Latency

**Test Case**: Measure p95 latency for task creation

1. Create 20 tasks rapidly via frontend
2. Record response times from browser DevTools

**Expected**:
- ✅ Average: < 1 second
- ✅ p95: < 2 seconds (per SC-007)
- ✅ No timeouts or 500 errors

### 2. Search Results Performance

**Test Case**: Search for tasks

1. Create 50 tasks
2. Use search: "test"
3. Measure time from input to results

**Expected**:
- ✅ Results appear < 500ms (per SC-002)
- ✅ Includes 300ms debounce + 200ms query

### 3. Kafka Throughput

**Test Case**: Verify Kafka can handle event load

1. Create 100 tasks rapidly (use script or load testing tool)
2. Check all events published successfully

**Expected**:
- ✅ All events published without errors
- ✅ Kafka throughput > 1000 events/sec (per SC-005)
- ✅ No backpressure or queue buildup

## Backward Compatibility Testing

### Test Phase 1-4 Features

These tests verify **SC-008**: 100% backward compatibility

#### Phase 1: Console App Features
- ✅ Task CRUD operations via API work
- ✅ Database schema unchanged (new columns have defaults)

#### Phase 2: Web App Features
- ✅ Login/signup works
- ✅ Task list displays correctly
- ✅ Filter tabs (All, Active, Completed) work
- ✅ Mark complete/delete works

#### Phase 3: AI Chatbot Features
- ✅ MCP server endpoints accessible (if deployed)
- ✅ Natural language task operations work

#### Phase 4: Kubernetes Features
- ✅ Helm chart deploys without errors
- ✅ Health probes pass
- ✅ Rolling updates work

**Pass Criteria**: 100% of Phase 1-4 tests pass on OKE

## Logs and Monitoring

### Check Logs

**Backend**:
```bash
kubectl logs -n taskflow -l app=backend -c backend -f
```

**Frontend**:
```bash
kubectl logs -n taskflow -l app=frontend -f
```

**Notification**:
```bash
kubectl logs -n taskflow -l app=notification -c notification -f
```

**Dapr Sidecar (Backend)**:
```bash
kubectl logs -n taskflow -l app=backend -c daprd -f
```

**Kafka**:
```bash
kubectl logs -n kafka taskflow-kafka-taskflow-kafka-pool-0 -f
```

### Check Resource Usage

```bash
kubectl top nodes
kubectl top pods -n taskflow
kubectl top pods -n kafka
```

**Expected (within Oracle Free Tier)**:
- Kafka: ~1.5GB RAM, ~1 CPU
- TaskFlow: ~800MB RAM, ~0.8 CPU
- Dapr: ~500MB RAM, ~0.5 CPU
- **Total**: < 3GB RAM, < 2.5 CPU

### Monitor Events

```bash
kubectl get events -n taskflow --sort-by='.lastTimestamp'
kubectl get events -n kafka --sort-by='.lastTimestamp'
```

## Test Checklist

Use this checklist to track testing progress:

### Infrastructure ✅
- [ ] 2 OKE nodes running (T079-T086)
- [ ] Kafka cluster Ready (T087-T091)
- [ ] Dapr system running (T092-T094)
- [ ] All pods Running (T095-T104)
- [ ] LoadBalancer has external IP (T102)

### Functional ✅
- [ ] Frontend accessible (T103)
- [ ] User auth works (T106)
- [ ] Task CRUD works (T106)
- [ ] Sort dropdown works (T011-T017, T112)
- [ ] Recurring tasks work (T018-T023, T111)

### Event-Driven ✅
- [ ] Task events published (T024-T030, T110)
- [ ] Reminder events published (T110)
- [ ] Notification service receives events (T054-T064, T110)
- [ ] Dapr pub/sub works (T046-T053)

### Performance ✅
- [ ] p95 latency < 2s (T113)
- [ ] Search < 500ms (existing)
- [ ] Reminders 95% within 60s (T110)
- [ ] Kafka > 1000 events/sec (T053)

### Backward Compatibility ✅
- [ ] Phase 1 tests pass (T105)
- [ ] Phase 2 tests pass (T106)
- [ ] Phase 3 tests pass (T107)
- [ ] Phase 4 tests pass (T108)
- [ ] 100% compatibility verified (T109)

## Success Criteria

**Phase 5 Part C is successful when**:

1. ✅ All infrastructure deployed on Oracle OKE free tier
2. ✅ All TaskFlow pods running with Dapr sidecars
3. ✅ Kafka cluster healthy with topics created
4. ✅ Frontend accessible via LoadBalancer IP
5. ✅ All functional tests pass
6. ✅ Event flow works end-to-end
7. ✅ Performance meets SC-001 to SC-010 targets
8. ✅ 100% backward compatibility with Phase 1-4 (SC-008)

## Next Steps

- [ ] Create demo video (T114) - 90 seconds max
- [ ] Update README.md with OKE deployment info (T115)
- [ ] Create production deployment guide (T116)
- [ ] Submit hackathon entry

## Troubleshooting

For deployment issues, see [ORACLE-CLOUD-DEPLOYMENT.md - Troubleshooting](./ORACLE-CLOUD-DEPLOYMENT.md#troubleshooting)

## Demo Script (90 seconds)

**0:00-0:15**: Show OKE cluster
```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

**0:15-0:30**: Show Kafka and Dapr
```bash
kubectl get kafka -n kafka
kubectl get pods -n dapr-system
```

**0:30-0:50**: Frontend demo
- Open `http://<EXTERNAL-IP>`
- Login
- Create task with due date and priority
- Use sort dropdown
- Create recurring task, mark complete

**0:50-1:10**: Show event flow
- Backend logs: event published
- Notification logs: reminder received

**1:10-1:30**: Show infrastructure
- All pods running
- LoadBalancer external IP
- Backward compatibility verified

**End**: Deployment URL + GitHub repo link
