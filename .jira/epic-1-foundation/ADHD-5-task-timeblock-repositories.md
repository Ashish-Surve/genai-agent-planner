# ADHD-5: Task & TimeBlock Repositories

## Story Information

- **Epic**: Foundation
- **Story Points**: 3
- **Estimated Time**: 3 hours
- **Prerequisites**: ADHD-4 (Base Repository Pattern)
- **Status**: ✅ Complete

## Description

Implement specialized repositories for Tasks and TimeBlocks that extend the base repository with domain-specific query methods. These repositories provide efficient data access patterns needed by the service layer, including filtering by status, deadline queries, conflict detection, and relationship handling.

## Goals

1. Create TaskRepository with task-specific queries
2. Create TimeBlockRepository with scheduling queries
3. Implement efficient filtering and sorting
4. Add relationship handling (tasks with dependencies, blocks with tasks)
5. Implement conflict detection for time blocks
6. Add date-based queries for scheduling
7. Create specialized query methods for common use cases

## Acceptance Criteria

- [x] TaskRepository implements all task queries
- [x] TimeBlockRepository implements all scheduling queries
- [x] Queries are efficient (use proper indexing)
- [x] Relationship loading works correctly
- [x] Conflict detection is accurate
- [x] All query methods tested
- [x] Unit tests pass (23/23 passing)

## Files to Create

```
src/repositories/task_repository.py           # Task repository
src/repositories/time_block_repository.py     # TimeBlock repository
tests/unit/test_task_repository.py            # Task repo tests
tests/unit/test_time_block_repository.py      # TimeBlock repo tests
```

## Implementation Steps

### Step 1: Task Repository (60 min)

**File**: `src/repositories/task_repository.py`

```python
"""Task repository with specialized queries."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from src.repositories.base_repository import BaseRepository
from src.database.schema import TaskModel
from src.utils.logger import get_logger

logger = get_logger("task_repository")


class TaskRepository(BaseRepository[TaskModel]):
    """Repository for task-specific queries."""

    def __init__(self, session: Session):
        """Initialize task repository."""
        super().__init__(TaskModel, session)

    def find_by_status(self, status: str) -> List[TaskModel]:
        """
        Find all tasks with a specific status.

        Args:
            status: Task status (NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED)

        Returns:
            List of matching tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.status == status
            ).order_by(self.model.created_at.desc()).all()

            self.logger.debug(f"Found {len(tasks)} tasks with status: {status}")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by status: {e}", exc_info=True)
            raise

    def find_by_priority(self, priority: str) -> List[TaskModel]:
        """
        Find all tasks with a specific priority.

        Args:
            priority: Task priority (URGENT, HIGH, MEDIUM, LOW)

        Returns:
            List of matching tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.priority == priority
            ).order_by(self.model.deadline.asc()).all()

            self.logger.debug(f"Found {len(tasks)} tasks with priority: {priority}")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by priority: {e}", exc_info=True)
            raise

    def find_overdue(self) -> List[TaskModel]:
        """
        Find all overdue tasks (past deadline, not completed).

        Returns:
            List of overdue tasks
        """
        try:
            now = datetime.utcnow()

            tasks = self.session.query(self.model).filter(
                self.model.deadline < now,
                self.model.status != "COMPLETED"
            ).order_by(self.model.deadline.asc()).all()

            self.logger.debug(f"Found {len(tasks)} overdue tasks")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding overdue tasks: {e}", exc_info=True)
            raise

    def find_due_soon(self, hours: int = 24) -> List[TaskModel]:
        """
        Find tasks due within the specified number of hours.

        Args:
            hours: Number of hours to look ahead

        Returns:
            List of tasks due soon
        """
        try:
            from datetime import timedelta
            now = datetime.utcnow()
            future = now + timedelta(hours=hours)

            tasks = self.session.query(self.model).filter(
                self.model.deadline.between(now, future),
                self.model.status != "COMPLETED"
            ).order_by(self.model.deadline.asc()).all()

            self.logger.debug(f"Found {len(tasks)} tasks due within {hours} hours")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks due soon: {e}", exc_info=True)
            raise

    def find_by_energy_level(self, energy_level: str) -> List[TaskModel]:
        """
        Find tasks requiring a specific energy level.

        Args:
            energy_level: Energy level (LOW, MEDIUM, HIGH)

        Returns:
            List of matching tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.estimated_energy_level == energy_level,
                self.model.status != "COMPLETED"
            ).all()

            self.logger.debug(
                f"Found {len(tasks)} tasks requiring {energy_level} energy"
            )
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by energy level: {e}", exc_info=True)
            raise

    def find_by_context(self, context_category: str) -> List[TaskModel]:
        """
        Find tasks in a specific context/category.

        Args:
            context_category: Context category

        Returns:
            List of matching tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.context_category == context_category
            ).all()

            self.logger.debug(
                f"Found {len(tasks)} tasks in context: {context_category}"
            )
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by context: {e}", exc_info=True)
            raise

    def find_with_dependencies(self) -> List[TaskModel]:
        """
        Find all tasks with their dependencies loaded.

        Returns:
            List of tasks with dependencies
        """
        try:
            tasks = self.session.query(self.model).options(
                joinedload(self.model.dependencies)
            ).all()

            self.logger.debug(f"Found {len(tasks)} tasks with dependencies loaded")
            return tasks

        except Exception as e:
            self.logger.error(f"Error loading tasks with dependencies: {e}", exc_info=True)
            raise

    def find_by_dependency(self, dependency_id: str) -> List[TaskModel]:
        """
        Find tasks that depend on a specific task.

        Args:
            dependency_id: ID of the dependency task

        Returns:
            List of dependent tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.dependencies.any(id=dependency_id)
            ).all()

            self.logger.debug(
                f"Found {len(tasks)} tasks depending on task {dependency_id}"
            )
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding dependent tasks: {e}", exc_info=True)
            raise

    def find_requiring_focus(self) -> List[TaskModel]:
        """
        Find tasks that require deep focus.

        Returns:
            List of focus-requiring tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.requires_focus == True,
                self.model.status != "COMPLETED"
            ).order_by(self.model.priority.desc()).all()

            self.logger.debug(f"Found {len(tasks)} tasks requiring focus")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding focus tasks: {e}", exc_info=True)
            raise

    def find_completed_with_durations(self) -> List[TaskModel]:
        """
        Find completed tasks that have actual durations recorded.

        Returns:
            List of completed tasks with durations
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.status == "COMPLETED",
                self.model.actual_duration_minutes.isnot(None)
            ).all()

            self.logger.debug(
                f"Found {len(tasks)} completed tasks with durations"
            )
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding completed tasks: {e}", exc_info=True)
            raise

    def find_pending_sync(self) -> List[TaskModel]:
        """
        Find tasks with pending sync operations.

        Returns:
            List of tasks pending sync
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.sync_enabled == True,
                self.model.sync_status == "PENDING"
            ).all()

            self.logger.debug(f"Found {len(tasks)} tasks pending sync")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding pending sync tasks: {e}", exc_info=True)
            raise

    def search_by_title(self, query: str) -> List[TaskModel]:
        """
        Search tasks by title (case-insensitive partial match).

        Args:
            query: Search query

        Returns:
            List of matching tasks
        """
        try:
            tasks = self.session.query(self.model).filter(
                self.model.title.ilike(f"%{query}%")
            ).all()

            self.logger.debug(f"Found {len(tasks)} tasks matching '{query}'")
            return tasks

        except Exception as e:
            self.logger.error(f"Error searching tasks: {e}", exc_info=True)
            raise

    def get_statistics(self) -> dict:
        """
        Get task statistics.

        Returns:
            Dictionary with task counts by status
        """
        try:
            stats = {
                "total": self.count(),
                "not_started": self.count({"status": "NOT_STARTED"}),
                "in_progress": self.count({"status": "IN_PROGRESS"}),
                "completed": self.count({"status": "COMPLETED"}),
                "blocked": self.count({"status": "BLOCKED"}),
                "overdue": len(self.find_overdue())
            }

            self.logger.debug(f"Task statistics: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Error getting task statistics: {e}", exc_info=True)
            raise
```

### Step 2: TimeBlock Repository (60 min)

**File**: `src/repositories/time_block_repository.py`

```python
"""TimeBlock repository with specialized queries."""

from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from src.repositories.base_repository import BaseRepository
from src.database.schema import TimeBlockModel
from src.utils.logger import get_logger

logger = get_logger("time_block_repository")


class TimeBlockRepository(BaseRepository[TimeBlockModel]):
    """Repository for time block specific queries."""

    def __init__(self, session: Session):
        """Initialize time block repository."""
        super().__init__(TimeBlockModel, session)

    def find_by_date(self, target_date: date) -> List[TimeBlockModel]:
        """
        Find all time blocks for a specific date.

        Args:
            target_date: Date to query

        Returns:
            List of time blocks for the date
        """
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
        """
        Find all time blocks within a date range.

        Args:
            start_date: Range start
            end_date: Range end (inclusive)

        Returns:
            List of time blocks in range
        """
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
        """
        Find all time blocks for a specific task.

        Args:
            task_id: Task ID

        Returns:
            List of time blocks for the task
        """
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
        """
        Find time blocks that conflict with the given time range.

        Args:
            start_time: Range start
            end_time: Range end
            exclude_block_id: Optional block ID to exclude from check

        Returns:
            List of conflicting time blocks
        """
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
        """
        Find time blocks by type, optionally within a date range.

        Args:
            block_type: Block type (TASK, BREAK, BUFFER, EVENT, FREE)
            start_date: Optional range start
            end_date: Optional range end

        Returns:
            List of matching time blocks
        """
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
        """
        Find all flexible time blocks.

        Returns:
            List of flexible blocks
        """
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
        """
        Find current and upcoming time blocks.

        Args:
            hours_ahead: How many hours ahead to look

        Returns:
            List of current and upcoming blocks
        """
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
        """
        Find time blocks with pending sync.

        Returns:
            List of blocks pending sync
        """
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
        """
        Find all time blocks with task relationships loaded.

        Returns:
            List of time blocks with tasks
        """
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
        """
        Get statistics for a specific day.

        Args:
            target_date: Date to analyze

        Returns:
            Dictionary with day statistics
        """
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
```

### Step 3: Update Repository __init__ (5 min)

**File**: `src/repositories/__init__.py`

```python
"""Repository layer for data access."""

from src.repositories.base_repository import BaseRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.time_block_repository import TimeBlockRepository

__all__ = [
    "BaseRepository",
    "TaskRepository",
    "TimeBlockRepository",
]
```

### Step 4: Unit Tests (35 min)

**File**: `tests/unit/test_task_repository.py`

```python
"""Test task repository."""

import pytest
from datetime import datetime, timedelta
from src.repositories.task_repository import TaskRepository


@pytest.fixture
def task_repo(test_db_session):
    """Create task repository."""
    return TaskRepository(test_db_session)


def test_find_by_status(task_repo):
    """Test finding tasks by status."""
    # Create tasks with different statuses
    task_repo.create({
        "title": "Not started task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "NOT_STARTED"
    })
    task_repo.create({
        "title": "In progress task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "IN_PROGRESS"
    })

    # Find by status
    not_started = task_repo.find_by_status("NOT_STARTED")
    assert len(not_started) == 1
    assert not_started[0].title == "Not started task"


def test_find_overdue(task_repo):
    """Test finding overdue tasks."""
    # Create overdue task
    past = datetime.utcnow() - timedelta(days=1)
    task_repo.create({
        "title": "Overdue task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "deadline": past
    })

    # Create future task
    future = datetime.utcnow() + timedelta(days=1)
    task_repo.create({
        "title": "Future task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "deadline": future
    })

    overdue = task_repo.find_overdue()
    assert len(overdue) == 1
    assert overdue[0].title == "Overdue task"


def test_find_completed_with_durations(task_repo):
    """Test finding completed tasks with durations."""
    task_repo.create({
        "title": "Completed task",
        "estimated_duration_minutes": 30,
        "actual_duration_minutes": 45,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "COMPLETED"
    })

    completed = task_repo.find_completed_with_durations()
    assert len(completed) == 1
    assert completed[0].actual_duration_minutes == 45


def test_get_statistics(task_repo):
    """Test getting task statistics."""
    # Create various tasks
    for i in range(3):
        task_repo.create({
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
            "status": "NOT_STARTED"
        })

    stats = task_repo.get_statistics()
    assert stats["total"] == 3
    assert stats["not_started"] == 3


**File**: `tests/unit/test_time_block_repository.py`

```python
"""Test time block repository."""

import pytest
from datetime import datetime, date, timedelta
from src.repositories.time_block_repository import TimeBlockRepository


@pytest.fixture
def block_repo(test_db_session):
    """Create time block repository."""
    return TimeBlockRepository(test_db_session)


def test_find_by_date(block_repo):
    """Test finding blocks by date."""
    target_date = date(2025, 1, 1)

    # Create block on target date
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    # Create block on different date
    block_repo.create({
        "start_time": datetime(2025, 1, 2, 9, 0),
        "end_time": datetime(2025, 1, 2, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    blocks = block_repo.find_by_date(target_date)
    assert len(blocks) == 1


def test_find_conflicts(block_repo):
    """Test finding conflicting blocks."""
    # Create existing block
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    # Check for conflicts
    conflicts = block_repo.find_conflicts(
        datetime(2025, 1, 1, 9, 30),
        datetime(2025, 1, 1, 10, 30)
    )

    assert len(conflicts) == 1


def test_get_day_statistics(block_repo):
    """Test getting day statistics."""
    target_date = date(2025, 1, 1)

    # Create blocks
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 10, 0),
        "end_time": datetime(2025, 1, 1, 10, 15),
        "duration_minutes": 15,
        "block_type": "BREAK"
    })

    stats = block_repo.get_day_statistics(target_date)
    assert stats["total_blocks"] == 2
    assert stats["task_minutes"] == 60
    assert stats["break_minutes"] == 15
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_task_repository.py -v
uv run pytest tests/unit/test_time_block_repository.py -v

# 2. Test task repository
uv run python -c "
from src.database.connection import get_db
from src.repositories.task_repository import TaskRepository

db = get_db()
with db.get_session() as session:
    repo = TaskRepository(session)

    # Create task
    task = repo.create({
        'title': 'Test task',
        'estimated_duration_minutes': 30,
        'estimated_energy_level': 'HIGH',
        'priority': 'URGENT'
    })

    # Find by status
    tasks = repo.find_by_status('NOT_STARTED')
    print(f'Found {len(tasks)} not started tasks')

    # Get statistics
    stats = repo.get_statistics()
    print(f'Statistics: {stats}')
"

# 3. Test time block repository
uv run python -c "
from datetime import datetime, date
from src.database.connection import get_db
from src.repositories.time_block_repository import TimeBlockRepository

db = get_db()
with db.get_session() as session:
    repo = TimeBlockRepository(session)

    # Create block
    block = repo.create({
        'start_time': datetime(2025, 1, 1, 9, 0),
        'end_time': datetime(2025, 1, 1, 10, 0),
        'duration_minutes': 60,
        'block_type': 'TASK'
    })

    # Find by date
    blocks = repo.find_by_date(date(2025, 1, 1))
    print(f'Found {len(blocks)} blocks for date')

    # Check conflicts
    conflicts = repo.find_conflicts(
        datetime(2025, 1, 1, 9, 30),
        datetime(2025, 1, 1, 10, 30)
    )
    print(f'Found {len(conflicts)} conflicts')
"

# 4. Run all tests
uv run pytest tests/unit/ -v

# 5. Code quality
uv run ruff check src/repositories/
uv run black --check src/repositories/
```

## Success Criteria

- ✅ TaskRepository implements all queries
- ✅ TimeBlockRepository implements all queries
- ✅ Conflict detection works correctly
- ✅ Date-based queries are efficient
- ✅ Relationship loading works
- ✅ All unit tests pass
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: Slow date range queries
**Solution**: Add indexes on start_time and end_time fields

### Issue: Conflict detection misses edge cases
**Solution**: Test with adjacent blocks, midnight crossovers, same start/end times

### Issue: Relationship loading causes N+1 queries
**Solution**: Use joinedload for eager loading of relationships

## Next Story

Once Epic 1 is complete, move to:
**[ADHD-6: Configuration & Logging Enhancement](../epic-2-services/ADHD-6-configuration-logging-enhancement.md)**

## Notes

- These repositories are heavily used by services - performance matters
- Proper indexing on frequently queried fields is critical
- Conflict detection algorithm must be bulletproof for scheduling
- Date-based queries should handle timezone edge cases
- Statistics methods help with dashboards and analytics
- Eager loading prevents N+1 query problems

---

## Completion Notes

**Status**: ✅ **COMPLETE** - Implemented and tested

**Implementation Details**:
- Created `TaskRepository` with 13 specialized query methods
- Created `TimeBlockRepository` with 10 specialized query methods
- All 23 unit tests passing
- Branch: `feature/ADHD-5-task-timeblock-repositories`
- Commit: feat(ADHD-5): Implement task and timeblock repositories

**Test Results**:
- TaskRepository: 11 tests passed
- TimeBlockRepository: 12 tests passed
- Code coverage: 48% (repositories at 60-69% coverage)

**Key Methods Implemented**:
1. **TaskRepository**: find_by_status, find_by_priority, find_overdue, find_due_soon, find_by_energy_level, find_by_context, find_with_dependencies, find_by_dependency, find_requiring_focus, find_completed_with_durations, find_pending_sync, search_by_title, get_statistics
2. **TimeBlockRepository**: find_by_date, find_by_date_range, find_conflicts, find_by_block_type, find_flexible_blocks, find_current_and_upcoming, find_pending_sync, find_with_tasks, get_day_statistics

**Ready for**: ADHD-6 (Configuration & Logging Enhancement)
