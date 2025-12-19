"""EnergyLog Pydantic model."""

from datetime import datetime

from pydantic import Field

from src.models.base import BaseAppModel
from src.models.enums import EnergyLevel


class EnergyLog(BaseAppModel):
    """Energy log data model."""

    id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Energy data
    reported_energy: EnergyLevel
    predicted_energy: EnergyLevel | None = None

    # Context
    tasks_completed: int = Field(default=0, ge=0)
    context_switches: int = Field(default=0, ge=0)
    time_since_break: int = Field(default=0, ge=0)

    # Analysis
    energy_accuracy: float | None = Field(None, ge=0.0, le=1.0)
