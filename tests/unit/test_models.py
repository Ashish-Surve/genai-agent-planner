"""Test Pydantic models."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.task import Task, TaskCreate
from src.models.time_block import TimeBlock
from src.models.enums import TaskStatus, Priority, EnergyLevel


def test_task_creation():
    """Test creating a valid task."""
    task = Task(
        title="Test task",
        estimated_duration_minutes=30,
        estimated_energy_level=EnergyLevel.MEDIUM,
        priority=Priority.HIGH
    )

    assert task.title == "Test task"
    assert task.estimated_duration_minutes == 30
    assert task.status == TaskStatus.NOT_STARTED


def test_task_validation_errors():
    """Test task validation."""
    # Empty title
    with pytest.raises(ValidationError):
        Task(title="", estimated_duration_minutes=30)

    # Negative duration
    with pytest.raises(ValidationError):
        Task(title="Test", estimated_duration_minutes=-10)

    # Duration too long
    with pytest.raises(ValidationError):
        Task(title="Test", estimated_duration_minutes=2000)


def test_task_deadline_validation():
    """Test deadline must be in future."""
    past_date = datetime.utcnow() - timedelta(days=1)

    with pytest.raises(ValidationError, match="must be in the future"):
        Task(
            title="Test",
            estimated_duration_minutes=30,
            deadline=past_date
        )


def test_task_is_overdue():
    """Test is_overdue computed field."""
    # Task with future deadline - not overdue
    future_task = Task(
        title="Test",
        estimated_duration_minutes=30,
        deadline=datetime.utcnow() + timedelta(hours=1)
    )
    assert future_task.is_overdue is False

    # Task without deadline - not overdue
    no_deadline_task = Task(
        title="Test",
        estimated_duration_minutes=30
    )
    assert no_deadline_task.is_overdue is False


def test_task_duration_accuracy():
    """Test duration accuracy calculation."""
    task = Task(
        title="Test",
        estimated_duration_minutes=60,
        actual_duration_minutes=90
    )

    # 90 - 60 = 30, 30/60 = 0.5 = 50%
    assert task.duration_accuracy == 50.0


def test_task_tags_unique():
    """Test that tags are made unique."""
    task = Task(
        title="Test",
        estimated_duration_minutes=30,
        tags=["work", "important", "work"]
    )

    assert len(task.tags) == 2
    assert set(task.tags) == {"work", "important"}


def test_time_block_validation():
    """Test time block validation."""
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 10, 0)

    block = TimeBlock(
        start_time=start,
        end_time=end,
        duration_minutes=60
    )

    assert block.start_time == start
    assert block.end_time == end


def test_time_block_end_before_start():
    """Test that end_time must be after start_time."""
    start = datetime(2025, 1, 1, 10, 0)
    end = datetime(2025, 1, 1, 9, 0)

    with pytest.raises(ValidationError, match="must be after"):
        TimeBlock(
            start_time=start,
            end_time=end,
            duration_minutes=60
        )


def test_time_block_is_current():
    """Test is_current computed field."""
    now = datetime.utcnow()
    start = now - timedelta(minutes=30)
    end = now + timedelta(minutes=30)

    block = TimeBlock(
        start_time=start,
        end_time=end,
        duration_minutes=60
    )

    assert block.is_current is True


def test_task_create_schema():
    """Test TaskCreate schema."""
    task_data = TaskCreate(
        title="New task",
        estimated_duration_minutes=45,
        priority=Priority.URGENT,
        tags=["work"]
    )

    assert task_data.title == "New task"
    assert task_data.estimated_duration_minutes == 45
    assert task_data.priority == Priority.URGENT


def test_enum_values():
    """Test enum string values."""
    assert TaskStatus.NOT_STARTED.value == "NOT_STARTED"
    assert Priority.HIGH.value == "HIGH"
    assert EnergyLevel.MEDIUM.value == "MEDIUM"
