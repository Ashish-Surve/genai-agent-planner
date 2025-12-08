"""TimeBlock repository with specialized queries."""

from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from src.repositories.base_repository import BaseRepository
from src.database.schema import TimeBlockModel
from src.adhd_planner.utils.logger import get_logger

logger = get_logger("time_block_repository")


class TimeBlockRepository(BaseRepository[TimeBlockModel]):
    """Repository for time block specific queries."""

    def __init__(self, session: Session):
        """Initialize time block repository."""
        super().__init__(TimeBlockModel, session)

    def find_by_date(self, target_date: date) -> List[TimeBlockModel]:
        """Find all time blocks for a specific date."""
        try:
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())

            blocks = self.session.query(self.model).filter(
                self.model.start_time >= start_of_day,
                self.model.start_time <= end_of_day
            ).order_by(self.model.start_time.asc()).all()

            self.logger.debug(f"Found {len(blocks)} time blocks for {target_date}")
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding blocks by date: {e}", exc_info=True)
            raise

    def find_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[TimeBlockModel]:
        """Find all time blocks within a date range."""
        try:
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            blocks = self.session.query(self.model).filter(
                self.model.start_time >= start_dt,
                self.model.start_time <= end_dt
            ).order_by(self.model.start_time.asc()).all()

            self.logger.debug(
                f"Found {len(blocks)} time blocks between {start_date} and {end_date}"
            )
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding blocks by date range: {e}", exc_info=True)
            raise

    def find_by_task(self, task_id: str) -> List[TimeBlockModel]:
        """Find all time blocks for a specific task."""
        try:
            blocks = self.session.query(self.model).filter(
                self.model.task_id == task_id
            ).order_by(self.model.start_time.asc()).all()

            self.logger.debug(f"Found {len(blocks)} time blocks for task {task_id}")
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding blocks by task: {e}", exc_info=True)
            raise

    def find_conflicts(
        self,
        start_time: datetime,
        end_time: datetime,
        exclude_block_id: Optional[str] = None
    ) -> List[TimeBlockModel]:
        """Find time blocks that conflict with the given time range."""
        try:
            # Blocks conflict if: start1 < end2 AND start2 < end1
            query = self.session.query(self.model).filter(
                self.model.start_time < end_time,
                self.model.end_time > start_time
            )

            if exclude_block_id:
                query = query.filter(self.model.id != exclude_block_id)

            conflicts = query.all()

            self.logger.debug(
                f"Found {len(conflicts)} conflicts for {start_time} - {end_time}"
            )
            return conflicts

        except Exception as e:
            self.logger.error(f"Error finding conflicts: {e}", exc_info=True)
            raise

    def find_by_block_type(
        self,
        block_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TimeBlockModel]:
        """Find time blocks by type, optionally within a date range."""
        try:
            query = self.session.query(self.model).filter(
                self.model.block_type == block_type
            )

            if start_date:
                start_dt = datetime.combine(start_date, datetime.min.time())
                query = query.filter(self.model.start_time >= start_dt)

            if end_date:
                end_dt = datetime.combine(end_date, datetime.max.time())
                query = query.filter(self.model.start_time <= end_dt)

            blocks = query.order_by(self.model.start_time.asc()).all()

            self.logger.debug(f"Found {len(blocks)} blocks of type {block_type}")
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding blocks by type: {e}", exc_info=True)
            raise

    def find_flexible_blocks(self) -> List[TimeBlockModel]:
        """Find all flexible time blocks."""
        try:
            blocks = self.session.query(self.model).filter(
                self.model.is_flexible == True
            ).order_by(self.model.start_time.asc()).all()

            self.logger.debug(f"Found {len(blocks)} flexible blocks")
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding flexible blocks: {e}", exc_info=True)
            raise

    def find_current_and_upcoming(
        self,
        hours_ahead: int = 4
    ) -> List[TimeBlockModel]:
        """Find current and upcoming time blocks."""
        try:
            now = datetime.utcnow()
            future = now + timedelta(hours=hours_ahead)

            blocks = self.session.query(self.model).filter(
                self.model.end_time >= now,
                self.model.start_time <= future
            ).order_by(self.model.start_time.asc()).all()

            self.logger.debug(
                f"Found {len(blocks)} current and upcoming blocks "
                f"(next {hours_ahead} hours)"
            )
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding upcoming blocks: {e}", exc_info=True)
            raise

    def find_pending_sync(self) -> List[TimeBlockModel]:
        """Find time blocks with pending sync."""
        try:
            blocks = self.session.query(self.model).filter(
                self.model.sync_enabled == True,
                self.model.apple_calendar_event_id.is_(None)
            ).all()

            self.logger.debug(f"Found {len(blocks)} blocks pending sync")
            return blocks

        except Exception as e:
            self.logger.error(f"Error finding pending sync blocks: {e}", exc_info=True)
            raise

    def find_with_tasks(self) -> List[TimeBlockModel]:
        """Find all time blocks with task relationships loaded."""
        try:
            blocks = self.session.query(self.model).options(
                joinedload(self.model.task)
            ).all()

            self.logger.debug(f"Found {len(blocks)} blocks with tasks loaded")
            return blocks

        except Exception as e:
            self.logger.error(f"Error loading blocks with tasks: {e}", exc_info=True)
            raise

    def get_day_statistics(self, target_date: date) -> dict:
        """Get statistics for a specific day."""
        try:
            blocks = self.find_by_date(target_date)

            total_minutes = sum(b.duration_minutes for b in blocks)
            task_blocks = [b for b in blocks if b.block_type == "TASK"]
            break_blocks = [b for b in blocks if b.block_type == "BREAK"]

            stats = {
                "date": target_date.isoformat(),
                "total_blocks": len(blocks),
                "total_minutes": total_minutes,
                "task_blocks": len(task_blocks),
                "break_blocks": len(break_blocks),
                "task_minutes": sum(b.duration_minutes for b in task_blocks),
                "break_minutes": sum(b.duration_minutes for b in break_blocks)
            }

            self.logger.debug(f"Day statistics for {target_date}: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Error getting day statistics: {e}", exc_info=True)
            raise
