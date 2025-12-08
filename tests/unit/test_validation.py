"""Test validation utilities."""

import pytest
from datetime import datetime

from adhd_planner.utils.validation import (
    validate_not_empty,
    validate_duration,
    validate_time_range,
    validate_enum_value,
    validate_time_string,
    ValidationError,
)


def test_validate_not_empty_success():
    """Test successful validation."""
    assert validate_not_empty("test", "field") == "test"
    assert validate_not_empty("  test  ", "field") == "test"


def test_validate_not_empty_failure():
    """Test validation failure."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_not_empty("", "field")

    with pytest.raises(ValidationError):
        validate_not_empty("   ", "field")


def test_validate_duration_success():
    """Test duration validation."""
    assert validate_duration(30, "duration") == 30
    assert validate_duration(120, "duration") == 120


def test_validate_duration_failures():
    """Test duration validation failures."""
    with pytest.raises(ValidationError, match="must be positive"):
        validate_duration(0, "duration")

    with pytest.raises(ValidationError, match="cannot exceed"):
        validate_duration(2000, "duration")


def test_validate_time_range_success():
    """Test time range validation."""
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 17, 0)

    validated_start, validated_end = validate_time_range(start, end)
    assert validated_start == start
    assert validated_end == end


def test_validate_time_range_failures():
    """Test time range validation failures."""
    start = datetime(2025, 1, 1, 17, 0)
    end = datetime(2025, 1, 1, 9, 0)

    with pytest.raises(ValidationError, match="must be before"):
        validate_time_range(start, end)


def test_validate_enum_value():
    """Test enum validation."""
    allowed = ["LOW", "MEDIUM", "HIGH"]

    assert validate_enum_value("low", allowed, "priority") == "LOW"
    assert validate_enum_value("HIGH", allowed, "priority") == "HIGH"

    with pytest.raises(ValidationError, match="must be one of"):
        validate_enum_value("INVALID", allowed, "priority")


def test_validate_time_string():
    """Test time string validation."""
    assert validate_time_string("09:00", "time") == "09:00"
    assert validate_time_string("23:59", "time") == "23:59"

    with pytest.raises(ValidationError, match="HH:MM format"):
        validate_time_string("25:00", "time")

    with pytest.raises(ValidationError):
        validate_time_string("9:00", "time")
