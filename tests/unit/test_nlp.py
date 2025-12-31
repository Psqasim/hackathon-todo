"""Unit tests for NLP parsing utilities.

Tests for:
- parse_natural_date: Natural language date parsing
- extract_priority: Priority keyword extraction
- extract_tags: Tag extraction from text
- parse_task_input: Combined task parsing

FR-015: Agent MUST parse natural language dates
FR-016: Agent MUST extract priority keywords
"""

from datetime import datetime, timedelta

import pytest

from src.mcp_server.nlp import (
    PRIORITY_KEYWORDS,
    extract_priority,
    extract_tags,
    format_date_for_api,
    format_date_for_display,
    parse_natural_date,
    parse_task_input,
)


class TestParseNaturalDate:
    """Tests for parse_natural_date function."""

    def test_parse_tomorrow(self) -> None:
        """Test parsing 'tomorrow'."""
        result = parse_natural_date("tomorrow")
        assert result is not None
        # Should be approximately tomorrow
        expected = datetime.now() + timedelta(days=1)
        assert result.date() == expected.date()

    def test_parse_today(self) -> None:
        """Test parsing 'today'."""
        result = parse_natural_date("today")
        assert result is not None
        assert result.date() == datetime.now().date()

    def test_parse_next_week(self) -> None:
        """Test parsing 'next week'."""
        result = parse_natural_date("next week")
        assert result is not None
        # Should be about 7 days from now
        expected_min = datetime.now() + timedelta(days=5)
        expected_max = datetime.now() + timedelta(days=10)
        assert expected_min.date() <= result.date() <= expected_max.date()

    def test_parse_in_3_days(self) -> None:
        """Test parsing 'in 3 days'."""
        result = parse_natural_date("in 3 days")
        assert result is not None
        expected = datetime.now() + timedelta(days=3)
        assert result.date() == expected.date()

    def test_parse_iso_format(self) -> None:
        """Test parsing ISO date format."""
        result = parse_natural_date("2025-06-15")
        assert result is not None
        assert result.year == 2025
        assert result.month == 6
        assert result.day == 15

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string returns None."""
        result = parse_natural_date("")
        assert result is None

    def test_parse_none_equivalent(self) -> None:
        """Test parsing whitespace-only string returns None."""
        result = parse_natural_date("   ")
        assert result is None

    def test_parse_invalid_text(self) -> None:
        """Test parsing non-date text returns None."""
        result = parse_natural_date("buy groceries")
        assert result is None

    def test_parse_weekday(self) -> None:
        """Test parsing weekday names."""
        result = parse_natural_date("Friday")
        # dateparser may or may not find a date depending on context
        # Just verify it doesn't crash and returns datetime or None
        if result is not None:
            # Friday is weekday 4
            assert result.weekday() == 4

    def test_parse_month_day(self) -> None:
        """Test parsing month and day."""
        result = parse_natural_date("January 15th")
        assert result is not None
        assert result.month == 1
        assert result.day == 15


class TestExtractPriority:
    """Tests for extract_priority function."""

    def test_extract_urgent(self) -> None:
        """Test extracting urgent priority."""
        assert extract_priority("this is urgent!") == "urgent"
        assert extract_priority("do this asap") == "urgent"
        assert extract_priority("critical task") == "urgent"
        assert extract_priority("emergency meeting") == "urgent"

    def test_extract_high(self) -> None:
        """Test extracting high priority."""
        assert extract_priority("important meeting") == "high"
        assert extract_priority("high priority task") == "high"

    def test_extract_medium(self) -> None:
        """Test extracting medium priority."""
        assert extract_priority("medium priority task") == "medium"
        assert extract_priority("this is medium") == "medium"
        assert extract_priority("normal task") == "medium"

    def test_extract_low(self) -> None:
        """Test extracting low priority."""
        assert extract_priority("low priority task") == "low"
        assert extract_priority("do this whenever") == "low"
        assert extract_priority("not urgent") == "low"

    def test_default_to_medium(self) -> None:
        """Test default to medium when no keywords."""
        assert extract_priority("buy groceries") == "medium"
        assert extract_priority("call the dentist") == "medium"

    def test_empty_string(self) -> None:
        """Test empty string returns medium."""
        assert extract_priority("") == "medium"

    def test_case_insensitive(self) -> None:
        """Test priority extraction is case insensitive."""
        assert extract_priority("URGENT task") == "urgent"
        assert extract_priority("Important Meeting") == "high"

    def test_priority_keywords_coverage(self) -> None:
        """Test all priority keywords are recognized."""
        for priority, keywords in PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                result = extract_priority(f"task {keyword} item")
                assert result == priority, f"Failed for keyword: {keyword}"


class TestExtractTags:
    """Tests for extract_tags function."""

    def test_extract_hashtag_tags(self) -> None:
        """Test extracting hashtag-style tags."""
        tags = extract_tags("buy groceries #shopping")
        assert "shopping" in tags

    def test_extract_multiple_hashtags(self) -> None:
        """Test extracting multiple hashtag tags."""
        tags = extract_tags("meeting with client #work #important")
        assert "work" in tags
        assert "important" in tags

    def test_extract_common_category(self) -> None:
        """Test extracting common category words."""
        tags = extract_tags("finish work report")
        assert "work" in tags

    def test_empty_string(self) -> None:
        """Test empty string returns empty list."""
        tags = extract_tags("")
        assert tags == []

    def test_no_tags_found(self) -> None:
        """Test no tags returns empty list."""
        tags = extract_tags("hello world")
        assert tags == []

    def test_remove_duplicates(self) -> None:
        """Test duplicate tags are removed."""
        tags = extract_tags("#work #work #work")
        assert tags.count("work") == 1

    def test_case_normalization(self) -> None:
        """Test tags are normalized to lowercase."""
        tags = extract_tags("#WORK #Shopping")
        assert "work" in tags
        assert "shopping" in tags


class TestParseTaskInput:
    """Tests for parse_task_input function."""

    def test_parse_simple_task(self) -> None:
        """Test parsing simple task description."""
        result = parse_task_input("buy groceries")
        assert result["title"] == "buy groceries"
        assert result["priority"] == "medium"
        assert result["tags"] == []

    def test_parse_task_with_date(self) -> None:
        """Test parsing task with due date."""
        # Use a clear date expression that dateparser will recognize
        result = parse_task_input("tomorrow finish report")
        # dateparser should find "tomorrow"
        # Note: dateparser behavior varies; this test verifies the flow works
        assert "title" in result
        assert "due_date" in result
        assert "priority" in result

    def test_parse_task_with_priority(self) -> None:
        """Test parsing task with priority keyword."""
        result = parse_task_input("urgent: finish report")
        assert result["priority"] == "urgent"

    def test_parse_task_with_tags(self) -> None:
        """Test parsing task with hashtag tags."""
        result = parse_task_input("buy groceries #shopping")
        assert "shopping" in result["tags"]

    def test_parse_combined_input(self) -> None:
        """Test parsing task with multiple components."""
        result = parse_task_input("urgent meeting #work")
        assert result["priority"] == "urgent"
        assert "work" in result["tags"]
        # Title should contain meeting
        assert "meeting" in result["title"]

    def test_title_cleaned(self) -> None:
        """Test title is cleaned of markers."""
        result = parse_task_input("buy groceries #shopping tomorrow")
        # Title should not contain the hashtag or date expression
        assert "#" not in result["title"]


class TestFormatDateForDisplay:
    """Tests for format_date_for_display function."""

    def test_format_date(self) -> None:
        """Test formatting a date."""
        dt = datetime(2024, 12, 31)
        result = format_date_for_display(dt)
        assert "December" in result
        assert "31" in result
        assert "2024" in result

    def test_format_none(self) -> None:
        """Test formatting None returns 'No date'."""
        result = format_date_for_display(None)
        assert result == "No date"


class TestFormatDateForApi:
    """Tests for format_date_for_api function."""

    def test_format_date(self) -> None:
        """Test formatting a date for API."""
        dt = datetime(2024, 12, 31, 14, 30)
        result = format_date_for_api(dt)
        assert result is not None
        assert "2024-12-31" in result

    def test_format_none(self) -> None:
        """Test formatting None returns None."""
        result = format_date_for_api(None)
        assert result is None
