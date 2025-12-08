# ADHD-9: Calendar Service

## Story Information

- **Epic**: Core Services
- **Story Points**: 3
- **Estimated Time**: 3 hours
- **Prerequisites**: ADHD-4 (Base Repository), ADHD-5 (TimeBlock Repository), ADHD-6 (Time Utils)
- **Status**: 📋 Not Started

## Description

Implement the Calendar Service that manages time blocks, checks availability, detects conflicts, and provides scheduling helpers. This service is critical for the scheduling agent and handles all time-based operations for the planner.

## Goals

1. Implement time block CRUD operations
2. Check availability for given time ranges
3. Detect scheduling conflicts
4. Generate optimal schedule slots
5. Handle working hours and breaks
6. Support energy-level based scheduling
7. Provide schedule visualization helpers

## Acceptance Criteria

- [ ] Time block CRUD operations work correctly
- [ ] Availability checking handles all edge cases
- [ ] Conflict detection is accurate
- [ ] Schedule generation respects constraints
- [ ] Working hours are enforced
- [ ] Energy levels are considered
- [ ] All operations logged
- [ ] Unit tests pass

## Files to Create

```
src/services/calendar_service.py        # Main calendar service
tests/unit/test_calendar_service.py     # Service tests
```

## Implementation Steps

### Step 1: Calendar Service Core (60 min)

**File**: `src/services/calendar_service.py`

```python
"""Calendar service for time block management."""

from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from src.models.time_block import TimeBlock, BlockType
from src.repositories.time_block_repository import TimeBlockRepository
from src.utils.time_utils import (
    calculate_duration_minutes,
    is_overlapping,
    get_working_hours,
    time_string_to_datetime
)
from src.utils.validation import validate_time_range, ValidationError
from src.utils.logger import get_logger
from src.utils.errors import UserFacingError

logger = get_logger("calendar_service")


class ScheduleSlot:
    """Represents an available schedule slot."""

    def __init__(self, start: datetime, end: datetime, energy_level: Optional[str] = None):
        self.start = start
        self.end = end
        self.duration_minutes = calculate_duration_minutes(start, end)
        self.energy_level = energy_level

    def __repr__(self) -> str:
        return f"Slot({self.start} - {self.end}, {self.duration_minutes}m, {self.energy_level})"


class CalendarService:
    """Service for calendar and time block management."""

    def __init__(self, session: Session):
        """
        Initialize calendar service.

        Args:
            session: Database session
        """
        self.session = session
        self.repository = TimeBlockRepository(session)
        self.logger = logger

    def create_time_block(
        self,
        start_time: datetime,
        end_time: datetime,
        block_type: str = "TASK",
        task_id: Optional[str] = None,
        is_flexible: bool = False,
        energy_level_required: Optional[str] = None,
        notes: Optional[str] = None,
        sync_enabled: bool = True
    ) -> TimeBlock:
        """
        Create a new time block.

        Args:
            start_time: Block start time
            end_time: Block end time
            block_type: Type (TASK, BREAK, BUFFER, EVENT, FREE)
            task_id: Optional linked task ID
            is_flexible: Whether block can be moved
            energy_level_required: Required energy level
            notes: Optional notes
            sync_enabled: Whether to sync with calendar

        Returns:
            Created time block

        Raises:
            ValidationError: If times are invalid
            UserFacingError: If conflict exists
        """
        # Validate times
        start_time, end_time = validate_time_range(start_time, end_time)

        # Calculate duration
        duration = calculate_duration_minutes(start_time, end_time)

        # Check for conflicts (unless it's a flexible block)
        if not is_flexible:
            conflicts = self.find_conflicts(start_time, end_time)
            if conflicts:
                conflict_titles = [self._block_title(c) for c in conflicts[:3]]
                raise UserFacingError(
                    f"Time slot conflicts with: {', '.join(conflict_titles)}",
                    technical_message=f"Found {len(conflicts)} conflicts"
                )

        # Create block
        block_data = {
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": duration,
            "block_type": block_type,
            "task_id": task_id,
            "is_flexible": is_flexible,
            "energy_level_required": energy_level_required,
            "notes": notes,
            "sync_enabled": sync_enabled
        }

        block = self.repository.create(block_data)

        self.logger.info(
            f"Created time block: {block.id} "
            f"({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})"
        )
        return block

    def update_time_block(
        self,
        block_id: str,
        **updates
    ) -> TimeBlock:
        """
        Update a time block.

        Args:
            block_id: Block ID
            **updates: Fields to update

        Returns:
            Updated time block

        Raises:
            UserFacingError: If block not found or update invalid
        """
        block = self.repository.get_by_id(block_id)
        if not block:
            raise UserFacingError("Time block not found")

        # If updating times, validate and check conflicts
        if "start_time" in updates or "end_time" in updates:
            start = updates.get("start_time", block.start_time)
            end = updates.get("end_time", block.end_time)

            start, end = validate_time_range(start, end)

            # Check conflicts (excluding this block)
            conflicts = self.find_conflicts(start, end, exclude_block_id=block_id)
            if conflicts:
                raise UserFacingError("Updated time conflicts with existing blocks")

            # Update duration
            updates["duration_minutes"] = calculate_duration_minutes(start, end)

        updated = self.repository.update(block_id, updates)
        self.logger.info(f"Updated time block: {block_id}")
        return updated

    def delete_time_block(self, block_id: str) -> None:
        """
        Delete a time block.

        Args:
            block_id: Block ID
        """
        block = self.repository.get_by_id(block_id)
        if not block:
            raise UserFacingError("Time block not found")

        self.repository.delete(block_id)
        self.logger.info(f"Deleted time block: {block_id}")

    def get_time_block(self, block_id: str) -> Optional[TimeBlock]:
        """Get time block by ID."""
        return self.repository.get_by_id(block_id)

    def get_blocks_for_date(
        self,
        target_date: date,
        block_type: Optional[str] = None
    ) -> List[TimeBlock]:
        """
        Get all time blocks for a specific date.

        Args:
            target_date: Date to query
            block_type: Optional filter by block type

        Returns:
            List of time blocks
        """
        blocks = self.repository.find_by_date(target_date)

        if block_type:
            blocks = [b for b in blocks if b.block_type == block_type]

        return blocks

    def get_blocks_for_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[TimeBlock]:
        """
        Get all time blocks in a date range.

        Args:
            start_date: Range start
            end_date: Range end (inclusive)

        Returns:
            List of time blocks
        """
        return self.repository.find_by_date_range(start_date, end_date)

    def find_conflicts(
        self,
        start_time: datetime,
        end_time: datetime,
        exclude_block_id: Optional[str] = None
    ) -> List[TimeBlock]:
        """
        Find time blocks that conflict with the given time range.

        Args:
            start_time: Range start
            end_time: Range end
            exclude_block_id: Optional block ID to exclude from check

        Returns:
            List of conflicting time blocks
        """
        return self.repository.find_conflicts(start_time, end_time, exclude_block_id)

    def is_available(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Check if a time slot is available (no conflicts).

        Args:
            start_time: Slot start
            end_time: Slot end

        Returns:
            True if available
        """
        conflicts = self.find_conflicts(start_time, end_time)
        return len(conflicts) == 0

    def find_available_slots(
        self,
        target_date: date,
        duration_minutes: int,
        work_start: str = "09:00",
        work_end: str = "17:00",
        min_slot_duration: Optional[int] = None,
        energy_level: Optional[str] = None
    ) -> List[ScheduleSlot]:
        """
        Find available time slots for a given date and duration.

        Args:
            target_date: Date to search
            duration_minutes: Required duration
            work_start: Work start time (HH:MM)
            work_end: Work end time (HH:MM)
            min_slot_duration: Minimum slot duration (defaults to duration_minutes)
            energy_level: Optional energy level for slot

        Returns:
            List of available schedule slots
        """
        min_slot_duration = min_slot_duration or duration_minutes

        # Get working hours
        work_start_dt, work_end_dt = get_working_hours(
            target_date,
            work_start,
            work_end
        )

        # Get existing blocks
        existing_blocks = self.get_blocks_for_date(target_date)

        # Sort blocks by start time
        existing_blocks.sort(key=lambda b: b.start_time)

        # Find gaps between blocks
        available_slots = []
        current_time = work_start_dt

        for block in existing_blocks:
            # Check gap before this block
            if block.start_time > current_time:
                gap_duration = calculate_duration_minutes(current_time, block.start_time)

                if gap_duration >= min_slot_duration:
                    available_slots.append(
                        ScheduleSlot(current_time, block.start_time, energy_level)
                    )

            # Move current time to after this block
            if block.end_time > current_time:
                current_time = block.end_time

        # Check gap after last block
        if current_time < work_end_dt:
            gap_duration = calculate_duration_minutes(current_time, work_end_dt)

            if gap_duration >= min_slot_duration:
                available_slots.append(
                    ScheduleSlot(current_time, work_end_dt, energy_level)
                )

        self.logger.debug(
            f"Found {len(available_slots)} available slots for {target_date}"
        )
        return available_slots

    def find_next_available_slot(
        self,
        duration_minutes: int,
        start_from: Optional[datetime] = None,
        days_ahead: int = 7
    ) -> Optional[ScheduleSlot]:
        """
        Find the next available slot that can fit the duration.

        Args:
            duration_minutes: Required duration
            start_from: Start searching from this time (defaults to now)
            days_ahead: How many days ahead to search

        Returns:
            Next available slot or None
        """
        start_from = start_from or datetime.utcnow()
        current_date = start_from.date()

        for day_offset in range(days_ahead):
            check_date = current_date + timedelta(days=day_offset)

            slots = self.find_available_slots(
                check_date,
                duration_minutes
            )

            # Filter slots that start after start_from
            if day_offset == 0:
                slots = [s for s in slots if s.start >= start_from]

            if slots:
                return slots[0]  # Return first available

        return None

    def get_schedule_summary(
        self,
        target_date: date
    ) -> dict:
        """
        Get a summary of the schedule for a date.

        Args:
            target_date: Date to summarize

        Returns:
            Dictionary with schedule statistics
        """
        blocks = self.get_blocks_for_date(target_date)

        total_scheduled = sum(b.duration_minutes for b in blocks)
        task_blocks = [b for b in blocks if b.block_type == BlockType.TASK.value]
        break_blocks = [b for b in blocks if b.block_type == BlockType.BREAK.value]

        return {
            "date": target_date,
            "total_blocks": len(blocks),
            "total_minutes_scheduled": total_scheduled,
            "task_blocks": len(task_blocks),
            "break_blocks": len(break_blocks),
            "task_minutes": sum(b.duration_minutes for b in task_blocks),
            "break_minutes": sum(b.duration_minutes for b in break_blocks)
        }

    def _block_title(self, block: TimeBlock) -> str:
        """Get display title for a block."""
        if block.task:
            return f"{block.task.title} ({block.block_type})"
        return f"{block.block_type} block"
```

### Step 2: Unit Tests (60 min)

**File**: `tests/unit/test_calendar_service.py`

```python
"""Test calendar service."""

import pytest
from datetime import datetime, date, timedelta
from src.services.calendar_service import CalendarService, ScheduleSlot
from src.models.time_block import BlockType
from src.utils.errors import UserFacingError


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
        block_type=BlockType.TASK.value
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
        end_time=datetime(2025, 1, 1, 10, 0)
    )
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 2, 9, 0),
        end_time=datetime(2025, 1, 2, 10, 0)
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
        end_time=datetime(2025, 1, 1, 10, 0)
    )
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 14, 0),
        end_time=datetime(2025, 1, 1, 15, 0)
    )

    # Find available slots
    slots = calendar_service.find_available_slots(
        target_date,
        duration_minutes=60,
        work_start="09:00",
        work_end="17:00"
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
        end_time=datetime.combine(today, datetime.min.time().replace(hour=17))
    )

    # Should find slot tomorrow
    slot = calendar_service.find_next_available_slot(
        duration_minutes=60,
        days_ahead=7
    )

    assert slot is not None
    assert slot.duration_minutes >= 60
    assert slot.start.date() > today


def test_update_time_block(calendar_service):
    """Test updating a time block."""
    block = calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0)
    )

    # Update notes
    updated = calendar_service.update_time_block(
        block.id,
        notes="Updated notes"
    )

    assert updated.notes == "Updated notes"


def test_delete_time_block(calendar_service):
    """Test deleting a time block."""
    block = calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0)
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
        block_type=BlockType.TASK.value
    )
    calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 10, 0),
        end_time=datetime(2025, 1, 1, 10, 15),
        block_type=BlockType.BREAK.value
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
        is_flexible=False
    )

    # Create flexible block that overlaps - should succeed
    block = calendar_service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 30),
        end_time=datetime(2025, 1, 1, 10, 30),
        is_flexible=True
    )

    assert block is not None
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_calendar_service.py -v

# 2. Test time block creation
uv run python -c "
from datetime import datetime
from src.database.connection import get_db
from src.services.calendar_service import CalendarService

db = get_db()
with db.get_session() as session:
    service = CalendarService(session)
    block = service.create_time_block(
        start_time=datetime(2025, 1, 1, 9, 0),
        end_time=datetime(2025, 1, 1, 10, 0)
    )
    print(f'Created block: {block.id} ({block.duration_minutes}m)')
"

# 3. Test availability checking
uv run python -c "
from datetime import datetime, date
from src.database.connection import get_db
from src.services.calendar_service import CalendarService

db = get_db()
with db.get_session() as session:
    service = CalendarService(session)

    # Find available slots
    slots = service.find_available_slots(
        date.today(),
        duration_minutes=60
    )
    print(f'Found {len(slots)} available slots')
    for slot in slots:
        print(f'  {slot}')
"

# 4. Run all tests
uv run pytest tests/unit/ -v

# 5. Code quality
uv run ruff check src/services/calendar_service.py
uv run black --check src/services/
```

## Success Criteria

- ✅ Time block CRUD works correctly
- ✅ Conflict detection is accurate
- ✅ Availability checking handles edge cases
- ✅ Slot finding algorithm works
- ✅ Schedule summaries are correct
- ✅ All unit tests pass
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: Off-by-one errors in availability checking
**Solution**: Use strict inequality for time comparisons, test edge cases

### Issue: Time blocks spanning midnight not handled
**Solution**: Ensure queries handle date boundaries correctly

### Issue: Performance with many time blocks
**Solution**: Add database indexes on start_time and end_time

## Next Story

Once this story is complete, move to:
**[ADHD-10: Time Estimation Service](ADHD-10-time-estimation-service.md)**

## Notes

- Calendar service is foundation for all scheduling features
- Accurate conflict detection is critical - test thoroughly
- Available slot algorithm should be efficient for daily use
- Consider energy levels when suggesting slots
- Time block flexibility enables smart rescheduling