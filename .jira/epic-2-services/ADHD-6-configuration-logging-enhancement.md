# ADHD-6: Configuration & Logging Enhancement

## Story Information

- **Epic**: Core Services
- **Story Points**: 2
- **Estimated Time**: 2 hours
- **Prerequisites**: ADHD-1 (Project Setup), ADHD-2 (Database Schema)
- **Status**: 📋 Not Started

## Description

Enhance the basic configuration and logging infrastructure with utility functions for validation, time/date manipulation, contextual logging, and error formatting. These utilities will be used across all services and agents.

## Goals

1. Create input validation helpers for common patterns
2. Implement time and date utility functions
3. Add contextual logging with automatic context propagation
4. Create error formatting and user-friendly error messages
5. Add validation for business rules

## Acceptance Criteria

- [ ] Validation helpers created and tested
- [ ] Time utilities handle all timezone scenarios
- [ ] Contextual logging works with nested calls
- [ ] Error messages are user-friendly and informative
- [ ] All utilities have comprehensive docstrings
- [ ] Unit tests pass for all utilities

## Files to Create

```
src/utils/validation.py          # Input validation helpers
src/utils/time_utils.py           # Time/date utilities
src/utils/errors.py                # Error formatting
tests/unit/test_validation.py     # Validation tests
tests/unit/test_time_utils.py     # Time utils tests
```

## Implementation Steps

### Step 1: Validation Helpers (30 min)

**File**: `src/utils/validation.py`

```python
"""Input validation utilities."""

import re
from datetime import datetime, time as dt_time
from typing import Any, Optional, List
from src.utils.logger import get_logger

logger = get_logger("validation")


class ValidationError(Exception):
    """Custom validation error with user-friendly messages."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


def validate_not_empty(value: str, field_name: str) -> str:
    """
    Validate that a string is not empty.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Returns:
        The validated string

    Raises:
        ValidationError: If string is empty or only whitespace
    """
    if not value or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty", field=field_name)
    return value.strip()


def validate_duration(minutes: int, field_name: str = "duration") -> int:
    """
    Validate that a duration is reasonable.

    Args:
        minutes: Duration in minutes
        field_name: Name of the field for error messages

    Returns:
        The validated duration

    Raises:
        ValidationError: If duration is not positive or unreasonably long
    """
    if minutes <= 0:
        raise ValidationError(
            f"{field_name} must be positive (got {minutes})",
            field=field_name
        )

    if minutes > 1440:  # 24 hours
        raise ValidationError(
            f"{field_name} cannot exceed 24 hours (got {minutes} minutes)",
            field=field_name
        )

    return minutes


def validate_time_range(
    start: datetime,
    end: datetime,
    allow_same: bool = False
) -> tuple[datetime, datetime]:
    """
    Validate that start time is before end time.

    Args:
        start: Start datetime
        end: End datetime
        allow_same: Whether to allow start == end

    Returns:
        Tuple of (start, end)

    Raises:
        ValidationError: If time range is invalid
    """
    if start > end:
        raise ValidationError(
            f"Start time ({start}) must be before end time ({end})"
        )

    if not allow_same and start == end:
        raise ValidationError("Start and end time cannot be the same")

    return start, end


def validate_enum_value(value: str, allowed_values: List[str], field_name: str) -> str:
    """
    Validate that a value is in the allowed set.

    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of the field for error messages

    Returns:
        The validated value (uppercase)

    Raises:
        ValidationError: If value is not in allowed set
    """
    value_upper = value.upper()
    allowed_upper = [v.upper() for v in allowed_values]

    if value_upper not in allowed_upper:
        raise ValidationError(
            f"{field_name} must be one of {allowed_values} (got '{value}')",
            field=field_name
        )

    return value_upper


def validate_time_string(time_str: str, field_name: str = "time") -> str:
    """
    Validate time string format (HH:MM).

    Args:
        time_str: Time string to validate
        field_name: Name of the field for error messages

    Returns:
        The validated time string

    Raises:
        ValidationError: If time format is invalid
    """
    pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"

    if not re.match(pattern, time_str):
        raise ValidationError(
            f"{field_name} must be in HH:MM format (got '{time_str}')",
            field=field_name
        )

    return time_str


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email to validate

    Returns:
        The validated email

    Raises:
        ValidationError: If email format is invalid
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}", field="email")

    return email.lower()
```

### Step 2: Time Utilities (40 min)

**File**: `src/utils/time_utils.py`

```python
"""Time and date utility functions."""

from datetime import datetime, date, time as dt_time, timedelta
from typing import Optional, Tuple, List
import pytz
from dateutil import parser
from src.utils.logger import get_logger

logger = get_logger("time_utils")


def parse_datetime(date_string: str, timezone: Optional[str] = None) -> datetime:
    """
    Parse a datetime string flexibly.

    Args:
        date_string: String to parse
        timezone: Optional timezone name (e.g., 'America/Los_Angeles')

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If string cannot be parsed
    """
    try:
        dt = parser.parse(date_string)

        if timezone:
            tz = pytz.timezone(timezone)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            else:
                dt = dt.astimezone(tz)

        return dt
    except (ValueError, parser.ParserError) as e:
        logger.error(f"Failed to parse datetime '{date_string}': {e}")
        raise ValueError(f"Cannot parse datetime: {date_string}")


def time_string_to_datetime(
    time_str: str,
    base_date: Optional[date] = None
) -> datetime:
    """
    Convert time string (HH:MM) to datetime for today or specified date.

    Args:
        time_str: Time in HH:MM format
        base_date: Base date to use (defaults to today)

    Returns:
        Datetime combining date and time
    """
    hours, minutes = map(int, time_str.split(':'))
    base = base_date or date.today()
    return datetime.combine(base, dt_time(hours, minutes))


def datetime_to_time_string(dt: datetime) -> str:
    """
    Convert datetime to time string (HH:MM).

    Args:
        dt: Datetime to convert

    Returns:
        Time string in HH:MM format
    """
    return dt.strftime("%H:%M")


def get_time_blocks_for_day(
    day: date,
    start_time: str = "00:00",
    end_time: str = "23:59",
    block_duration: int = 30
) -> List[Tuple[datetime, datetime]]:
    """
    Generate time blocks for a given day.

    Args:
        day: Date to generate blocks for
        start_time: Start time (HH:MM)
        end_time: End time (HH:MM)
        block_duration: Duration of each block in minutes

    Returns:
        List of (start, end) datetime tuples
    """
    start_dt = time_string_to_datetime(start_time, day)
    end_dt = time_string_to_datetime(end_time, day)

    blocks = []
    current = start_dt

    while current < end_dt:
        block_end = min(current + timedelta(minutes=block_duration), end_dt)
        blocks.append((current, block_end))
        current = block_end

    return blocks


def calculate_duration_minutes(start: datetime, end: datetime) -> int:
    """
    Calculate duration between two datetimes in minutes.

    Args:
        start: Start datetime
        end: End datetime

    Returns:
        Duration in minutes (rounded up)
    """
    delta = end - start
    minutes = delta.total_seconds() / 60
    return int(minutes) if minutes == int(minutes) else int(minutes) + 1


def is_overlapping(
    start1: datetime,
    end1: datetime,
    start2: datetime,
    end2: datetime
) -> bool:
    """
    Check if two time ranges overlap.

    Args:
        start1: Start of first range
        end1: End of first range
        start2: Start of second range
        end2: End of second range

    Returns:
        True if ranges overlap
    """
    return start1 < end2 and start2 < end1


def get_working_hours(
    day: date,
    start_time: str = "09:00",
    end_time: str = "17:00"
) -> Tuple[datetime, datetime]:
    """
    Get working hours for a given day.

    Args:
        day: Date to get working hours for
        start_time: Work start time (HH:MM)
        end_time: Work end time (HH:MM)

    Returns:
        Tuple of (work_start, work_end) datetimes
    """
    work_start = time_string_to_datetime(start_time, day)
    work_end = time_string_to_datetime(end_time, day)
    return work_start, work_end


def format_duration(minutes: int) -> str:
    """
    Format duration in human-readable format.

    Args:
        minutes: Duration in minutes

    Returns:
        Formatted string (e.g., "2h 30m", "45m")
    """
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"

    return f"{hours}h {remaining_minutes}m"


def get_next_occurrence(
    base_time: datetime,
    target_time_str: str
) -> datetime:
    """
    Get next occurrence of a specific time.

    Args:
        base_time: Reference datetime
        target_time_str: Target time (HH:MM)

    Returns:
        Next datetime matching the target time
    """
    target = time_string_to_datetime(target_time_str, base_time.date())

    if target <= base_time:
        # Move to next day
        target += timedelta(days=1)

    return target
```

### Step 3: Error Formatting (20 min)

**File**: `src/utils/errors.py`

```python
"""Error formatting and user-friendly error messages."""

from typing import Optional, Dict, Any
from src.utils.logger import get_logger

logger = get_logger("errors")


class UserFacingError(Exception):
    """Error with user-friendly message."""

    def __init__(
        self,
        user_message: str,
        technical_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        self.details = details or {}
        super().__init__(self.technical_message)


def format_error_for_user(error: Exception) -> str:
    """
    Format an error message for user display.

    Args:
        error: Exception to format

    Returns:
        User-friendly error message
    """
    if isinstance(error, UserFacingError):
        return error.user_message

    # Map common errors to user-friendly messages
    error_type = type(error).__name__
    error_str = str(error)

    if "database" in error_str.lower():
        return "Sorry, there was a problem saving your data. Please try again."

    if "connection" in error_str.lower() or "network" in error_str.lower():
        return "Connection issue detected. Please check your network and try again."

    if "permission" in error_str.lower():
        return "Permission denied. Please check your system permissions."

    # Generic fallback
    logger.error(f"Unhandled error: {error_type}: {error_str}")
    return "Something went wrong. Please try again or contact support if the problem persists."


def log_error_with_context(
    error: Exception,
    context: Dict[str, Any],
    operation: str
) -> None:
    """
    Log an error with context information.

    Args:
        error: Exception that occurred
        context: Context dictionary
        operation: Operation being performed
    """
    logger.error(
        f"Error in {operation}: {type(error).__name__}: {str(error)}\n"
        f"Context: {context}",
        exc_info=True
    )
```

### Step 4: Update Logger with Context Support (20 min)

**File**: `src/utils/logger.py` (add to existing file)

Add these functions to the existing logger.py:

```python
# Add to existing logger.py

from contextvars import ContextVar
from typing import Dict, Any

# Context storage
_log_context: ContextVar[Dict[str, Any]] = ContextVar('log_context', default={})


def set_log_context(**kwargs: Any) -> None:
    """
    Set context values that will be included in all log messages.

    Args:
        **kwargs: Context key-value pairs
    """
    context = _log_context.get().copy()
    context.update(kwargs)
    _log_context.set(context)


def clear_log_context() -> None:
    """Clear all log context."""
    _log_context.set({})


def get_log_context() -> Dict[str, Any]:
    """Get current log context."""
    return _log_context.get().copy()


class ContextFormatter(logging.Formatter):
    """Formatter that includes context in log messages."""

    def format(self, record: logging.LogRecord) -> str:
        context = get_log_context()
        if context:
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            record.msg = f"[{context_str}] {record.msg}"
        return super().format(record)
```

### Step 5: Unit Tests (30 min)

**File**: `tests/unit/test_validation.py`

```python
"""Test validation utilities."""

import pytest
from datetime import datetime
from src.utils.validation import (
    validate_not_empty,
    validate_duration,
    validate_time_range,
    validate_enum_value,
    validate_time_string,
    ValidationError
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
        validate_time_string("9:00", "time")  # Missing leading zero
```

**File**: `tests/unit/test_time_utils.py`

```python
"""Test time utilities."""

import pytest
from datetime import datetime, date, timedelta
from src.utils.time_utils import (
    time_string_to_datetime,
    datetime_to_time_string,
    calculate_duration_minutes,
    is_overlapping,
    format_duration,
    get_next_occurrence
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
```

## Testing Checklist

```bash
# 1. Run validation tests
uv run pytest tests/unit/test_validation.py -v

# 2. Run time utils tests
uv run pytest tests/unit/test_time_utils.py -v

# 3. Test imports
uv run python -c "
from src.utils.validation import validate_duration
from src.utils.time_utils import format_duration
from src.utils.errors import format_error_for_user
print('All imports successful')
"

# 4. Test validation in Python
uv run python -c "
from src.utils.validation import validate_duration, ValidationError
try:
    validate_duration(-10, 'test')
except ValidationError as e:
    print(f'Caught expected error: {e.message}')
"

# 5. Test time formatting
uv run python -c "
from src.utils.time_utils import format_duration
print(format_duration(90))  # Should print: 1h 30m
"

# 6. Run all unit tests
uv run pytest tests/unit/ -v

# 7. Check code quality
uv run ruff check src/utils/
uv run black --check src/utils/
```

## Expected Output

All tests should pass:
```
tests/unit/test_validation.py::test_validate_not_empty_success PASSED
tests/unit/test_validation.py::test_validate_duration_success PASSED
tests/unit/test_time_utils.py::test_format_duration PASSED
...
===================== XX passed in X.XXs =====================
```

## Success Criteria

- ✅ All validation helpers working correctly
- ✅ Time utilities handle edge cases
- ✅ Error formatting provides user-friendly messages
- ✅ Contextual logging implemented
- ✅ All unit tests pass
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: Timezone-related test failures
**Solution**: Use UTC consistently in tests, or mock timezone functions

### Issue: Time string parsing fails
**Solution**: Ensure strict HH:MM format with leading zeros

### Issue: Validation errors not caught
**Solution**: Always catch ValidationError specifically, not generic Exception

## Next Story

Once this story is complete, move to:
**[ADHD-7: LLM Service & Provider Factory](ADHD-7-llm-service-provider-factory.md)**

## Notes

- These utilities are used throughout the codebase - thorough testing is critical
- Validation should be strict but provide clear error messages
- Time utilities must handle all edge cases (midnight, DST, etc.)
- Error formatting helps with ADHD-friendly UX - clear, actionable messages