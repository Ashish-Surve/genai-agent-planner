"""UserPreferences Pydantic model."""

from pydantic import Field

from adhd_planner.models.base import BaseAppModel


class EnergyTimeSlot(BaseAppModel):
    """Time slot with energy level."""

    start: str = Field(pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class UserPreferences(BaseAppModel):
    """User preferences data model."""

    id: str | None = None
    user_id: str = "default"

    # Working hours
    typical_work_start: str = Field(default="09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    typical_work_end: str = Field(default="17:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    preferred_break_duration: int = Field(default=15, gt=0, le=60)

    # Energy patterns
    peak_energy_times: list[EnergyTimeSlot] = Field(default_factory=list)
    low_energy_times: list[EnergyTimeSlot] = Field(default_factory=list)

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
    llm_provider: str = Field(default="ollama", pattern=r"^(ollama|gemini|claude|anthropic)$")
    model_name: str = Field(default="llama3.1", max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
