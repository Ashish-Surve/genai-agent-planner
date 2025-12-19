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
