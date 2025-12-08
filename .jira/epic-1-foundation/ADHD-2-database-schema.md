# ADHD-2: Database Schema & Migrations

## Story Information

- **Epic**: Foundation
- **Story Points**: 3
- **Estimated Time**: 3 hours
- **Prerequisites**: ADHD-1 (Project Setup)
- **Status**: 📋 Not Started

## Description

Create the SQLAlchemy database schema for all core entities and set up Alembic for database migrations. This establishes the persistence layer for tasks, time blocks, user preferences, and all other data.

## Goals

1. Define SQLAlchemy models for all entities
2. Set up Alembic for migrations
3. Create initial migration
4. Implement database connection management
5. Create database initialization script

## Acceptance Criteria

- [ ] SQLAlchemy models defined for all entities
- [ ] Alembic configured and working
- [ ] Initial migration created
- [ ] Database can be created and initialized
- [ ] Database connection pooling configured
- [ ] All relationships and constraints defined

## Files to Create

```
src/database/connection.py        # Database connection management
src/database/schema.py             # SQLAlchemy models
src/database/migrations/alembic.ini
src/database/migrations/env.py
src/database/migrations/script.py.mako
scripts/setup_database.py          # Database initialization
```

## Implementation Steps

### Step 1: Set up Alembic (20 min)

```bash
# Initialize Alembic in database migrations folder
cd src/database
uv run alembic init migrations
cd ../..
```

Edit `src/database/migrations/alembic.ini` to set SQLite URL:
```ini
sqlalchemy.url = sqlite:///data/database/adhd_planner.db
```

### Step 2: Database Connection (30 min)

**File**: `src/database/connection.py`

```python
"""Database connection management."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger("database")


# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key support in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        """Initialize database manager."""
        self.settings = get_settings()
        self.engine = None
        self.session_factory = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Create SQLAlchemy engine."""
        db_path = self.settings.database_path

        # Create engine with connection pooling
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # Use static pool for SQLite
            echo=self.settings.debug,  # Log SQL in debug mode
        )

        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

        logger.info(f"Database engine initialized: {db_path}")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session context manager.

        Usage:
            with db.get_session() as session:
                session.query(Task).all()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def create_tables(self):
        """Create all tables (for testing, use Alembic in production)."""
        from src.database.schema import Base
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")

    def drop_tables(self):
        """Drop all tables (for testing only!)."""
        from src.database.schema import Base
        Base.metadata.drop_all(self.engine)
        logger.warning("Database tables dropped")


# Global database manager instance
_db_manager = None


def get_db() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
```

### Step 3: SQLAlchemy Schema (90 min)

**File**: `src/database/schema.py`

```python
"""SQLAlchemy ORM models for database schema."""

from datetime import datetime
from typing import List
import uuid

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer,
    String, Table, Text, Index
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


# Association table for task dependencies (many-to-many)
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', String, ForeignKey('tasks.id', ondelete='CASCADE')),
    Column('depends_on_id', String, ForeignKey('tasks.id', ondelete='CASCADE'))
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
    time_blocks = relationship("TimeBlockModel", back_populates="task", cascade="all, delete-orphan")
    sync_operations = relationship("SyncOperationModel", back_populates="task")

    # Self-referential many-to-many for dependencies
    dependencies = relationship(
        "TaskModel",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_id,
        backref="dependent_tasks"
    )

    # Indexes
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_deadline', 'deadline'),
        Index('idx_task_created_at', 'created_at'),
    )


class TimeBlockModel(Base):
    """Time block entity."""

    __tablename__ = "time_blocks"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True)

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
        Index('idx_time_block_start', 'start_time'),
        Index('idx_time_block_task', 'task_id'),
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
    __table_args__ = (
        Index('idx_energy_log_timestamp', 'timestamp'),
    )


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
    related_task_id = Column(String, ForeignKey('tasks.id'), nullable=True)


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
    task_id = Column(String, ForeignKey('tasks.id'), nullable=True)
    task = relationship("TaskModel", back_populates="sync_operations")

    # Indexes
    __table_args__ = (
        Index('idx_sync_status', 'status'),
        Index('idx_sync_created', 'created_at'),
    )
```

### Step 4: Database Initialization Script (30 min)

**File**: `scripts/setup_database.py`

```python
"""Initialize database with schema and default data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_db
from src.database.schema import Base, UserPreferencesModel
from src.utils.logger import get_logger

logger = get_logger("setup_database")


def setup_database(reset: bool = False):
    """
    Initialize database with schema and default data.

    Args:
        reset: If True, drop all tables first
    """
    db = get_db()

    if reset:
        logger.warning("Dropping all tables...")
        db.drop_tables()

    logger.info("Creating database tables...")
    db.create_tables()

    # Create default user preferences
    with db.get_session() as session:
        # Check if preferences exist
        existing = session.query(UserPreferencesModel).first()

        if not existing:
            logger.info("Creating default user preferences...")
            default_prefs = UserPreferencesModel(
                user_id="default",
                typical_work_start="09:00",
                typical_work_end="17:00",
                max_focus_duration=45,
                peak_energy_times=[
                    {"start": "09:00", "end": "12:00"}
                ],
                low_energy_times=[
                    {"start": "14:00", "end": "16:00"}
                ]
            )
            session.add(default_prefs)
            session.commit()
            logger.info("Default preferences created")
        else:
            logger.info("User preferences already exist")

    logger.info("✓ Database setup complete!")
    print(f"\n✓ Database created at: {db.settings.database_path}")
    print("✓ Tables created successfully")
    print("✓ Default preferences inserted\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Set up ADHD Planner database")
    parser.add_argument("--reset", action="store_true", help="Drop all tables first")
    args = parser.parse_args()

    setup_database(reset=args.reset)
```

## Testing Checklist

```bash
# 1. Create database
uv run python scripts/setup_database.py

# 2. Verify database file exists
ls -lh data/database/adhd_planner.db

# 3. Inspect database schema
sqlite3 data/database/adhd_planner.db ".schema"

# 4. Verify tables created
sqlite3 data/database/adhd_planner.db ".tables"

# 5. Check default preferences
sqlite3 data/database/adhd_planner.db "SELECT * FROM user_preferences;"

# 6. Test database connection in Python
uv run python -c "
from src.database.connection import get_db
db = get_db()
with db.get_session() as session:
    from src.database.schema import UserPreferencesModel
    prefs = session.query(UserPreferencesModel).first()
    print(f'User preferences found: {prefs.user_id}')
"
```

## Success Criteria

- ✅ Database file created
- ✅ All tables exist
- ✅ Foreign keys working
- ✅ Default preferences inserted
- ✅ Can query database from Python
- ✅ Alembic configured

## Next Story

**[ADHD-3: Pydantic Models & Enums](ADHD-3-pydantic-models.md)**
