# Data Models

## Overview

This document defines all data models used in the ADHD Planner system, including entity schemas, relationships, enums, and validation rules.

## Table of Contents
1. [Core Entity Models](#core-entity-models)
2. [Enumerations](#enumerations)
3. [Relationships](#relationships)
4. [Validation Rules](#validation-rules)
5. [Database Schema](#database-schema)

## Core Entity Models

### Task

The primary entity representing a to-do item.

```python
class Task:
    # Identity
    id: UUID
    title: str                          # Required, max 200 chars
    description: Optional[str]          # Optional, max 2000 chars

    # Time Management
    estimated_duration_minutes: int     # Required, > 0
    actual_duration_minutes: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime                # Auto-set on creation
    updated_at: datetime                # Auto-updated
    completed_at: Optional[datetime]

    # Energy & Context
    estimated_energy_level: EnergyLevel  # LOW, MEDIUM, HIGH
    requires_focus: bool                 # Default: True
    context_category: str                # "work", "personal", etc.

    # Scheduling
    scheduled_blocks: List[UUID]         # References to TimeBlock IDs
    priority: Priority                   # URGENT, HIGH, MEDIUM, LOW
    is_recurring: bool                   # Default: False
    recurrence_rule: Optional[str]       # iCal RRULE format

    # Sync
    sync_enabled: bool                   # Default: True
    apple_reminder_id: Optional[str]     # Apple Reminders ID
    last_synced_at: Optional[datetime]
    sync_status: SyncStatus              # SYNCED, PENDING, etc.

    # Metadata
    tags: List[str]                      # Free-form tags
    dependencies: List[UUID]             # Task IDs this depends on
    status: TaskStatus                   # NOT_STARTED, IN_PROGRESS, etc.
```

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write project report",
  "description": "Complete Q4 project summary report",
  "estimated_duration_minutes": 120,
  "actual_duration_minutes": null,
  "deadline": "2025-01-15T17:00:00Z",
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-01-10T09:00:00Z",
  "completed_at": null,
  "estimated_energy_level": "HIGH",
  "requires_focus": true,
  "context_category": "work",
  "scheduled_blocks": [],
  "priority": "HIGH",
  "is_recurring": false,
  "recurrence_rule": null,
  "sync_enabled": true,
  "apple_reminder_id": "x-apple-reminder://ABC123",
  "last_synced_at": "2025-01-10T09:01:00Z",
  "sync_status": "SYNCED",
  "tags": ["report", "Q4", "important"],
  "dependencies": [],
  "status": "NOT_STARTED"
}
```

### TimeBlock

Represents a scheduled block of time, either for a task or other activity.

```python
class TimeBlock:
    # Identity
    id: UUID
    task_id: Optional[UUID]              # None for breaks/free time

    # Timing
    start_time: datetime                 # Required
    end_time: datetime                   # Required
    duration_minutes: int                # Computed from start/end

    # Type
    block_type: BlockType                # TASK, BREAK, BUFFER, EVENT, FREE
    is_flexible: bool                    # Can be moved if needed

    # Sync
    apple_calendar_event_id: Optional[str]
    sync_enabled: bool                   # Default: True
    last_synced_at: Optional[datetime]

    # Context
    energy_level_required: EnergyLevel
    notes: Optional[str]
```

**Example**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_time": "2025-01-11T09:00:00Z",
  "end_time": "2025-01-11T11:00:00Z",
  "duration_minutes": 120,
  "block_type": "TASK",
  "is_flexible": false,
  "apple_calendar_event_id": "x-apple-calendar://XYZ789",
  "sync_enabled": true,
  "last_synced_at": "2025-01-10T09:05:00Z",
  "energy_level_required": "HIGH",
  "notes": "Morning focus session"
}
```

### UserPreferences

User-specific configuration and patterns.

```python
class UserPreferences:
    # Identity
    id: UUID
    user_id: str                         # For future multi-user support

    # Working Hours
    typical_work_start: time             # e.g., 09:00
    typical_work_end: time               # e.g., 17:00
    preferred_break_duration: int        # minutes

    # Energy Patterns
    peak_energy_times: List[TimeRange]
    low_energy_times: List[TimeRange]

    # ADHD-Specific Settings
    max_focus_duration: int              # minutes before break needed
    context_switch_penalty: int          # extra minutes after switch
    buffer_time_between_tasks: int       # minutes

    # Planning Preferences
    planning_horizon_days: int           # how far ahead to plan
    default_task_duration: int           # minutes

    # Sync Settings
    default_sync_to_reminders: bool
    default_sync_to_calendar: bool
    sync_interval_minutes: int

    # LLM Settings
    llm_provider: str                    # "ollama", "gemini", "claude"
    model_name: str
    temperature: float                   # 0.0 to 1.0
```

**Example**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "default",
  "typical_work_start": "09:00:00",
  "typical_work_end": "17:00:00",
  "preferred_break_duration": 15,
  "peak_energy_times": [
    {"start": "09:00:00", "end": "12:00:00"},
    {"start": "19:00:00", "end": "21:00:00"}
  ],
  "low_energy_times": [
    {"start": "14:00:00", "end": "16:00:00"}
  ],
  "max_focus_duration": 45,
  "context_switch_penalty": 5,
  "buffer_time_between_tasks": 10,
  "planning_horizon_days": 7,
  "default_task_duration": 30,
  "default_sync_to_reminders": true,
  "default_sync_to_calendar": true,
  "sync_interval_minutes": 5,
  "llm_provider": "ollama",
  "model_name": "llama3.1",
  "temperature": 0.7
}
```

### EnergyLog

Records of user energy levels over time.

```python
class EnergyLog:
    # Identity
    id: UUID
    timestamp: datetime

    # Energy Data
    reported_energy: EnergyLevel         # User-reported
    predicted_energy: Optional[EnergyLevel]  # System prediction

    # Context
    tasks_completed: int
    context_switches: int
    time_since_break: int                # minutes

    # Analysis
    energy_accuracy: Optional[float]     # How accurate was prediction (0-1)
```

**Example**:
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "timestamp": "2025-01-10T14:30:00Z",
  "reported_energy": "MEDIUM",
  "predicted_energy": "HIGH",
  "tasks_completed": 2,
  "context_switches": 3,
  "time_since_break": 90,
  "energy_accuracy": 0.6
}
```

### CalendarEvent

External calendar events (from Apple Calendar or manual entry).

```python
class CalendarEvent:
    # Identity
    id: UUID
    title: str
    start_time: datetime
    end_time: datetime

    # Source
    source: EventSource                  # LOCAL, APPLE_CALENDAR, SYNCED
    apple_event_id: Optional[str]

    # Metadata
    is_all_day: bool
    location: Optional[str]
    notes: Optional[str]

    # Integration
    related_task_id: Optional[UUID]      # Link to Task if applicable
```

### SyncOperation

Tracks pending and completed sync operations.

```python
class SyncOperation:
    # Identity
    id: UUID
    operation_type: OperationType        # CREATE, UPDATE, DELETE
    direction: SyncDirection             # LOCAL_TO_APPLE, APPLE_TO_LOCAL
    entity_type: EntityType              # TASK, TIME_BLOCK, EVENT
    entity_id: UUID

    # Status
    status: SyncStatus
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int                     # Number of retry attempts
```

## Enumerations

### EnergyLevel

```python
class EnergyLevel(Enum):
    LOW = "low"          # Low energy, suitable for simple tasks
    MEDIUM = "medium"    # Medium energy, most tasks
    HIGH = "high"        # High energy, complex/creative tasks
```

### Priority

```python
class Priority(Enum):
    URGENT = "urgent"    # Immediate attention needed
    HIGH = "high"        # Important, should be done soon
    MEDIUM = "medium"    # Normal priority
    LOW = "low"          # Can be deferred
```

### TaskStatus

```python
class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"        # Waiting on dependency
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

### BlockType

```python
class BlockType(Enum):
    TASK = "task"        # Time allocated for a task
    BREAK = "break"      # Scheduled break time
    BUFFER = "buffer"    # Context switch buffer
    EVENT = "event"      # External calendar event
    FREE = "free"        # Unscheduled time
```

### SyncStatus

```python
class SyncStatus(Enum):
    SYNCED = "synced"        # Successfully synced
    PENDING = "pending"      # Waiting to sync
    CONFLICT = "conflict"    # Conflict detected
    DISABLED = "disabled"    # Sync disabled for this item
    ERROR = "error"          # Sync failed
```

### OperationType

```python
class OperationType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
```

### SyncDirection

```python
class SyncDirection(Enum):
    LOCAL_TO_APPLE = "local_to_apple"
    APPLE_TO_LOCAL = "apple_to_local"
```

### EntityType

```python
class EntityType(Enum):
    TASK = "task"
    TIME_BLOCK = "time_block"
    EVENT = "event"
```

### EventSource

```python
class EventSource(Enum):
    LOCAL = "local"              # Created in ADHD Planner
    APPLE_CALENDAR = "apple_calendar"  # From Apple Calendar
    SYNCED = "synced"            # Bidirectionally synced
```

## Relationships

### Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐
│     Task     │────────▶│  TimeBlock   │
│              │ 1:N     │              │
└──────────────┘         └──────────────┘
       │                        │
       │ N:1                    │ 1:1
       ▼                        ▼
┌──────────────┐         ┌──────────────┐
│CalendarEvent │         │ SyncOperation│
│              │         │              │
└──────────────┘         └──────────────┘
       │
       │ N:1
       ▼
┌──────────────┐
│  EnergyLog   │
│              │
└──────────────┘
       │
       │ N:1
       ▼
┌──────────────┐
│UserPreferences│
│              │
└──────────────┘
```

### Relationship Details

**Task → TimeBlock** (One-to-Many)
- One task can have multiple scheduled time blocks
- A time block belongs to zero or one task (can be a break/buffer)
- Cascade delete: Deleting a task deletes its time blocks

**Task → CalendarEvent** (One-to-One, Optional)
- A task may be linked to a calendar event
- A calendar event may be linked to a task
- Used for synced items

**Task → SyncOperation** (One-to-Many)
- A task can have multiple sync operations (history)
- Latest sync operation indicates current sync status

**Task → Task** (Many-to-Many, Dependencies)
- Tasks can depend on other tasks
- Dependency relationships are explicit
- Used for scheduling constraints

## Validation Rules

### Task Validation

```python
def validate_task(task: Task):
    # Title
    assert 1 <= len(task.title) <= 200, "Title must be 1-200 characters"

    # Duration
    assert task.estimated_duration_minutes > 0, "Duration must be positive"
    assert task.estimated_duration_minutes <= 1440, "Duration max 24 hours"

    # Dates
    if task.deadline:
        assert task.deadline > task.created_at, "Deadline must be in future"

    if task.completed_at:
        assert task.status == TaskStatus.COMPLETED, "Completed tasks must have COMPLETED status"

    # Dependencies
    for dep_id in task.dependencies:
        assert dep_id != task.id, "Task cannot depend on itself"
        # Check for circular dependencies (complex check)
```

### TimeBlock Validation

```python
def validate_time_block(block: TimeBlock):
    # Times
    assert block.end_time > block.start_time, "End must be after start"

    # Duration consistency
    calculated_duration = (block.end_time - block.start_time).total_seconds() / 60
    assert abs(calculated_duration - block.duration_minutes) < 1, "Duration mismatch"

    # Block type
    if block.block_type == BlockType.TASK:
        assert block.task_id is not None, "TASK blocks must have task_id"
    elif block.block_type in [BlockType.BREAK, BlockType.BUFFER, BlockType.FREE]:
        assert block.task_id is None, "Non-task blocks cannot have task_id"
```

### UserPreferences Validation

```python
def validate_user_preferences(prefs: UserPreferences):
    # Working hours
    assert prefs.typical_work_start < prefs.typical_work_end, "Work start before end"

    # Durations
    assert 5 <= prefs.max_focus_duration <= 120, "Focus duration 5-120 minutes"
    assert 0 <= prefs.context_switch_penalty <= 30, "Switch penalty 0-30 minutes"
    assert 0 <= prefs.buffer_time_between_tasks <= 30, "Buffer 0-30 minutes"

    # LLM settings
    assert 0.0 <= prefs.temperature <= 1.0, "Temperature 0.0-1.0"
    assert prefs.llm_provider in ["ollama", "gemini", "claude"], "Valid provider"
```

## Database Schema

### SQLAlchemy Models

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(String(2000))
    estimated_duration_minutes = Column(Integer, nullable=False)
    actual_duration_minutes = Column(Integer)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    estimated_energy_level = Column(String(10), nullable=False)
    requires_focus = Column(Boolean, default=True)
    context_category = Column(String(50))
    priority = Column(String(10), nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(200))
    sync_enabled = Column(Boolean, default=True)
    apple_reminder_id = Column(String(200))
    last_synced_at = Column(DateTime)
    sync_status = Column(String(20), default="PENDING")
    tags = Column(ARRAY(String))  # PostgreSQL specific, use JSON for SQLite
    status = Column(String(20), default="NOT_STARTED")

    # Relationships
    time_blocks = relationship("TimeBlockModel", back_populates="task", cascade="all, delete-orphan")
    sync_operations = relationship("SyncOperationModel", back_populates="task")

    # Indexes
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_deadline', 'deadline'),
        Index('idx_task_created_at', 'created_at'),
    )
```

### SQLite Adaptations

For SQLite compatibility:
- Use `TEXT` instead of `VARCHAR` with length
- Store arrays/lists as JSON strings
- Use `INTEGER` for booleans (0/1)
- Use `TEXT` for UUIDs (stored as strings)

## Related Documentation

- [System Overview](system-overview.md)
- [Agent System](agent-system.md)
- [API Schemas](../api/data-schemas.md)
- [Database Schema Details](../technical/directory-structure.md#database-layer)
