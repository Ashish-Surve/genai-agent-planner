"""CalendarEvent Pydantic model."""

from datetime import datetime

from pydantic import Field

from src.models.base import BaseAppModel
from src.models.enums import EventSource


class CalendarEvent(BaseAppModel):
    """Calendar event data model."""

    id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime

    # Source
    source: EventSource = EventSource.LOCAL
    apple_event_id: str | None = None

    # Metadata
    is_all_day: bool = False
    location: str | None = Field(None, max_length=200)
    notes: str | None = None

    # Integration
    related_task_id: str | None = None
