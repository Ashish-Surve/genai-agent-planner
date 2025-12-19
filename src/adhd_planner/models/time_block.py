"""TimeBlock Pydantic model."""

from datetime import datetime

from pydantic import Field, computed_field, field_validator

from src.models.base import BaseAppModel
from src.models.enums import BlockType, EnergyLevel


class TimeBlock(BaseAppModel):
    """Time block data model."""

    # Identity
    id: str | None = None
    task_id: str | None = None

    # Timing
    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(gt=0)

    # Type
    block_type: BlockType = BlockType.TASK
    is_flexible: bool = False

    # Sync
    apple_calendar_event_id: str | None = None
    sync_enabled: bool = True
    last_synced_at: datetime | None = None

    # Context
    energy_level_required: EnergyLevel | None = None
    notes: str | None = None

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        """Validate that end_time is after start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
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

    model_config = {
        **BaseAppModel.model_config,
        "json_schema_extra": {
            "example": {
                "start_time": "2025-01-01T09:00:00",
                "end_time": "2025-01-01T10:00:00",
                "duration_minutes": 60,
                "block_type": "TASK",
                "energy_level_required": "HIGH",
            }
        },
    }


class TimeBlockCreate(BaseAppModel):
    """Schema for creating a time block."""

    start_time: datetime
    end_time: datetime
    block_type: BlockType = BlockType.TASK
    task_id: str | None = None
    is_flexible: bool = False
    energy_level_required: EnergyLevel | None = None
    notes: str | None = None
    sync_enabled: bool = True


class TimeBlockUpdate(BaseAppModel):
    """Schema for updating a time block."""

    start_time: datetime | None = None
    end_time: datetime | None = None
    block_type: BlockType | None = None
    is_flexible: bool | None = None
    energy_level_required: EnergyLevel | None = None
    notes: str | None = None
