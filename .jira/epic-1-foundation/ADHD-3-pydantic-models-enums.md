# ADHD-3: Pydantic Models & Enums

## Story Information

- **Epic**: Foundation
- **Story Points**: 2
- **Estimated Time**: 2 hours
- **Prerequisites**: ADHD-2 (Database Schema)
- **Status**: 📋 Not Started

## Description

Create Pydantic models that mirror the database schema for type-safe data transfer between layers. Also define all enums used throughout the application. These models provide validation, serialization, and clear type hints for the entire codebase.

## Goals

1. Create Pydantic models for all database entities
2. Define all enums (TaskStatus, Priority, EnergyLevel, BlockType, etc.)
3. Add validation rules for each model
4. Implement type conversions between Pydantic and SQLAlchemy models
5. Add computed fields and helper methods
6. Create base model with common functionality

## Acceptance Criteria

- [ ] Pydantic models created for all entities
- [ ] All enums defined with proper values
- [ ] Validation rules enforce business constraints
- [ ] Models can convert to/from SQLAlchemy models
- [ ] All models have docstrings
- [ ] Type hints are complete
- [ ] Unit tests pass

## Files to Create

```
src/models/__init__.py
src/models/base.py                  # Base Pydantic model
src/models/enums.py                 # All enums
src/models/task.py                  # Task Pydantic model
src/models/time_block.py            # TimeBlock Pydantic model
src/models/user_preferences.py      # UserPreferences model
src/models/energy_log.py            # EnergyLog model
src/models/calendar_event.py        # CalendarEvent model
src/models/sync_operation.py        # SyncOperation model
tests/unit/test_models.py           # Model tests
```

## Implementation Steps

### Step 1: Define Enums (20 min)

**File**: `src/models/enums.py`

```python
"""Enums used throughout the application."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task status values."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class Priority(str, Enum):
    """Task priority levels."""

    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EnergyLevel(str, Enum):
    """Energy level requirements."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BlockType(str, Enum):
    """Time block types."""

    TASK = "TASK"
    BREAK = "BREAK"
    BUFFER = "BUFFER"
    EVENT = "EVENT"
    FREE = "FREE"


class SyncStatus(str, Enum):
    """Sync operation status."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SyncDirection(str, Enum):
    """Sync direction."""

    LOCAL_TO_APPLE = "LOCAL_TO_APPLE"
    APPLE_TO_LOCAL = "APPLE_TO_LOCAL"


class SyncOperationType(str, Enum):
    """Type of sync operation."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class EventSource(str, Enum):
    """Calendar event source."""

    LOCAL = "LOCAL"
    APPLE_CALENDAR = "APPLE_CALENDAR"
    SYNCED = "SYNCED"
```

### Step 2: Base Pydantic Model (15 min)

**File**: `src/models/base.py`

```python
"""Base Pydantic model with common functionality."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseAppModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Allow from_orm() for SQLAlchemy models
        validate_assignment=True,  # Validate on field assignment
        use_enum_values=True,  # Use enum values instead of enum objects
        str_strip_whitespace=True,  # Strip whitespace from strings
    )


class TimestampedModel(BaseAppModel):
    """Model with created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def mark_updated(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
```

### Step 3: Task Model (30 min)

**File**: `src/models/task.py`

```python
"""Task Pydantic model."""

from datetime import datetime
from typing import Optional, List
from pydantic import Field, field_validator, computed_field

from src.models.base import BaseAppModel, TimestampedModel
from src.models.enums import TaskStatus, Priority, EnergyLevel, SyncStatus


class Task(TimestampedModel):
    """Task data model."""

    # Identity
    id: Optional[str] = None
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None

    # Time management
    estimated_duration_minutes: int = Field(gt=0, le=1440)
    actual_duration_minutes: Optional[int] = Field(None, gt=0)
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Energy & context
    estimated_energy_level: EnergyLevel = EnergyLevel.MEDIUM
    requires_focus: bool = True
    context_category: Optional[str] = Field(None, max_length=50)

    # Scheduling
    priority: Priority = Priority.MEDIUM
    is_recurring: bool = False
    recurrence_rule: Optional[str] = Field(None, max_length=200)

    # Status
    status: TaskStatus = TaskStatus.NOT_STARTED

    # Sync
    sync_enabled: bool = True
    apple_reminder_id: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING

    # Metadata
    tags: List[str] = Field(default_factory=list)

    @field_validator('deadline')
    @classmethod
    def deadline_must_be_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that deadline is in the future."""
        if v is not None and v < datetime.utcnow():
            raise ValueError('Deadline must be in the future')
        return v

    @field_validator('tags')
    @classmethod
    def tags_must_be_unique(cls, v: List[str]) -> List[str]:
        """Ensure tags are unique."""
        return list(set(v))

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.deadline is None or self.status == TaskStatus.COMPLETED:
            return False
        return datetime.utcnow() > self.deadline

    @computed_field
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    @computed_field
    @property
    def duration_accuracy(self) -> Optional[float]:
        """Calculate estimation accuracy if task is completed."""
        if self.actual_duration_minutes is None:
            return None

        estimated = self.estimated_duration_minutes
        actual = self.actual_duration_minutes

        if estimated == 0:
            return None

        # Negative means underestimated, positive means overestimated
        error_percentage = ((actual - estimated) / estimated) * 100
        return round(error_percentage, 1)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Write monthly report",
                "description": "Prepare and write the monthly status report",
                "estimated_duration_minutes": 60,
                "estimated_energy_level": "HIGH",
                "priority": "URGENT",
                "requires_focus": True,
                "context_category": "writing",
                "tags": ["work", "report"]
            }
        }


class TaskCreate(BaseAppModel):
    """Schema for creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    estimated_duration_minutes: int = Field(default=30, gt=0, le=1440)
    estimated_energy_level: EnergyLevel = EnergyLevel.MEDIUM
    priority: Priority = Priority.MEDIUM
    deadline: Optional[datetime] = None
    context_category: Optional[str] = None
    requires_focus: bool = True
    tags: List[str] = Field(default_factory=list)
    sync_enabled: bool = True


class TaskUpdate(BaseAppModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(None, gt=0, le=1440)
    estimated_energy_level: Optional[EnergyLevel] = None
    priority: Optional[Priority] = None
    deadline: Optional[datetime] = None
    context_category: Optional[str] = None
    requires_focus: Optional[bool] = None
    status: Optional[TaskStatus] = None
    tags: Optional[List[str]] = None
```

### Step 4: TimeBlock Model (20 min)

**File**: `src/models/time_block.py`

```python
"""TimeBlock Pydantic model."""

from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator, computed_field

from src.models.base import BaseAppModel
from src.models.enums import BlockType, EnergyLevel


class TimeBlock(BaseAppModel):
    """Time block data model."""

    # Identity
    id: Optional[str] = None
    task_id: Optional[str] = None

    # Timing
    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(gt=0)

    # Type
    block_type: BlockType = BlockType.TASK
    is_flexible: bool = False

    # Sync
    apple_calendar_event_id: Optional[str] = None
    sync_enabled: bool = True
    last_synced_at: Optional[datetime] = None

    # Context
    energy_level_required: Optional[EnergyLevel] = None
    notes: Optional[str] = None

    @field_validator('end_time')
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        """Validate that end_time is after start_time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    @computed_field
    @property
    def is_past(self) -> bool:
        """Check if time block is in the past."""
        return datetime.utcnow() > self.end_time

    @computed_field
    @property
    def is_current(self) -> bool:
        """Check if time block is currently active."""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time

    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "2025-01-01T09:00:00",
                "end_time": "2025-01-01T10:00:00",
                "duration_minutes": 60,
                "block_type": "TASK",
                "energy_level_required": "HIGH"
            }
        }


class TimeBlockCreate(BaseAppModel):
    """Schema for creating a time block."""

    start_time: datetime
    end_time: datetime
    block_type: BlockType = BlockType.TASK
    task_id: Optional[str] = None
    is_flexible: bool = False
    energy_level_required: Optional[EnergyLevel] = None
    notes: Optional[str] = None
    sync_enabled: bool = True


class TimeBlockUpdate(BaseAppModel):
    """Schema for updating a time block."""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    block_type: Optional[BlockType] = None
    is_flexible: Optional[bool] = None
    energy_level_required: Optional[EnergyLevel] = None
    notes: Optional[str] = None
```

### Step 5: Other Models (30 min)

**File**: `src/models/user_preferences.py`

```python
"""UserPreferences Pydantic model."""

from typing import Optional, List, Dict
from pydantic import Field

from src.models.base import BaseAppModel


class EnergyTimeSlot(BaseAppModel):
    """Time slot with energy level."""

    start: str = Field(pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    end: str = Field(pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')


class UserPreferences(BaseAppModel):
    """User preferences data model."""

    id: Optional[str] = None
    user_id: str = "default"

    # Working hours
    typical_work_start: str = Field(
        default="09:00",
        pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    )
    typical_work_end: str = Field(
        default="17:00",
        pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    )
    preferred_break_duration: int = Field(default=15, gt=0, le=60)

    # Energy patterns
    peak_energy_times: List[EnergyTimeSlot] = Field(default_factory=list)
    low_energy_times: List[EnergyTimeSlot] = Field(default_factory=list)

    # ADHD settings
    max_focus_duration: int = Field(default=45, gt=0, le=120)
    context_switch_penalty: int = Field(default=5, ge=0, le=30)
    buffer_time_between_tasks: int = Field(default=10, ge=0, le=30)

    # Planning
    planning_horizon_days: int = Field(default=7, gt=0, le=30)
    default_task_duration: int = Field(default=30, gt=0, le=480)

    # Sync
    default_sync_to_reminders: bool = True
    default_sync_to_calendar: bool = True
    sync_interval_minutes: int = Field(default=5, gt=0, le=60)

    # LLM settings
    llm_provider: str = Field(default="ollama", pattern=r'^(ollama|gemini|claude|anthropic)$')
    model_name: str = Field(default="llama3.1", max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
```

**File**: `src/models/energy_log.py`

```python
"""EnergyLog Pydantic model."""

from datetime import datetime
from typing import Optional
from pydantic import Field

from src.models.base import BaseAppModel
from src.models.enums import EnergyLevel


class EnergyLog(BaseAppModel):
    """Energy log data model."""

    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Energy data
    reported_energy: EnergyLevel
    predicted_energy: Optional[EnergyLevel] = None

    # Context
    tasks_completed: int = Field(default=0, ge=0)
    context_switches: int = Field(default=0, ge=0)
    time_since_break: int = Field(default=0, ge=0)

    # Analysis
    energy_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
```

**File**: `src/models/calendar_event.py`

```python
"""CalendarEvent Pydantic model."""

from datetime import datetime
from typing import Optional
from pydantic import Field

from src.models.base import BaseAppModel
from src.models.enums import EventSource


class CalendarEvent(BaseAppModel):
    """Calendar event data model."""

    id: Optional[str] = None
    title: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime

    # Source
    source: EventSource = EventSource.LOCAL
    apple_event_id: Optional[str] = None

    # Metadata
    is_all_day: bool = False
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    # Integration
    related_task_id: Optional[str] = None
```

**File**: `src/models/sync_operation.py`

```python
"""SyncOperation Pydantic model."""

from datetime import datetime
from typing import Optional
from pydantic import Field

from src.models.base import BaseAppModel, TimestampedModel
from src.models.enums import SyncOperationType, SyncDirection, SyncStatus


class SyncOperation(TimestampedModel):
    """Sync operation data model."""

    id: Optional[str] = None
    operation_type: SyncOperationType
    direction: SyncDirection
    entity_type: str = Field(max_length=20)
    entity_id: str

    # Status
    status: SyncStatus = SyncStatus.PENDING
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)

    # Relationships
    task_id: Optional[str] = None
```

### Step 6: Update __init__.py (5 min)

**File**: `src/models/__init__.py`

```python
"""Pydantic models for data validation and transfer."""

from src.models.enums import (
    TaskStatus,
    Priority,
    EnergyLevel,
    BlockType,
    SyncStatus,
    SyncDirection,
    SyncOperationType,
    EventSource
)
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.time_block import TimeBlock, TimeBlockCreate, TimeBlockUpdate
from src.models.user_preferences import UserPreferences, EnergyTimeSlot
from src.models.energy_log import EnergyLog
from src.models.calendar_event import CalendarEvent
from src.models.sync_operation import SyncOperation

__all__ = [
    # Enums
    "TaskStatus",
    "Priority",
    "EnergyLevel",
    "BlockType",
    "SyncStatus",
    "SyncDirection",
    "SyncOperationType",
    "EventSource",
    # Models
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TimeBlock",
    "TimeBlockCreate",
    "TimeBlockUpdate",
    "UserPreferences",
    "EnergyTimeSlot",
    "EnergyLog",
    "CalendarEvent",
    "SyncOperation",
]
```

### Step 7: Unit Tests (20 min)

**File**: `tests/unit/test_models.py`

```python
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
    # Task with past deadline
    task = Task(
        title="Test",
        estimated_duration_minutes=30,
        deadline=datetime.utcnow() - timedelta(hours=1)
    )
    task.deadline = datetime.utcnow() - timedelta(hours=1)  # Bypass validation
    assert task.is_overdue is True

    # Completed task is never overdue
    task.status = TaskStatus.COMPLETED
    assert task.is_overdue is False


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
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_models.py -v

# 2. Test imports
uv run python -c "
from src.models import Task, TimeBlock, TaskStatus, Priority
print('Task:', Task)
print('TaskStatus:', list(TaskStatus))
print('All imports successful')
"

# 3. Test model creation
uv run python -c "
from src.models import Task, Priority, EnergyLevel

task = Task(
    title='Test task',
    estimated_duration_minutes=60,
    priority=Priority.HIGH,
    estimated_energy_level=EnergyLevel.HIGH
)
print(f'Created task: {task.title}')
print(f'Is overdue: {task.is_overdue}')
"

# 4. Test validation
uv run python -c "
from src.models import Task
try:
    task = Task(title='', estimated_duration_minutes=30)
except Exception as e:
    print(f'Validation error caught: {type(e).__name__}')
"

# 5. Run all tests
uv run pytest tests/unit/ -v

# 6. Code quality
uv run ruff check src/models/
uv run black --check src/models/
```

## Success Criteria

- ✅ All Pydantic models created
- ✅ All enums defined
- ✅ Validation rules work correctly
- ✅ Computed fields calculate correctly
- ✅ Models serialize/deserialize properly
- ✅ All unit tests pass
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: Validation errors on model creation
**Solution**: Check field constraints, ensure all required fields provided

### Issue: Enum values not matching database
**Solution**: Use `use_enum_values=True` in model config

### Issue: from_orm() not working
**Solution**: Ensure `from_attributes=True` in model config

### Issue: Datetime validation fails
**Solution**: Use timezone-aware datetimes or configure Pydantic to handle naive datetimes

## Next Story

Once this story is complete, move to:
**[ADHD-4: Base Repository Pattern](ADHD-4-base-repository-pattern.md)**

## Notes

- Pydantic models are the source of truth for data validation
- These models are used throughout services, agents, and UI
- Validation should be strict but provide clear error messages
- Computed fields avoid duplication and ensure consistency
- Use separate Create/Update schemas to control what can be changed
- Type hints enable excellent IDE support and catch errors early
