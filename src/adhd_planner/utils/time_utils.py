"""Time and date utility functions."""

from datetime import date, datetime, timedelta
from datetime import time as dt_time

import pytz
from dateutil import parser

from adhd_planner.utils.logger import get_logger

logger = get_logger("time_utils")


def parse_datetime(date_string: str, timezone: str | None = None) -> datetime:
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
        raise ValueError(f"Cannot parse datetime: {date_string}") from e


def time_string_to_datetime(
    time_str: str, base_date: date | None = None
) -> datetime:
    """
    Convert time string (HH:MM) to datetime for today or specified date.

    Args:
        time_str: Time in HH:MM format
        base_date: Base date to use (defaults to today)

    Returns:
        Datetime combining date and time
    """
    hours, minutes = map(int, time_str.split(":"))
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
    block_duration: int = 30,
) -> list[tuple[datetime, datetime]]:
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
    start1: datetime, end1: datetime, start2: datetime, end2: datetime
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
    day: date, start_time: str = "09:00", end_time: str = "17:00"
) -> tuple[datetime, datetime]:
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


def get_next_occurrence(base_time: datetime, target_time_str: str) -> datetime:
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
