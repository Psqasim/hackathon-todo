"""
TaskFlow Notification Service

FastAPI microservice that subscribes to reminder events from Kafka via Dapr.
Logs notifications for tasks that are due soon.

Endpoints:
- GET /health - Health check
- GET /dapr/subscribe - Dapr subscription configuration
- POST /events/reminders - Handles reminder events from Dapr
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
import logging
import os

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("notification-service")

# FastAPI app
app = FastAPI(
    title="TaskFlow Notification Service",
    description="Microservice for handling task reminders via Dapr/Kafka",
    version="1.0.0"
)


# Models
class ReminderEvent(BaseModel):
    """Reminder event data model"""
    task_id: int
    user_id: str
    title: str
    due_at: str
    remind_at: Optional[str] = None


class CloudEvent(BaseModel):
    """Dapr Cloud Event envelope"""
    id: str
    source: str
    specversion: str = "1.0"
    type: str
    datacontenttype: str = "application/json"
    data: Any
    traceid: Optional[str] = None
    pubsubname: Optional[str] = None
    topic: Optional[str] = None


# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# Dapr subscription endpoint
@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription configuration endpoint.

    Tells Dapr which topics this service subscribes to and
    which routes to use for event delivery.

    Returns:
        List of subscription configurations
    """
    subscriptions = [
        {
            "pubsubname": "taskflow-pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]

    logger.info(f"📋 Dapr subscription configuration requested: {subscriptions}")
    return subscriptions


# Reminder event handler
@app.post("/events/reminders")
async def handle_reminder(request: Request):
    """
    Handle reminder events from Dapr.

    Receives CloudEvent-formatted reminder events, extracts the reminder data,
    and logs the notification (in production, this would send email/SMS/push).

    Args:
        request: FastAPI request containing CloudEvent

    Returns:
        Success status

    Raises:
        HTTPException: If event processing fails
    """
    try:
        # Parse CloudEvent
        event_data = await request.json()
        logger.info(f"📬 REMINDER EVENT RECEIVED: {event_data}")

        # Extract data from CloudEvent
        # Dapr wraps events in CloudEvent format
        if "data" in event_data:
            reminder_data = event_data["data"]
        else:
            # Fallback if not wrapped
            reminder_data = event_data

        # Parse reminder event
        task_id = reminder_data.get("task_id")
        title = reminder_data.get("title", "Untitled Task")
        due_at = reminder_data.get("due_at")
        user_id = reminder_data.get("user_id")
        remind_at = reminder_data.get("remind_at")

        # Log notification (in production, send actual notification)
        logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║              🔔 TASK REMINDER NOTIFICATION               ║
╠══════════════════════════════════════════════════════════╣
║ Task ID:    {task_id:<45} ║
║ Title:      {title:<45} ║
║ User:       {user_id:<45} ║
║ Due At:     {due_at:<45} ║
║ Remind At:  {remind_at or 'N/A':<45} ║
╚══════════════════════════════════════════════════════════╝
        """)

        # TODO: In production, integrate with notification providers:
        # - SendGrid/AWS SES for email
        # - Twilio for SMS
        # - Firebase/OneSignal for push notifications
        # - Slack/Discord webhooks for team notifications

        return {
            "status": "SUCCESS",
            "message": f"Reminder processed for task {task_id}",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing reminder event: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process reminder event: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log service startup"""
    logger.info("🚀 TaskFlow Notification Service starting up...")
    logger.info(f"📌 Log level: {LOG_LEVEL}")
    logger.info(f"📌 Service version: 1.0.0")
    logger.info("✅ Notification Service ready to receive events")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log service shutdown"""
    logger.info("🛑 TaskFlow Notification Service shutting down...")


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level=LOG_LEVEL.lower()
    )
