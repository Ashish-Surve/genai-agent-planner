"""SQLAlchemy ORM models for database schema."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Association table for task dependencies (many-to-many)
task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column("task_id", String, ForeignKey("tasks.id", ondelete="CASCADE")),
    Column("depends_on_id", String, ForeignKey("tasks.id", ondelete="CASCADE")),
)


class TaskModel(Base):
    """Task entity."""

    __tablename__ = "tasks"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Time management
    estimated_duration_minutes = Column(Integer, nullable=False)
    actual_duration_minutes = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Energy & context
    estimated_energy_level = Column(String(10), nullable=False)  # LOW, MEDIUM, HIGH
    requires_focus = Column(Boolean, default=True)
    context_category = Column(String(50), nullable=True)

    # Scheduling
    priority = Column(String(10), nullable=False)  # URGENT, HIGH, MEDIUM, LOW
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(200), nullable=True)

    # Sync
    sync_enabled = Column(Boolean, default=True)
    apple_reminder_id = Column(String(200), nullable=True)
    last_synced_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), default="PENDING")

    # Metadata (stored as JSON in SQLite)
    tags = Column(JSON, default=list)
    status = Column(String(20), default="NOT_STARTED")

    # Relationships
    time_blocks = relationship(
        "TimeBlockModel", back_populates="task", cascade="all, delete-orphan"
    )
    sync_operations = relationship("SyncOperationModel", back_populates="task")

    # Self-referential many-to-many for dependencies
    dependencies = relationship(
        "TaskModel",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_id,
        backref="dependent_tasks",
    )

    # Indexes
    __table_args__ = (
        Index("idx_task_status", "status"),
        Index("idx_task_deadline", "deadline"),
        Index("idx_task_created_at", "created_at"),
    )


class TimeBlockModel(Base):
    """Time block entity."""

    __tablename__ = "time_blocks"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)

    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    # Type
    block_type = Column(String(10), nullable=False)  # TASK, BREAK, BUFFER, EVENT, FREE
    is_flexible = Column(Boolean, default=False)

    # Sync
    apple_calendar_event_id = Column(String(200), nullable=True)
    sync_enabled = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, nullable=True)

    # Context
    energy_level_required = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    task = relationship("TaskModel", back_populates="time_blocks")

    # Indexes
    __table_args__ = (
        Index("idx_time_block_start", "start_time"),
        Index("idx_time_block_task", "task_id"),
    )


class UserPreferencesModel(Base):
    """User preferences entity."""

    __tablename__ = "user_preferences"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, default="default")

    # Working hours (stored as strings HH:MM)
    typical_work_start = Column(String(5), default="09:00")
    typical_work_end = Column(String(5), default="17:00")
    preferred_break_duration = Column(Integer, default=15)

    # Energy patterns (stored as JSON)
    peak_energy_times = Column(JSON, default=list)
    low_energy_times = Column(JSON, default=list)

    # ADHD settings
    max_focus_duration = Column(Integer, default=45)
    context_switch_penalty = Column(Integer, default=5)
    buffer_time_between_tasks = Column(Integer, default=10)

    # Planning
    planning_horizon_days = Column(Integer, default=7)
    default_task_duration = Column(Integer, default=30)

    # Sync
    default_sync_to_reminders = Column(Boolean, default=True)
    default_sync_to_calendar = Column(Boolean, default=True)
    sync_interval_minutes = Column(Integer, default=5)

    # LLM settings
    llm_provider = Column(String(20), default="ollama")
    model_name = Column(String(100), default="llama3.1")
    temperature = Column(Float, default=0.7)


class EnergyLogModel(Base):
    """Energy log entity."""

    __tablename__ = "energy_logs"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Energy data
    reported_energy = Column(String(10), nullable=False)
    predicted_energy = Column(String(10), nullable=True)

    # Context
    tasks_completed = Column(Integer, default=0)
    context_switches = Column(Integer, default=0)
    time_since_break = Column(Integer, default=0)

    # Analysis
    energy_accuracy = Column(Float, nullable=True)

    # Indexes
    __table_args__ = (Index("idx_energy_log_timestamp", "timestamp"),)


class CalendarEventModel(Base):
    """Calendar event entity."""

    __tablename__ = "calendar_events"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Source
    source = Column(String(20), nullable=False)  # LOCAL, APPLE_CALENDAR, SYNCED
    apple_event_id = Column(String(200), nullable=True)

    # Metadata
    is_all_day = Column(Boolean, default=False)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)

    # Integration
    related_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)


class SyncOperationModel(Base):
    """Sync operation entity."""

    __tablename__ = "sync_operations"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_type = Column(String(10), nullable=False)  # CREATE, UPDATE, DELETE
    direction = Column(String(20), nullable=False)  # LOCAL_TO_APPLE, APPLE_TO_LOCAL
    entity_type = Column(String(20), nullable=False)  # TASK, TIME_BLOCK, EVENT
    entity_id = Column(String, nullable=False)

    # Status
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Relationships
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    task = relationship("TaskModel", back_populates="sync_operations")

    # Indexes
    __table_args__ = (
        Index("idx_sync_status", "status"),
        Index("idx_sync_created", "created_at"),
    )
