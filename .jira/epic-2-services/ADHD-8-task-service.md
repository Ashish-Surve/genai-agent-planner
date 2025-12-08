# ADHD-8: Task Service

## Story Information

- **Epic**: Core Services
- **Story Points**: 3
- **Estimated Time**: 3 hours
- **Prerequisites**: ADHD-3 (Pydantic Models), ADHD-5 (Task Repository), ADHD-6 (Validation Utils)
- **Status**: 📋 Not Started

## Description

Implement the Task Service layer that provides high-level business logic for task management. This service handles task CRUD operations, status transitions, dependency management, recurrence rules, and enforces business rules for ADHD-friendly task management.

## Goals

1. Implement task CRUD operations with validation
2. Handle task status transitions with business rules
3. Implement dependency checking and validation
4. Support recurring task creation
5. Add task filtering and search capabilities
6. Implement task completion workflow
7. Add task update with change tracking

## Acceptance Criteria

- [ ] All CRUD operations work correctly
- [ ] Status transitions follow business rules
- [ ] Dependencies are validated and enforced
- [ ] Recurring tasks can be created and managed
- [ ] Tasks can be filtered by multiple criteria
- [ ] Task completion updates related entities
- [ ] All operations are logged
- [ ] Unit tests pass for all operations

## Files to Create

```
src/services/task_service.py           # Main task service
tests/unit/test_task_service.py        # Service tests
```

## Implementation Steps

### Step 1: Task Service Core (45 min)

**File**: `src/services/task_service.py`

```python
"""Task service with business logic."""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.task import Task, TaskStatus, Priority, EnergyLevel
from src.repositories.task_repository import TaskRepository
from src.utils.validation import (
    validate_not_empty,
    validate_duration,
    validate_enum_value,
    ValidationError
)
from src.utils.logger import get_logger
from src.utils.errors import UserFacingError

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
    ) -> Task:
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

        # Check dependencies exist
        if dependency_ids:
            for dep_id in dependency_ids:
                dep_task = self.repository.get_by_id(dep_id)
                if not dep_task:
                    raise UserFacingError(
                        f"Dependency task not found: {dep_id}",
                        technical_message=f"Task {dep_id} does not exist"
                    )

                # Check for circular dependencies
                if self._would_create_cycle(dep_id, dependency_ids):
                    raise UserFacingError(
                        "Cannot create circular task dependencies",
                        technical_message=f"Circular dependency detected with {dep_id}"
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
            "status": TaskStatus.NOT_STARTED.value
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
    ) -> Task:
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
            del updates["energy_level"]  # Use correct field name

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

    def start_task(self, task_id: str) -> Task:
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
        if task.status == TaskStatus.COMPLETED.value:
            raise UserFacingError(
                "Cannot start a completed task",
                technical_message=f"Task {task_id} is already completed"
            )

        if task.status == TaskStatus.IN_PROGRESS.value:
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
            "status": TaskStatus.IN_PROGRESS.value
        })

        self.logger.info(f"Started task: {task_id}")
        return updated

    def complete_task(
        self,
        task_id: str,
        actual_duration_minutes: Optional[int] = None
    ) -> Task:
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

        if task.status == TaskStatus.COMPLETED.value:
            self.logger.warning(f"Task {task_id} already completed")
            return task

        # Update task
        updates = {
            "status": TaskStatus.COMPLETED.value,
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
            UserFacingError: If task not found
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

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.repository.get_by_id(task_id)

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        context_category: Optional[str] = None,
        tag: Optional[str] = None,
        overdue_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Task]:
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
                if t.deadline and t.deadline < now and t.status != TaskStatus.COMPLETED.value
            ]

        # Limit
        if limit:
            tasks = tasks[:limit]

        return tasks

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get all tasks with a specific status."""
        status = validate_enum_value(
            status,
            ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED"],
            "status"
        )
        return self.repository.find_by_status(status)

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return self.repository.find_overdue()

    def get_tasks_ready_to_start(self) -> List[Task]:
        """
        Get tasks that are ready to start (no blocking dependencies).

        Returns:
            List of tasks ready to start
        """
        not_started = self.repository.find_by_status(TaskStatus.NOT_STARTED.value)
        ready_tasks = [
            task for task in not_started
            if self._dependencies_satisfied(task)
        ]
        return ready_tasks

    def _dependencies_satisfied(self, task: Task) -> bool:
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
            if dep.status != TaskStatus.COMPLETED.value:
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
        # Simple cycle detection: check if any new dependency
        # already depends on the current task (directly or transitively)
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
            return False  # Already checked

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
```

### Step 2: Unit Tests (60 min)

**File**: `tests/unit/test_task_service.py`

```python
"""Test task service."""

import pytest
from datetime import datetime, timedelta
from src.services.task_service import TaskService
from src.models.task import TaskStatus
from src.utils.validation import ValidationError
from src.utils.errors import UserFacingError


@pytest.fixture
def task_service(test_db_session):
    """Create task service with test database."""
    return TaskService(test_db_session)


def test_create_task_success(task_service):
    """Test successful task creation."""
    task = task_service.create_task(
        title="Test task",
        description="Test description",
        estimated_duration_minutes=60,
        energy_level="HIGH",
        priority="URGENT"
    )

    assert task.id is not None
    assert task.title == "Test task"
    assert task.estimated_duration_minutes == 60
    assert task.estimated_energy_level == "HIGH"
    assert task.priority == "URGENT"
    assert task.status == TaskStatus.NOT_STARTED.value


def test_create_task_validation_errors(task_service):
    """Test task creation validation."""
    # Empty title
    with pytest.raises(ValidationError, match="cannot be empty"):
        task_service.create_task(title="")

    # Invalid duration
    with pytest.raises(ValidationError, match="must be positive"):
        task_service.create_task(title="Test", estimated_duration_minutes=0)

    # Invalid energy level
    with pytest.raises(ValidationError, match="must be one of"):
        task_service.create_task(title="Test", energy_level="INVALID")


def test_create_task_with_past_deadline(task_service):
    """Test that past deadlines are rejected."""
    past_deadline = datetime.utcnow() - timedelta(days=1)

    with pytest.raises(ValidationError, match="cannot be in the past"):
        task_service.create_task(
            title="Test",
            deadline=past_deadline
        )


def test_start_task(task_service):
    """Test starting a task."""
    task = task_service.create_task(title="Test task")

    assert task.status == TaskStatus.NOT_STARTED.value

    started = task_service.start_task(task.id)

    assert started.status == TaskStatus.IN_PROGRESS.value


def test_start_completed_task_fails(task_service):
    """Test that completed tasks cannot be started."""
    task = task_service.create_task(title="Test task")
    task_service.complete_task(task.id)

    with pytest.raises(UserFacingError, match="Cannot start a completed task"):
        task_service.start_task(task.id)


def test_complete_task(task_service):
    """Test completing a task."""
    task = task_service.create_task(title="Test task")
    task_service.start_task(task.id)

    completed = task_service.complete_task(task.id, actual_duration_minutes=45)

    assert completed.status == TaskStatus.COMPLETED.value
    assert completed.completed_at is not None
    assert completed.actual_duration_minutes == 45


def test_update_task(task_service):
    """Test updating a task."""
    task = task_service.create_task(title="Original title")

    updated = task_service.update_task(
        task.id,
        title="Updated title",
        priority="HIGH"
    )

    assert updated.title == "Updated title"
    assert updated.priority == "HIGH"


def test_delete_task(task_service):
    """Test deleting a task."""
    task = task_service.create_task(title="Test task")

    task_service.delete_task(task.id)

    # Task should no longer exist
    assert task_service.get_task(task.id) is None


def test_delete_task_with_dependents_fails(task_service):
    """Test that tasks with dependents cannot be deleted."""
    task1 = task_service.create_task(title="Task 1")
    task2 = task_service.create_task(
        title="Task 2",
        dependency_ids=[task1.id]
    )

    with pytest.raises(UserFacingError, match="tasks depend on it"):
        task_service.delete_task(task1.id)


def test_list_tasks_with_filters(task_service):
    """Test listing tasks with filters."""
    # Create tasks with different attributes
    task_service.create_task(title="Urgent task", priority="URGENT")
    task_service.create_task(title="High task", priority="HIGH")
    task_service.create_task(title="Low task", priority="LOW")

    # Filter by priority
    urgent_tasks = task_service.list_tasks(priority="URGENT")
    assert len(urgent_tasks) == 1
    assert urgent_tasks[0].title == "Urgent task"

    # Filter by status
    not_started = task_service.list_tasks(status="NOT_STARTED")
    assert len(not_started) == 3


def test_get_overdue_tasks(task_service):
    """Test getting overdue tasks."""
    # Create task with past deadline
    past_deadline = datetime.utcnow() - timedelta(days=1)
    task_service.create_task(title="Overdue task", deadline=past_deadline)

    # Create task with future deadline
    future_deadline = datetime.utcnow() + timedelta(days=1)
    task_service.create_task(title="Future task", deadline=future_deadline)

    overdue = task_service.get_overdue_tasks()
    assert len(overdue) == 1
    assert overdue[0].title == "Overdue task"


def test_dependencies_satisfied(task_service):
    """Test dependency checking."""
    task1 = task_service.create_task(title="Task 1")
    task2 = task_service.create_task(
        title="Task 2",
        dependency_ids=[task1.id]
    )

    # Task 2 should not be ready (dependency not completed)
    ready_tasks = task_service.get_tasks_ready_to_start()
    assert task1.id in [t.id for t in ready_tasks]
    assert task2.id not in [t.id for t in ready_tasks]

    # Complete task 1
    task_service.complete_task(task1.id)

    # Now task 2 should be ready
    ready_tasks = task_service.get_tasks_ready_to_start()
    assert task2.id in [t.id for t in ready_tasks]


def test_circular_dependency_prevention(task_service):
    """Test that circular dependencies are prevented."""
    task1 = task_service.create_task(title="Task 1")
    task2 = task_service.create_task(
        title="Task 2",
        dependency_ids=[task1.id]
    )

    # Try to make task1 depend on task2 (would create cycle)
    with pytest.raises(UserFacingError, match="circular"):
        task_service.update_task(task1.id, dependency_ids=[task2.id])
```

### Step 3: Conftest Updates (15 min)

**File**: `tests/conftest.py` (add to existing)

```python
# Add these fixtures to existing conftest.py

@pytest.fixture
def test_db_session(tmp_path):
    """Create test database session."""
    from src.database.connection import DatabaseManager
    from src.database.schema import Base

    db_path = tmp_path / "test.db"

    # Create test database
    db_manager = DatabaseManager()
    db_manager.settings.database_path = str(db_path)
    db_manager._initialize_engine()
    db_manager.create_tables()

    # Yield session
    with db_manager.get_session() as session:
        yield session

    # Cleanup
    db_manager.drop_tables()
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_task_service.py -v

# 2. Test task creation
uv run python -c "
from src.database.connection import get_db
from src.services.task_service import TaskService

db = get_db()
with db.get_session() as session:
    service = TaskService(session)
    task = service.create_task(
        title='Test task',
        estimated_duration_minutes=30,
        priority='HIGH'
    )
    print(f'Created task: {task.id} - {task.title}')
"

# 3. Test task lifecycle
uv run python -c "
from src.database.connection import get_db
from src.services.task_service import TaskService

db = get_db()
with db.get_session() as session:
    service = TaskService(session)

    # Create
    task = service.create_task(title='Lifecycle test')
    print(f'Created: {task.status}')

    # Start
    task = service.start_task(task.id)
    print(f'Started: {task.status}')

    # Complete
    task = service.complete_task(task.id, actual_duration_minutes=25)
    print(f'Completed: {task.status}')
"

# 4. Run all tests
uv run pytest tests/unit/ -v

# 5. Code quality
uv run ruff check src/services/task_service.py
uv run black --check src/services/
```

## Success Criteria

- ✅ All CRUD operations work
- ✅ Status transitions follow rules
- ✅ Dependencies validated
- ✅ Circular dependencies prevented
- ✅ All unit tests pass
- ✅ Business rules enforced
- ✅ Error messages are user-friendly

## Common Issues & Solutions

### Issue: Dependency checking too slow
**Solution**: Add database indexes on foreign keys, consider caching

### Issue: Circular dependency detection misses edge cases
**Solution**: Use visited set to handle complex dependency graphs

### Issue: Tasks not appearing in filters
**Solution**: Check enum value uppercase conversion, verify database query

## Next Story

Once this story is complete, move to:
**[ADHD-9: Calendar Service](ADHD-9-calendar-service.md)**

## Notes

- Task service is the heart of the application - thorough testing is critical
- Business rules should be easy to modify - keep them in one place
- Dependency tracking enables smart scheduling
- Actual duration tracking enables ML-based time estimation
- Always provide user-friendly error messages for ADHD users