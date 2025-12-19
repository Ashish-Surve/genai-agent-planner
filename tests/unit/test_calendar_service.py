"""Test calendar service."""

from datetime import date, datetime

import pytest

from adhd_planner.models.enums import BlockType
from adhd_planner.services.calendar_service import CalendarService
from adhd_planner.utils.errors import UserFacingError


@pytest.fixture
def calendar_service(test_db_session):
    """Create calendar service with test database."""
    return CalendarService(test_db_session)


def test_create_time_block(calendar_service):
    """Test creating a time block."""
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 10, 0)

    block = calendar_service.create_time_block(
        start_time=start,
        end_time=end,
        block_type=BlockType.TASK.value,
    )

    assert block.id is not None
    assert block.start_time == start
    assert block.end_time == end
    assert block.duration_minutes == 60
    assert block.block_type == BlockType.TASK.value


def test_create_overlapping_block_fails(calendar_service):
    """Test that overlapping blocks are rejected."""
    start1 = datetime(2025, 1, 1, 9, 0)
    end1 = datetime(2025, 1, 1, 10, 0)

    # Create first block
    calendar_service.create_time_block(start_time=start1, end_time=end1)

    # Try to create overlapping block
    start2 = datetime(2025, 1, 1, 9, 30)
    end2 = datetime(2025, 1, 1, 10, 30)

    with pytest.raises(UserFacingError, match="conflicts"):
        calendar_service.create_time_block(start_time=start2, end_time=end2)


def test_find_conflicts(calendar_service):
    """Test conflict detection."""
    # Create a block
    start1 = datetime(2025, 1, 1, 9, 0)
    end1 = datetime(2025, 1, 1, 10, 0)
    calendar_service.create_time_block(start_time=start1, end_time=end1)

    # Check for conflicts
    start2 = datetime(2025, 1, 1, 9, 30)
    end2 = datetime(2025, 1, 1, 10, 30)

    conflicts = calendar_service.find_conflicts(start2, end2)
    assert len(conflicts) == 1

    # No conflict for adjacent block
    start3 = datetime(2025, 1, 1, 10, 0)
    end3 = datetime(2025, 1, 1, 11, 0)

    conflicts = calendar_service.find_conflicts(start3, end3)
    assert len(conflicts) == 0


def test_is_available(calendar_service):
    """Test availability checking."""
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 10, 0)

    # Should be available initially
    assert calendar_service.is_available(start, end) is True

    # Create block
    calendar_service.create_time_block(start_time=start, end_time=end)

    # Should no longer be available
    assert calendar_service.is_available(start, end) is False


def test_get_blocks_for_date(calendar_service):
    """Test getting blocks for a specific date."""
    date1 = date(2025, 1, 1)
    date2 = date(2025, 1, 2)

    # Create blocks on different dates
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
    )
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 2, 9, 0),
        end_time=datetime(2025, 1, 2, 10, 0),
    )

    # Check blocks for each date
    blocks_date1 = calendar_service.get_blocks_for_date(date1)
    assert len(blocks_date1) == 1

    blocks_date2 = calendar_service.get_blocks_for_date(date2)
    assert len(blocks_date2) == 1


def test_find_available_slots(calendar_service):
    """Test finding available slots."""
    target_date = date(2025, 1, 1)

    # Create some blocks
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
    )
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 14, 0),
        end_time=datetime(2025, 1, 1, 15, 0),
    )

    # Find available slots
    slots = calendar_service.find_available_slots(
        target_date,
        duration_minutes=60,
        work_start="09:00",
        work_end="17:00",
    )

    # Should have gaps: 10:00-14:00 (240m) and 15:00-17:00 (120m)
    assert len(slots) >= 2
    assert any(s.duration_minutes >= 240 for s in slots)


def test_find_next_available_slot(calendar_service):
    """Test finding next available slot."""
    # Fill today's schedule
    today = date.today()
    calendar_service.create_time_block(
        start_time=datetime.combine(today, datetime.min.time().replace(hour=9)),
        end_time=datetime.combine(today, datetime.min.time().replace(hour=17)),
    )

    # Should find slot tomorrow
    slot = calendar_service.find_next_available_slot(
        duration_minutes=60,
        days_ahead=7,
    )

    assert slot is not None
    assert slot.duration_minutes >= 60
    assert slot.start.date() > today


def test_update_time_block(calendar_service):
    """Test updating a time block."""
    block = calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
    )

    # Update notes
    updated = calendar_service.update_time_block(
        block.id,
        notes="Updated notes",
    )

    assert updated.notes == "Updated notes"


def test_delete_time_block(calendar_service):
    """Test deleting a time block."""
    block = calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
    )

    calendar_service.delete_time_block(block.id)

    # Block should no longer exist
    assert calendar_service.get_time_block(block.id) is None


def test_get_schedule_summary(calendar_service):
    """Test getting schedule summary."""
    target_date = date(2025, 1, 1)

    # Create various blocks
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
        block_type=BlockType.TASK.value,
    )
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 10, 0),
        end_time=datetime(2025, 1, 1, 10, 15),
        block_type=BlockType.BREAK.value,
    )

    summary = calendar_service.get_schedule_summary(target_date)

    assert summary["total_blocks"] == 2
    assert summary["task_blocks"] == 1
    assert summary["break_blocks"] == 1
    assert summary["task_minutes"] == 60
    assert summary["break_minutes"] == 15
    assert summary["total_minutes_scheduled"] == 75


def test_flexible_blocks_allow_overlap(calendar_service):
    """Test that flexible blocks can overlap."""
    # Create regular block
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0),
        is_flexible=False,
    )

    # Create flexible block that overlaps - should succeed
    block = calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 30),
        end_time=datetime(2025, 1, 1, 10, 30),
        is_flexible=True,
    )

    assert block is not None
