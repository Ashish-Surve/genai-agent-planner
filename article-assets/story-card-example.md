# Example Story Card: ADHD-3 (Pydantic Models & Enums)

This is an excerpt showing the structure of a story card designed for AI-assisted implementation.

## Story Information

- **Epic**: Foundation
- **Story Points**: 2
- **Estimated Time**: 2 hours
- **Prerequisites**: ADHD-2 (Database Schema)
- **Status**: ✅ Complete

## Description

Create Pydantic models that mirror the database schema for type-safe data transfer between layers. Also define all enums used throughout the application.

## Goals

1. Create Pydantic models for all database entities
2. Define all enums (TaskStatus, Priority, EnergyLevel, etc.)
3. Add validation rules for each model
4. Implement type conversions between Pydantic and SQLAlchemy
5. Add computed fields and helper methods

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
src/models/time_block.py            # TimeBlock model
src/models/user_preferences.py      # UserPreferences
src/models/energy_log.py            # EnergyLog
src/models/calendar_event.py        # CalendarEvent
src/models/sync_operation.py        # SyncOperation
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

# ... (8 total enums defined)
```

### Step 2: Create Base Model (15 min)

**File**: `src/models/base.py`

```python
"""Base Pydantic model with common functionality."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseAppModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
    )

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Step 3: Task Model (20 min)

**File**: `src/models/task.py`

```python
"""Task Pydantic model with validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import Field, field_validator, computed_field

from .base import BaseAppModel
from .enums import TaskStatus, Priority, EnergyLevel

class TaskBase(BaseAppModel):
    """Base task fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    priority: Priority = Field(default=Priority.MEDIUM)
    # ... (full model with 15+ fields)

    @field_validator('estimated_duration_minutes')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration must be positive')
        return v

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.now() > self.due_date
        return False

# Separate Create/Update schemas for safe mutations
class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseAppModel):
    # All fields optional for partial updates
    title: Optional[str] = None
    # ...
```

### [Additional Steps 4-7...]

## Testing Checklist

- [ ] Run `pytest tests/unit/test_models.py -v`
- [ ] Test enum value validation
- [ ] Test model field validation (min/max lengths, positive numbers)
- [ ] Test computed fields calculate correctly
- [ ] Test Create/Update schema differences
- [ ] Test conversion from SQLAlchemy models

## Common Issues

**Issue**: Validation errors when converting from SQLAlchemy
**Solution**: Use `model_config = ConfigDict(from_attributes=True)`

**Issue**: Circular imports between models
**Solution**: Use `typing.TYPE_CHECKING` and forward references

## Success Criteria

✅ All 8 Pydantic models created with validation
✅ All 8 enums defined
✅ 12-test suite passes
✅ Type hints complete
✅ Docstrings on all classes and complex methods

## Key Insights from This Story Card

1. **Complete Code Examples**: 400+ lines of production code included
2. **Step-by-Step Breakdown**: 7 sequential steps with time estimates
3. **Built-in Testing**: Test suite included, not an afterthought
4. **Common Issues**: Anticipated problems with solutions
5. **Clear Success Criteria**: Unambiguous definition of "done"

This format eliminates ambiguity and enables autonomous AI implementation within a single session.
