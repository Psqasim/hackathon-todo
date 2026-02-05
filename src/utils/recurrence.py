"""Recurrence utilities for TaskFlow.

Provides functions for calculating next due dates for recurring tasks.
Phase 5: Added for US2 - Recurring Tasks
"""

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta


def calculate_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Calculate the next due date for a recurring task.

    Args:
        current_due: Current due date of the task
        pattern: Recurrence pattern (daily, weekly, monthly, yearly)

    Returns:
        Next due date based on the recurrence pattern

    Raises:
        ValueError: If pattern is not supported

    Examples:
        >>> from datetime import datetime
        >>> current = datetime(2024, 1, 15, 10, 0)
        >>> calculate_next_due_date(current, "daily")
        datetime.datetime(2024, 1, 16, 10, 0)
        >>> calculate_next_due_date(current, "weekly")
        datetime.datetime(2024, 1, 22, 10, 0)
        >>> calculate_next_due_date(current, "monthly")
        datetime.datetime(2024, 2, 15, 10, 0)
    """
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(days=7)
    elif pattern == "monthly":
        # Use relativedelta to handle month-end dates correctly
        # e.g., Jan 31 -> Feb 28 (or 29 in leap years)
        return current_due + relativedelta(months=1)
    elif pattern == "yearly":
        return current_due + relativedelta(years=1)
    else:
        raise ValueError(f"Unsupported recurrence pattern: {pattern}")
