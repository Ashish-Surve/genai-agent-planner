"""Database connection management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.adhd_planner.utils.config import get_settings
from src.adhd_planner.utils.logger import get_logger

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
