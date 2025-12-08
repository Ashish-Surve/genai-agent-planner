"""Test time utilities."""

import pytest
from datetime import datetime, date, timedelta

from adhd_planner.utils.time_utils import (
    time_string_to_datetime,
    datetime_to_time_string,
    calculate_duration_minutes,
    is_overlapping,
    format_duration,
    get_next_occurrence,
)


def test_time_string_to_datetime():
    """Test time string conversion."""
    result = time_string_to_datetime("09:30", date(2025, 1, 1))
    assert result == datetime(2025, 1, 1, 9, 30)


def test_datetime_to_time_string():
    """Test datetime to time string."""
    dt = datetime(2025, 1, 1, 9, 30)
    assert datetime_to_time_string(dt) == "09:30"


def test_calculate_duration_minutes():
    """Test duration calculation."""
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 11, 30)

    assert calculate_duration_minutes(start, end) == 150


def test_is_overlapping():
    """Test overlap detection."""
    start1 = datetime(2025, 1, 1, 9, 0)
    end1 = datetime(2025, 1, 1, 10, 0)
    start2 = datetime(2025, 1, 1, 9, 30)
    end2 = datetime(2025, 1, 1, 10, 30)

    assert is_overlapping(start1, end1, start2, end2) is True

    # No overlap
    start3 = datetime(2025, 1, 1, 11, 0)
    end3 = datetime(2025, 1, 1, 12, 0)

    assert is_overlapping(start1, end1, start3, end3) is False


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(45) == "45m"
    assert format_duration(60) == "1h"
    assert format_duration(90) == "1h 30m"
    assert format_duration(120) == "2h"


def test_get_next_occurrence():
    """Test next occurrence calculation."""
    base = datetime(2025, 1, 1, 10, 0)

    # Target is later today
    next_time = get_next_occurrence(base, "15:00")
    assert next_time.date() == date(2025, 1, 1)
    assert next_time.hour == 15

    # Target is earlier - should be tomorrow
    next_time = get_next_occurrence(base, "09:00")
    assert next_time.date() == date(2025, 1, 2)
    assert next_time.hour == 9
