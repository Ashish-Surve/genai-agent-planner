"""Initialize database with schema and default data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_db
from src.database.schema import Base, UserPreferencesModel
from src.adhd_planner.utils.logger import get_logger

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
