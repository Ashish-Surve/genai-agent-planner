"""Task service with business logic for task management."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from src.database.schema import TaskModel
from src.repositories.task_repository import TaskRepository
from src.adhd_planner.utils.validation import (
    validate_not_empty,
    validate_duration,
    validate_enum_value,
    ValidationError
)
from src.adhd_planner.utils.logger import get_logger
from src.adhd_planner.utils.errors import UserFacingError

logger = get_logger("task_service")


class TaskService:
    """Service for task management with business logic."""

    def __init__(self, session: Session):
        """
        Initialize task service.

        Args:
            session: Database session
        """
        self.session = session
        self.repository = TaskRepository(session)
        self.logger = logger

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        estimated_duration_minutes: int = 30,
        energy_level: str = "MEDIUM",
        priority: str = "MEDIUM",
        deadline: Optional[datetime] = None,
        context_category: Optional[str] = None,
        requires_focus: bool = True,
        tags: Optional[List[str]] = None,
        dependency_ids: Optional[List[str]] = None,
        sync_enabled: bool = True
    ) -> TaskModel:
        """
        Create a new task with validation.

        Args:
            title: Task title
            description: Optional description
            estimated_duration_minutes: Duration estimate
            energy_level: Required energy (LOW, MEDIUM, HIGH)
            priority: Task priority (URGENT, HIGH, MEDIUM, LOW)
            deadline: Optional deadline
            context_category: Task context/category
            requires_focus: Whether task requires deep focus
            tags: Optional list of tags
            dependency_ids: Optional list of task IDs this depends on
            sync_enabled: Whether to sync with Apple Reminders

        Returns:
            Created task

        Raises:
            ValidationError: If validation fails
            UserFacingError: If business rule violation
        """
        # Validate inputs
        title = validate_not_empty(title, "title")
        estimated_duration_minutes = validate_duration(
            estimated_duration_minutes,
            "estimated_duration"
        )
        energy_level = validate_enum_value(
            energy_level,
            ["LOW", "MEDIUM", "HIGH"],
            "energy_level"
        )
        priority = validate_enum_value(
            priority,
            ["URGENT", "HIGH", "MEDIUM", "LOW"],
            "priority"
        )

        # Validate deadline if provided
        if deadline and deadline < datetime.utcnow():
            raise ValidationError(
                "Deadline cannot be in the past",
                field="deadline"
            )

        # Check dependencies exist and prevent cycles
        if dependency_ids:
            for dep_id in dependency_ids:
                dep_task = self.repository.get_by_id(dep_id)
                if not dep_task:
                    raise UserFacingError(
                        f"Dependency task not found: {dep_id}",
                        technical_message=f"Task {dep_id} does not exist"
                    )

        # Create task
        task_data = {
            "title": title,
            "description": description,
            "estimated_duration_minutes": estimated_duration_minutes,
            "estimated_energy_level": energy_level,
            "priority": priority,
            "deadline": deadline,
            "context_category": context_category,
            "requires_focus": requires_focus,
            "tags": tags or [],
            "sync_enabled": sync_enabled,
            "status": "NOT_STARTED"
        }

        task = self.repository.create(task_data)

        # Add dependencies
        if dependency_ids:
            for dep_id in dependency_ids:
                dep_task = self.repository.get_by_id(dep_id)
                task.dependencies.append(dep_task)
            self.session.commit()

        self.logger.info(f"Created task: {task.id} - {task.title}")
        return task

    def update_task(
        self,
        task_id: str,
        **updates
    ) -> TaskModel:
        """
        Update a task.

        Args:
            task_id: Task ID
            **updates: Fields to update

        Returns:
            Updated task

        Raises:
            UserFacingError: If task not found or update invalid
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            raise UserFacingError(
                "Task not found",
                technical_message=f"Task {task_id} does not exist"
            )

        # Validate updates
        if "title" in updates:
            updates["title"] = validate_not_empty(updates["title"], "title")

        if "estimated_duration_minutes" in updates:
            updates["estimated_duration_minutes"] = validate_duration(
                updates["estimated_duration_minutes"],
                "estimated_duration"
            )

        if "energy_level" in updates:
            updates["estimated_energy_level"] = validate_enum_value(
                updates["energy_level"],
                ["LOW", "MEDIUM", "HIGH"],
                "energy_level"
            )
            del updates["energy_level"]

        if "priority" in updates:
            updates["priority"] = validate_enum_value(
                updates["priority"],
                ["URGENT", "HIGH", "MEDIUM", "LOW"],
                "priority"
            )

        # Update task
        updated_task = self.repository.update(task_id, updates)

        self.logger.info(f"Updated task: {task_id}")
        return updated_task

    def start_task(self, task_id: str) -> TaskModel:
        """
        Start a task (transition to IN_PROGRESS).

        Args:
            task_id: Task ID

        Returns:
            Updated task

        Raises:
            UserFacingError: If task not found or invalid transition
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            raise UserFacingError("Task not found")

        # Check current status
        if task.status == "COMPLETED":
            raise UserFacingError(
                "Cannot start a completed task",
                technical_message=f"Task {task_id} is already completed"
            )

        if task.status == "IN_PROGRESS":
            self.logger.warning(f"Task {task_id} already in progress")
            return task

        # Check dependencies
        if not self._dependencies_satisfied(task):
            raise UserFacingError(
                "Cannot start task: dependencies not completed",
                technical_message=f"Task {task_id} has incomplete dependencies"
            )

        # Update status
        updated = self.repository.update(task_id, {
            "status": "IN_PROGRESS"
        })

        self.logger.info(f"Started task: {task_id}")
        return updated

    def complete_task(
        self,
        task_id: str,
        actual_duration_minutes: Optional[int] = None
    ) -> TaskModel:
        """
        Complete a task.

        Args:
            task_id: Task ID
            actual_duration_minutes: Optional actual duration for learning

        Returns:
            Updated task

        Raises:
            UserFacingError: If task not found
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            raise UserFacingError("Task not found")

        if task.status == "COMPLETED":
            self.logger.warning(f"Task {task_id} already completed")
            return task

        # Update task
        updates = {
            "status": "COMPLETED",
            "completed_at": datetime.utcnow()
        }

        if actual_duration_minutes:
            validate_duration(actual_duration_minutes, "actual_duration")
            updates["actual_duration_minutes"] = actual_duration_minutes

        updated = self.repository.update(task_id, updates)

        self.logger.info(
            f"Completed task: {task_id} "
            f"(estimated: {task.estimated_duration_minutes}m, "
            f"actual: {actual_duration_minutes or 'not recorded'}m)"
        )

        return updated

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task.

        Args:
            task_id: Task ID

        Raises:
            UserFacingError: If task not found or has dependents
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            raise UserFacingError("Task not found")

        # Check if other tasks depend on this one
        dependent_tasks = self.repository.find_by_dependency(task_id)
        if dependent_tasks:
            titles = [t.title for t in dependent_tasks[:3]]
            raise UserFacingError(
                f"Cannot delete task: {len(dependent_tasks)} tasks depend on it. "
                f"Examples: {', '.join(titles)}",
                technical_message=f"Task {task_id} has {len(dependent_tasks)} dependents"
            )

        self.repository.delete(task_id)
        self.logger.info(f"Deleted task: {task_id}")

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        return self.repository.get_by_id(task_id)

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        context_category: Optional[str] = None,
        tag: Optional[str] = None,
        overdue_only: bool = False,
        limit: Optional[int] = None
    ) -> List[TaskModel]:
        """
        List tasks with filtering.

        Args:
            status: Filter by status
            priority: Filter by priority
            context_category: Filter by context
            tag: Filter by tag
            overdue_only: Only show overdue tasks
            limit: Maximum number of tasks

        Returns:
            List of matching tasks
        """
        filters = {}

        if status:
            status = validate_enum_value(
                status,
                ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED"],
                "status"
            )
            filters["status"] = status

        if priority:
            priority = validate_enum_value(
                priority,
                ["URGENT", "HIGH", "MEDIUM", "LOW"],
                "priority"
            )
            filters["priority"] = priority

        if context_category:
            filters["context_category"] = context_category

        tasks = self.repository.find_by_filters(filters)

        # Additional filtering
        if tag:
            tasks = [t for t in tasks if tag in (t.tags or [])]

        if overdue_only:
            now = datetime.utcnow()
            tasks = [
                t for t in tasks
                if t.deadline and t.deadline < now and t.status != "COMPLETED"
            ]

        # Limit
        if limit:
            tasks = tasks[:limit]

        return tasks

    def get_tasks_by_status(self, status: str) -> List[TaskModel]:
        """
        Get all tasks with a specific status.

        Args:
            status: Task status to filter by

        Returns:
            List of matching tasks
        """
        status = validate_enum_value(
            status,
            ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED"],
            "status"
        )
        return self.repository.find_by_status(status)

    def get_overdue_tasks(self) -> List[TaskModel]:
        """
        Get all overdue tasks.

        Returns:
            List of overdue tasks
        """
        return self.repository.find_overdue()

    def get_tasks_ready_to_start(self) -> List[TaskModel]:
        """
        Get tasks that are ready to start (no blocking dependencies).

        Returns:
            List of tasks ready to start
        """
        not_started = self.repository.find_by_status("NOT_STARTED")
        ready_tasks = [
            task for task in not_started
            if self._dependencies_satisfied(task)
        ]
        return ready_tasks

    def _dependencies_satisfied(self, task: TaskModel) -> bool:
        """
        Check if all task dependencies are satisfied.

        Args:
            task: Task to check

        Returns:
            True if all dependencies completed
        """
        if not task.dependencies:
            return True

        for dep in task.dependencies:
            if dep.status != "COMPLETED":
                return False

        return True

    def _would_create_cycle(
        self,
        task_id: str,
        new_dependency_ids: List[str]
    ) -> bool:
        """
        Check if adding dependencies would create a cycle.

        Args:
            task_id: Task that would have dependencies added
            new_dependency_ids: Dependency IDs to add

        Returns:
            True if cycle would be created
        """
        for dep_id in new_dependency_ids:
            if self._depends_on_transitively(dep_id, task_id):
                return True
        return False

    def _depends_on_transitively(
        self,
        task_id: str,
        target_id: str,
        visited: Optional[set] = None
    ) -> bool:
        """
        Check if task transitively depends on target.

        Args:
            task_id: Task to check
            target_id: Target task
            visited: Set of visited task IDs (for cycle detection)

        Returns:
            True if task depends on target
        """
        if visited is None:
            visited = set()

        if task_id in visited:
            return False

        visited.add(task_id)

        task = self.repository.get_by_id(task_id)
        if not task or not task.dependencies:
            return False

        for dep in task.dependencies:
            if dep.id == target_id:
                return True
            if self._depends_on_transitively(dep.id, target_id, visited):
                return True

        return False
