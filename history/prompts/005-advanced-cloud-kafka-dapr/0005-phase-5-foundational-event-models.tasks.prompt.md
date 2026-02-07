---
id: 0005
title: Phase 5 Foundational Event Models
stage: tasks
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-advanced-cloud-kafka-dapr
branch: 005-advanced-cloud-kafka-dapr
user: ps_qasim
command: /sp.implement
labels: ["phase-5", "foundational", "event-models", "dapr-publisher", "pydantic", "async", "kafka"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/events/models.py
  - src/events/publisher.py
  - src/events/__init__.py
  - tests/test_events.py
  - specs/005-advanced-cloud-kafka-dapr/tasks.md
tests:
  - tests/test_events.py (16 tests, all passed)
---

## Prompt

Execute Phase 2 Foundational tasks (T007-T010) only.

## Tasks to Execute:

- T007: Create event models in src/events/models.py
  - TaskEvent: event_type (created/updated/completed/deleted), task_id, user_id, task_data, timestamp
  - ReminderEvent: task_id, user_id, title, due_at, remind_at, timestamp

- T008: Create Dapr publisher client in src/events/publisher.py
  - DaprPublisher class with publish_event() method
  - Uses httpx to POST to Dapr sidecar: http://localhost:3500/v1.0/publish/{pubsub_name}/{topic}
  - Configurable DAPR_HTTP_PORT (default 3500)
  - Configurable PUBSUB_NAME (default "taskflow-pubsub")
  - Graceful fallback when Dapr not available (log warning, don't crash)

- T009: Export models and publisher in src/events/__init__.py

- T010: Add unit tests for event models in tests/test_events.py

## Instructions:

1. Create the event models with Pydantic
2. Create the Dapr publisher with async httpx
3. Handle case when Dapr is not running (for local development without Dapr)
4. Add basic unit tests
5. Commit with message: "feat: Phase 5 foundational - event models and Dapr publisher (T007-T010)"

## Code Patterns:

Use these patterns from my skills:

### Event Model Pattern:
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict

class TaskEvent(BaseModel):
    event_type: str  # created, updated, completed, deleted
    task_id: int
    user_id: str
    task_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### Dapr Publisher Pattern:
```python
import httpx
import os
import logging

class DaprPublisher:
    def __init__(self):
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.pubsub_name = os.getenv("PUBSUB_NAME", "taskflow-pubsub")
        self.base_url = f"http://localhost:{self.dapr_port}"
        self.enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"

    async def publish(self, topic: str, event: BaseModel) -> bool:
        if not self.enabled:
            logging.debug(f"Dapr disabled, skipping publish to {topic}")
            return False
        # ... publish logic
```

Execute only these 4 foundational tasks now. Do not proceed to Phase 3 yet.

## Response snapshot

Executed Phase 2 Foundational tasks (T007-T010) successfully:

**Event Models Created** (src/events/models.py):
- TaskEvent: Captures task lifecycle events (created, updated, completed, deleted) with task_id, user_id, task_data, timestamp
- ReminderEvent: Schedules reminders with task_id, user_id, title, due_at, remind_at, timestamp
- Both use Pydantic v2 ConfigDict (no deprecation warnings)
- Timezone-aware datetime using datetime.now(UTC)

**Dapr Publisher Created** (src/events/publisher.py):
- DaprPublisher class with async httpx client
- POST to Dapr: http://localhost:3500/v1.0/publish/{pubsub}/{topic}
- Environment configuration: DAPR_HTTP_PORT, PUBSUB_NAME, DAPR_ENABLED
- Graceful error handling: ConnectError, TimeoutException, generic exceptions
- Convenience methods: publish_task_event(), publish_reminder_event()
- Singleton pattern: get_publisher() for shared instance
- Logs warnings when Dapr unavailable, doesn't crash app

**Exports Added** (src/events/__init__.py):
- TaskEvent, ReminderEvent, DaprPublisher, get_publisher

**Unit Tests Created** (tests/test_events.py):
- 16 test cases covering all functionality
- TaskEvent: creation, serialization, event types, custom timestamps
- ReminderEvent: creation, serialization, 1-hour-before logic
- DaprPublisher: init (enabled/disabled), publish success/failure, connection errors, timeouts, convenience methods, singleton
- All tests pass with zero warnings

**Git Commit**: 087993a - "feat: Phase 5 foundational - event models and Dapr publisher (T007-T010)"

Ready to proceed to Phase 3: Part A - Missing Features (T011-T030) when requested.

## Outcome

- ✅ Impact: Event-driven architecture foundation complete - ready for Part A feature integration
- 🧪 Tests: 16 tests created and passing with 0 warnings (100% coverage on new modules)
- 📁 Files: 5 files created/modified (2 models, 1 publisher, 1 __init__, 1 test suite, 1 tasks.md update)
- 🔁 Next prompts: Execute Phase 3 Part A (T011-T030) - sort functionality, recurring tasks, event publishing prep
- 🧠 Reflection: Clean implementation using Pydantic v2 best practices. Graceful degradation when Dapr unavailable enables local dev without full stack. Publisher singleton simplifies integration.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - 16/16 tests passed, no warnings
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
