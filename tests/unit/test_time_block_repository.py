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

    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 2, 9, 0),
        "end_time": datetime(2025, 1, 2, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    blocks = block_repo.find_by_date(target_date)
    assert len(blocks) == 1
    assert blocks[0].start_time.date() == target_date


def test_find_by_date_range(block_repo):
    """Test finding blocks by date range."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 5, 9, 0),
        "end_time": datetime(2025, 1, 5, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 10, 9, 0),
        "end_time": datetime(2025, 1, 10, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    blocks = block_repo.find_by_date_range(date(2025, 1, 1), date(2025, 1, 7))
    assert len(blocks) == 2


def test_find_conflicts(block_repo):
    """Test finding conflicting blocks."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    conflicts = block_repo.find_conflicts(
        datetime(2025, 1, 1, 9, 30),
        datetime(2025, 1, 1, 10, 30)
    )
    assert len(conflicts) == 1


def test_find_conflicts_no_overlap(block_repo):
    """Test finding conflicts with no overlap."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    conflicts = block_repo.find_conflicts(
        datetime(2025, 1, 1, 10, 0),
        datetime(2025, 1, 1, 11, 0)
    )
    assert len(conflicts) == 0


def test_find_conflicts_exclude_block(block_repo):
    """Test finding conflicts excluding a block."""
    block = block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    conflicts = block_repo.find_conflicts(
        datetime(2025, 1, 1, 9, 30),
        datetime(2025, 1, 1, 10, 30),
        exclude_block_id=block.id
    )
    assert len(conflicts) == 0


def test_find_by_block_type(block_repo):
    """Test finding blocks by type."""
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

    task_blocks = block_repo.find_by_block_type("TASK")
    assert len(task_blocks) == 1
    assert task_blocks[0].block_type == "TASK"


def test_find_by_block_type_with_date_range(block_repo):
    """Test finding blocks by type within date range."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 5, 9, 0),
        "end_time": datetime(2025, 1, 5, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    blocks = block_repo.find_by_block_type(
        "TASK",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 2)
    )
    assert len(blocks) == 1


def test_find_flexible_blocks(block_repo):
    """Test finding flexible blocks."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK",
        "is_flexible": True
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 10, 0),
        "end_time": datetime(2025, 1, 1, 11, 0),
        "duration_minutes": 60,
        "block_type": "TASK",
        "is_flexible": False
    })

    flexible = block_repo.find_flexible_blocks()
    assert len(flexible) == 1
    assert flexible[0].is_flexible == True


def test_find_current_and_upcoming(block_repo):
    """Test finding current and upcoming blocks."""
    now = datetime.utcnow()

    block_repo.create({
        "start_time": now - timedelta(minutes=30),
        "end_time": now + timedelta(minutes=30),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": now + timedelta(hours=2),
        "end_time": now + timedelta(hours=3),
        "duration_minutes": 60,
        "block_type": "TASK"
    })
    block_repo.create({
        "start_time": now + timedelta(hours=5),
        "end_time": now + timedelta(hours=6),
        "duration_minutes": 60,
        "block_type": "TASK"
    })

    current = block_repo.find_current_and_upcoming(hours_ahead=4)
    assert len(current) == 2


def test_find_pending_sync(block_repo):
    """Test finding blocks pending sync."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK",
        "sync_enabled": True,
        "apple_calendar_event_id": None
    })
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 10, 0),
        "end_time": datetime(2025, 1, 1, 11, 0),
        "duration_minutes": 60,
        "block_type": "TASK",
        "sync_enabled": True,
        "apple_calendar_event_id": "event-123"
    })

    pending = block_repo.find_pending_sync()
    assert len(pending) == 1
    assert pending[0].apple_calendar_event_id is None


def test_find_with_tasks(block_repo):
    """Test finding blocks with task relationships."""
    block_repo.create({
        "start_time": datetime(2025, 1, 1, 9, 0),
        "end_time": datetime(2025, 1, 1, 10, 0),
        "duration_minutes": 60,
        "block_type": "TASK",
        "task_id": None
    })

    blocks = block_repo.find_with_tasks()
    assert len(blocks) >= 1


def test_get_day_statistics(block_repo):
    """Test getting day statistics."""
    target_date = date(2025, 1, 1)

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
    assert stats["total_minutes"] == 75
