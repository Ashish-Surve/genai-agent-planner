"""Task repository with specialized queries."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from src.adhd_planner.utils.logger import get_logger
from src.database.schema import TaskModel
from src.repositories.base_repository import BaseRepository

logger = get_logger("task_repository")


class TaskRepository(BaseRepository[TaskModel]):
    """Repository for task-specific queries."""

    def __init__(self, session: Session):
        """Initialize task repository."""
        super().__init__(TaskModel, session)

    def find_by_status(self, status: str) -> list[TaskModel]:
        """Find all tasks with a specific status."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(self.model.status == status)
                .order_by(self.model.created_at.desc())
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks with status: {status}")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by status: {e}", exc_info=True)
            raise

    def find_by_priority(self, priority: str) -> list[TaskModel]:
        """Find all tasks with a specific priority."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(self.model.priority == priority)
                .order_by(self.model.deadline.asc())
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks with priority: {priority}")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by priority: {e}", exc_info=True)
            raise

    def find_overdue(self) -> list[TaskModel]:
        """Find all overdue tasks (past deadline, not completed)."""
        try:
            now = datetime.utcnow()

            tasks = (
                self.session.query(self.model)
                .filter(self.model.deadline < now, self.model.status != "COMPLETED")
                .order_by(self.model.deadline.asc())
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} overdue tasks")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding overdue tasks: {e}", exc_info=True)
            raise

    def find_due_soon(self, hours: int = 24) -> list[TaskModel]:
        """Find tasks due within the specified number of hours."""
        try:
            now = datetime.utcnow()
            future = now + timedelta(hours=hours)

            tasks = (
                self.session.query(self.model)
                .filter(self.model.deadline.between(now, future), self.model.status != "COMPLETED")
                .order_by(self.model.deadline.asc())
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks due within {hours} hours")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks due soon: {e}", exc_info=True)
            raise

    def find_by_energy_level(self, energy_level: str) -> list[TaskModel]:
        """Find tasks requiring a specific energy level."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(
                    self.model.estimated_energy_level == energy_level,
                    self.model.status != "COMPLETED",
                )
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks requiring {energy_level} energy")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by energy level: {e}", exc_info=True)
            raise

    def find_by_context(self, context_category: str) -> list[TaskModel]:
        """Find tasks in a specific context/category."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(self.model.context_category == context_category)
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks in context: {context_category}")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding tasks by context: {e}", exc_info=True)
            raise

    def find_with_dependencies(self) -> list[TaskModel]:
        """Find all tasks with their dependencies loaded."""
        try:
            tasks = (
                self.session.query(self.model).options(joinedload(self.model.dependencies)).all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks with dependencies loaded")
            return tasks

        except Exception as e:
            self.logger.error(f"Error loading tasks with dependencies: {e}", exc_info=True)
            raise

    def find_by_dependency(self, dependency_id: str) -> list[TaskModel]:
        """Find tasks that depend on a specific task."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(self.model.dependencies.any(id=dependency_id))
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks depending on task {dependency_id}")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding dependent tasks: {e}", exc_info=True)
            raise

    def find_requiring_focus(self) -> list[TaskModel]:
        """Find tasks that require deep focus."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(self.model.requires_focus == True, self.model.status != "COMPLETED")
                .order_by(self.model.priority.desc())
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks requiring focus")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding focus tasks: {e}", exc_info=True)
            raise

    def find_completed_with_durations(self) -> list[TaskModel]:
        """Find completed tasks that have actual durations recorded."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(
                    self.model.status == "COMPLETED", self.model.actual_duration_minutes.isnot(None)
                )
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} completed tasks with durations")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding completed tasks: {e}", exc_info=True)
            raise

    def find_pending_sync(self) -> list[TaskModel]:
        """Find tasks with pending sync operations."""
        try:
            tasks = (
                self.session.query(self.model)
                .filter(self.model.sync_enabled == True, self.model.sync_status == "PENDING")
                .all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks pending sync")
            return tasks

        except Exception as e:
            self.logger.error(f"Error finding pending sync tasks: {e}", exc_info=True)
            raise

    def search_by_title(self, query: str) -> list[TaskModel]:
        """Search tasks by title (case-insensitive partial match)."""
        try:
            tasks = (
                self.session.query(self.model).filter(self.model.title.ilike(f"%{query}%")).all()
            )

            self.logger.debug(f"Found {len(tasks)} tasks matching '{query}'")
            return tasks

        except Exception as e:
            self.logger.error(f"Error searching tasks: {e}", exc_info=True)
            raise

    def get_statistics(self) -> dict:
        """Get task statistics."""
        try:
            stats = {
                "total": self.count(),
                "not_started": self.count({"status": "NOT_STARTED"}),
                "in_progress": self.count({"status": "IN_PROGRESS"}),
                "completed": self.count({"status": "COMPLETED"}),
                "blocked": self.count({"status": "BLOCKED"}),
                "overdue": len(self.find_overdue()),
            }

            self.logger.debug(f"Task statistics: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Error getting task statistics: {e}", exc_info=True)
            raise
