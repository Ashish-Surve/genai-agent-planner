"""Task Pydantic model."""

from datetime import datetime

from pydantic import Field, computed_field, field_validator

from adhd_planner.models.base import BaseAppModel, TimestampedModel
from adhd_planner.models.enums import EnergyLevel, Priority, SyncStatus, TaskStatus


class Task(TimestampedModel):
    """Task data model."""

    # Identity
    id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None

    # Time management
    estimated_duration_minutes: int = Field(gt=0, le=1440)
    actual_duration_minutes: int | None = Field(None, gt=0)
    deadline: datetime | None = None
    completed_at: datetime | None = None

    # Energy & context
    estimated_energy_level: EnergyLevel = EnergyLevel.MEDIUM
    requires_focus: bool = True
    context_category: str | None = Field(None, max_length=50)

    # Scheduling
    priority: Priority = Priority.MEDIUM
    is_recurring: bool = False
    recurrence_rule: str | None = Field(None, max_length=200)

    # Status
    status: TaskStatus = TaskStatus.NOT_STARTED

    # Sync
    sync_enabled: bool = True
    apple_reminder_id: str | None = None
    last_synced_at: datetime | None = None
    sync_status: SyncStatus = SyncStatus.PENDING

    # Metadata
    tags: list[str] = Field(default_factory=list)

    @field_validator("deadline")
    @classmethod
    def deadline_must_be_future(cls, v: datetime | None) -> datetime | None:
        """Validate that deadline is in the future."""
        if v is not None and v < datetime.utcnow():
            raise ValueError("Deadline must be in the future")
        return v

    @field_validator("tags")
    @classmethod
    def tags_must_be_unique(cls, v: list[str]) -> list[str]:
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
    def duration_accuracy(self) -> float | None:
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

    model_config = {
        **TimestampedModel.model_config,
        "json_schema_extra": {
            "example": {
                "title": "Write monthly report",
                "description": "Prepare and write the monthly status report",
                "estimated_duration_minutes": 60,
                "estimated_energy_level": "HIGH",
                "priority": "URGENT",
                "requires_focus": True,
                "context_category": "writing",
                "tags": ["work", "report"],
            }
        },
    }


class TaskCreate(BaseAppModel):
    """Schema for creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    estimated_duration_minutes: int = Field(default=30, gt=0, le=1440)
    estimated_energy_level: EnergyLevel = EnergyLevel.MEDIUM
    priority: Priority = Priority.MEDIUM
    deadline: datetime | None = None
    context_category: str | None = None
    requires_focus: bool = True
    tags: list[str] = Field(default_factory=list)
    sync_enabled: bool = True


class TaskUpdate(BaseAppModel):
    """Schema for updating a task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    estimated_duration_minutes: int | None = Field(None, gt=0, le=1440)
    estimated_energy_level: EnergyLevel | None = None
    priority: Priority | None = None
    deadline: datetime | None = None
    context_category: str | None = None
    requires_focus: bool | None = None
    status: TaskStatus | None = None
    tags: list[str] | None = None
