"""
Natural language processing utilities.

This module provides date and priority parsing from natural language:
- parse_natural_date: Parse dates like "tomorrow", "next week", "in 3 days"
- extract_priority: Extract priority from keywords like "urgent", "asap"

FR-015: Agent MUST parse natural language dates (tomorrow, next week, in 3 days, etc.)
FR-016: Agent MUST extract priority keywords (urgent, important, low priority, etc.)
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import dateparser
import structlog

logger = structlog.get_logger()

# Priority keywords mapping - ordered by specificity (most specific first)
# Note: Check order matters - longer phrases checked before shorter ones
PRIORITY_KEYWORDS: dict[str, list[str]] = {
    "urgent": ["urgent", "asap", "critical", "emergency", "immediately", "right now"],
    "high": ["important", "high priority", "crucial"],
    "medium": ["medium priority", "medium", "normal", "regular", "standard"],
    "low": ["low priority", "low", "whenever", "eventually", "not urgent", "later"],
}

# Flattened keyword list sorted by length (longest first) for matching
_SORTED_KEYWORDS: list[tuple[str, str]] = []
for priority, keywords in PRIORITY_KEYWORDS.items():
    for keyword in keywords:
        _SORTED_KEYWORDS.append((keyword, priority))
_SORTED_KEYWORDS.sort(key=lambda x: len(x[0]), reverse=True)

# Valid priority values
PriorityLevel = Literal["low", "medium", "high", "urgent"]


def parse_natural_date(
    text: str,
    base_date: datetime | None = None,
    prefer_future: bool = True,
) -> datetime | None:
    """Parse natural language date expressions.

    Handles expressions like:
    - "tomorrow"
    - "next week"
    - "in 3 days"
    - "next Friday"
    - "January 15th"
    - "2024-12-31" (ISO format)

    Args:
        text: The text containing a date expression
        base_date: Base date for relative dates (defaults to now)
        prefer_future: If True, prefer future dates for ambiguous expressions

    Returns:
        Parsed datetime or None if no date found

    Examples:
        >>> parse_natural_date("tomorrow")
        datetime(2024, 12, 31, ...)  # Tomorrow's date

        >>> parse_natural_date("next week")
        datetime(2025, 1, 6, ...)  # 7 days from now

        >>> parse_natural_date("in 3 days")
        datetime(2025, 1, 2, ...)  # 3 days from now
    """
    if not text or not text.strip():
        return None

    # Configure dateparser settings
    settings = {
        "PREFER_DATES_FROM": "future" if prefer_future else "past",
        "PREFER_DAY_OF_MONTH": "first",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }

    if base_date:
        settings["RELATIVE_BASE"] = base_date

    try:
        parsed = dateparser.parse(text, settings=settings)
        if parsed:
            logger.debug(
                "date_parsed",
                input_text=text,
                parsed_date=parsed.isoformat(),
            )
        return parsed
    except Exception as e:
        logger.warning("date_parse_failed", input_text=text, error=str(e))
        return None


def extract_priority(text: str) -> PriorityLevel:
    """Extract priority level from natural language text.

    Searches for priority keywords in the text and returns
    the corresponding priority level. Longer phrases are
    checked first to avoid partial matches.

    Args:
        text: Text that may contain priority keywords

    Returns:
        Priority level (urgent, high, medium, low)
        Defaults to "medium" if no keywords found

    Examples:
        >>> extract_priority("this is urgent!")
        "urgent"

        >>> extract_priority("add this task asap")
        "urgent"

        >>> extract_priority("low priority task")
        "low"

        >>> extract_priority("buy groceries")
        "medium"  # default
    """
    if not text:
        return "medium"

    text_lower = text.lower()

    # Check keywords in order of length (longest first)
    # This ensures "low priority" matches before "priority" alone
    for keyword, priority in _SORTED_KEYWORDS:
        if keyword in text_lower:
            logger.debug(
                "priority_extracted",
                input_text=text[:50],
                keyword=keyword,
                priority=priority,
            )
            return priority  # type: ignore

    # Default to medium if no keywords found
    return "medium"


def extract_tags(text: str) -> list[str]:
    """Extract tags from natural language text.

    Looks for common tagging patterns:
    - #hashtag style tags
    - "tag: value" or "tags: a, b, c" format
    - Common category words (work, personal, shopping, etc.)

    Args:
        text: Text that may contain tags

    Returns:
        List of extracted tag strings

    Examples:
        >>> extract_tags("buy groceries #shopping")
        ["shopping"]

        >>> extract_tags("meeting with client #work #important")
        ["work", "important"]
    """
    if not text:
        return []

    tags = []

    # Extract hashtag-style tags
    import re

    hashtag_pattern = r"#(\w+)"
    hashtags = re.findall(hashtag_pattern, text.lower())
    tags.extend(hashtags)

    # Common category words (only if no hashtags found)
    if not tags:
        common_tags = ["work", "personal", "shopping", "health", "finance", "family", "home"]
        text_lower = text.lower()
        for tag in common_tags:
            if tag in text_lower:
                tags.append(tag)
                break  # Only add one common tag

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    if unique_tags:
        logger.debug("tags_extracted", input_text=text[:50], tags=unique_tags)

    return unique_tags


def format_date_for_display(dt: datetime | None) -> str:
    """Format a datetime for user display.

    Creates a human-readable date string.

    Args:
        dt: Datetime to format

    Returns:
        Formatted date string or "No date" if None

    Examples:
        >>> format_date_for_display(datetime(2024, 12, 31))
        "December 31, 2024"
    """
    if not dt:
        return "No date"

    return dt.strftime("%B %d, %Y")


def format_date_for_api(dt: datetime | None) -> str | None:
    """Format a datetime for API requests.

    Creates an ISO format date string for API calls.

    Args:
        dt: Datetime to format

    Returns:
        ISO format date string or None if no date

    Examples:
        >>> format_date_for_api(datetime(2024, 12, 31, 14, 30))
        "2024-12-31T14:30:00"
    """
    if not dt:
        return None

    return dt.isoformat()


def parse_task_input(text: str) -> dict:
    """Parse a natural language task description.

    Extracts task components from natural language:
    - Title (cleaned of date/priority/tag markers)
    - Due date (if mentioned)
    - Priority (from keywords)
    - Tags (from hashtags or common words)

    Args:
        text: Natural language task description

    Returns:
        Dictionary with extracted components:
        {
            "title": str,
            "due_date": str | None,  # ISO format
            "priority": str,
            "tags": list[str],
        }

    Examples:
        >>> parse_task_input("buy groceries tomorrow #shopping")
        {
            "title": "buy groceries",
            "due_date": "2024-12-31T00:00:00",
            "priority": "medium",
            "tags": ["shopping"],
        }
    """
    import re

    # Extract priority first
    priority = extract_priority(text)

    # Extract tags
    tags = extract_tags(text)

    # Try to parse a date from the text
    due_date = parse_natural_date(text)

    # Clean the title by removing date expressions, priority keywords, and hashtags
    title = text

    # Remove hashtags
    title = re.sub(r"#\w+", "", title)

    # Remove common date expressions (simplified)
    date_patterns = [
        r"\btomorrow\b",
        r"\btoday\b",
        r"\bnext\s+\w+\b",
        r"\bin\s+\d+\s+days?\b",
        r"\bby\s+\w+\b",
    ]
    for pattern in date_patterns:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # Remove priority keywords
    for keywords in PRIORITY_KEYWORDS.values():
        for keyword in keywords:
            title = re.sub(rf"\b{re.escape(keyword)}\b", "", title, flags=re.IGNORECASE)

    # Clean up extra whitespace
    title = " ".join(title.split()).strip()

    return {
        "title": title,
        "due_date": format_date_for_api(due_date),
        "priority": priority,
        "tags": tags,
    }


# Export public functions
__all__ = [
    "parse_natural_date",
    "extract_priority",
    "extract_tags",
    "format_date_for_display",
    "format_date_for_api",
    "parse_task_input",
    "PriorityLevel",
    "PRIORITY_KEYWORDS",
]
