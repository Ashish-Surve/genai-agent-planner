"""Input validation utilities."""

import re
from datetime import datetime

from adhd_planner.utils.logger import get_logger

logger = get_logger("validation")


class ValidationError(Exception):
    """Custom validation error with user-friendly messages."""

    def __init__(self, message: str, field: str | None = None):
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
            field=field_name,
        )

    if minutes > 1440:  # 24 hours
        raise ValidationError(
            f"{field_name} cannot exceed 24 hours (got {minutes} minutes)",
            field=field_name,
        )

    return minutes


def validate_time_range(
    start: datetime, end: datetime, allow_same: bool = False
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


def validate_enum_value(
    value: str, allowed_values: list[str], field_name: str
) -> str:
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
            field=field_name,
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
    pattern = r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$"

    if not re.match(pattern, time_str):
        raise ValidationError(
            f"{field_name} must be in HH:MM format (got '{time_str}')",
            field=field_name,
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
