"""Dapr event publisher for TaskFlow.

Publishes events to Kafka via Dapr HTTP API.
Gracefully handles cases when Dapr is not running (local development).
"""

import logging
import os
from typing import Any

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DaprPublisher:
    """Publisher for sending events to Kafka via Dapr pub/sub component.

    This client uses the Dapr HTTP API to publish events to Kafka topics.
    It's designed to work seamlessly in both Dapr-enabled and local environments.

    Environment Variables:
        DAPR_HTTP_PORT: Port for Dapr HTTP sidecar (default: 3500)
        PUBSUB_NAME: Name of Dapr pub/sub component (default: taskflow-pubsub)
        DAPR_ENABLED: Whether Dapr is available (default: false)

    Example:
        ```python
        publisher = DaprPublisher()
        event = TaskEvent(
            event_type="created",
            task_id=123,
            user_id="user_abc",
            task_data={"title": "Review PR"}
        )
        await publisher.publish("task-events", event)
        ```
    """

    def __init__(self) -> None:
        """Initialize Dapr publisher with configuration from environment."""
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.pubsub_name = os.getenv("PUBSUB_NAME", "taskflow-pubsub")
        self.base_url = f"http://localhost:{self.dapr_port}"
        self.enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"

        if self.enabled:
            logger.info(
                f"Dapr publisher initialized: {self.base_url}, pubsub={self.pubsub_name}"
            )
        else:
            logger.debug("Dapr publisher disabled (DAPR_ENABLED=false)")

    async def publish(self, topic: str, event: BaseModel) -> bool:
        """Publish an event to a Kafka topic via Dapr.

        Args:
            topic: Kafka topic name (e.g., "task-events", "reminders")
            event: Pydantic model instance to publish (TaskEvent or ReminderEvent)

        Returns:
            True if published successfully, False if skipped or failed

        Raises:
            No exceptions raised - failures are logged and method returns False
        """
        if not self.enabled:
            logger.debug(
                f"Dapr disabled, skipping publish to {topic}: {event.__class__.__name__}"
            )
            return False

        # Dapr pub/sub endpoint: POST /v1.0/publish/{pubsubname}/{topic}
        url = f"{self.base_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Dapr expects JSON payload - Pydantic model_dump() handles serialization
                response = await client.post(
                    url,
                    json=event.model_dump(mode="json"),
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code in (200, 204):
                    logger.info(
                        f"Published {event.__class__.__name__} to {topic}: "
                        f"event_type={getattr(event, 'event_type', 'N/A')}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to publish to {topic}: HTTP {response.status_code} - {response.text}"
                    )
                    return False

        except httpx.ConnectError as e:
            logger.warning(
                f"Cannot connect to Dapr at {self.base_url} - is Dapr sidecar running? Error: {e}"
            )
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout publishing to {topic} via Dapr: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing to {topic}: {e}", exc_info=True)
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: dict[str, Any],
    ) -> bool:
        """Convenience method to publish a TaskEvent.

        Args:
            event_type: Type of event (created, updated, completed, deleted)
            task_id: ID of the task
            user_id: ID of the user who owns the task
            task_data: Complete task data snapshot

        Returns:
            True if published successfully, False otherwise
        """
        from src.events.models import TaskEvent

        event = TaskEvent(
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            task_data=task_data,
        )
        return await self.publish("task-events", event)

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: str,
        title: str,
        due_at: Any,  # datetime
        remind_at: Any,  # datetime
    ) -> bool:
        """Convenience method to publish a ReminderEvent.

        Args:
            task_id: ID of the task
            user_id: ID of the user to remind
            title: Task title for the reminder
            due_at: When the task is due
            remind_at: When to send the reminder (typically 1 hour before due_at)

        Returns:
            True if published successfully, False otherwise
        """
        from src.events.models import ReminderEvent

        event = ReminderEvent(
            task_id=task_id,
            user_id=user_id,
            title=title,
            due_at=due_at,
            remind_at=remind_at,
        )
        return await self.publish("reminders", event)


# Global publisher instance (singleton pattern)
_publisher: DaprPublisher | None = None


def get_publisher() -> DaprPublisher:
    """Get the global DaprPublisher instance (singleton).

    Returns:
        Shared DaprPublisher instance
    """
    global _publisher
    if _publisher is None:
        _publisher = DaprPublisher()
    return _publisher
