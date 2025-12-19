"""SyncOperation Pydantic model."""

from datetime import datetime

from pydantic import Field

from src.models.base import TimestampedModel
from src.models.enums import SyncDirection, SyncOperationType, SyncStatus


class SyncOperation(TimestampedModel):
    """Sync operation data model."""

    id: str | None = None
    operation_type: SyncOperationType
    direction: SyncDirection
    entity_type: str = Field(max_length=20)
    entity_id: str

    # Status
    status: SyncStatus = SyncStatus.PENDING
    completed_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = Field(default=0, ge=0)

    # Relationships
    task_id: str | None = None
