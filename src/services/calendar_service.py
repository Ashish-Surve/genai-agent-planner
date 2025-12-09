"""Calendar service for time block management."""

from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.time_block import TimeBlock
from src.models.enums import BlockType
from src.repositories.time_block_repository import TimeBlockRepository
from src.adhd_planner.utils.time_utils import (
    calculate_duration_minutes,
    get_working_hours,
)
from src.adhd_planner.utils.validation import validate_time_range
from src.adhd_planner.utils.logger import get_logger
from src.adhd_planner.utils.errors import UserFacingError

logger = get_logger("calendar_service")


class ScheduleSlot:
    """Represents an available schedule slot."""

    def __init__(self, start: datetime, end: datetime, energy_level: Optional[str] = None):
        self.start = start
        self.end = end
        self.duration_minutes = calculate_duration_minutes(start, end)
        self.energy_level = energy_level

    def __repr__(self) -> str:
        return f"Slot({self.start.strftime('%H:%M')} - {self.end.strftime('%H:%M')}, {self.duration_minutes}m, {self.energy_level})"


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
        block_type: str = BlockType.TASK.value,
        task_id: Optional[str] = None,
        is_flexible: bool = False,
        energy_level_required: Optional[str] = None,
        notes: Optional[str] = None,
        sync_enabled: bool = True,
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
                    technical_message=f"Found {len(conflicts)} conflicts",
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
            "sync_enabled": sync_enabled,
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
        **updates,
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
        block_type: Optional[str] = None,
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
        end_date: date,
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
        exclude_block_id: Optional[str] = None,
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
        end_time: datetime,
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
        energy_level: Optional[str] = None,
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
        work_start_dt, work_end_dt = get_working_hours(target_date, work_start, work_end)

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

        self.logger.debug(f"Found {len(available_slots)} available slots for {target_date}")
        return available_slots

    def find_next_available_slot(
        self,
        duration_minutes: int,
        start_from: Optional[datetime] = None,
        days_ahead: int = 7,
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
        if start_from is None:
            start_from = datetime.now()
        current_date = start_from.date()

        for day_offset in range(days_ahead):
            check_date = current_date + timedelta(days=day_offset)

            slots = self.find_available_slots(check_date, duration_minutes)

            # Filter slots that start after start_from
            if day_offset == 0:
                slots = [s for s in slots if s.start >= start_from]

            if slots:
                return slots[0]  # Return first available

        return None

    def get_schedule_summary(
        self,
        target_date: date,
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
            "break_minutes": sum(b.duration_minutes for b in break_blocks),
        }

    def _block_title(self, block: TimeBlock) -> str:
        """Get display title for a block."""
        if hasattr(block, 'task') and block.task:
            return f"{block.task.title} ({block.block_type})"
        return f"{block.block_type} block"
