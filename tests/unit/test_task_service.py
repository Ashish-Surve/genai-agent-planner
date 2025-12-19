"""Test task service."""

from datetime import datetime, timedelta

import pytest

from adhd_planner.services.task_service import TaskService
from adhd_planner.utils.errors import UserFacingError
from adhd_planner.utils.validation import ValidationError


@pytest.fixture
def task_service(test_db_session):
    """Create task service with test database."""
    return TaskService(test_db_session)


class TestCreateTask:
    """Tests for task creation."""

    def test_create_task_success(self, task_service):
        """Test successful task creation."""
        task = task_service.create_task(
            title="Test task",
            description="Test description",
            estimated_duration_minutes=60,
            energy_level="HIGH",
            priority="URGENT",
        )

        assert task.id is not None
        assert task.title == "Test task"
        assert task.description == "Test description"
        assert task.estimated_duration_minutes == 60
        assert task.estimated_energy_level == "HIGH"
        assert task.priority == "URGENT"
        assert task.status == "NOT_STARTED"

    def test_create_task_with_defaults(self, task_service):
        """Test task creation with default values."""
        task = task_service.create_task(title="Simple task")

        assert task.title == "Simple task"
        assert task.estimated_duration_minutes == 30
        assert task.estimated_energy_level == "MEDIUM"
        assert task.priority == "MEDIUM"
        assert task.status == "NOT_STARTED"

    def test_create_task_empty_title(self, task_service):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="")

    def test_create_task_whitespace_title(self, task_service):
        """Test that whitespace-only title is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="   ")

    def test_create_task_invalid_duration(self, task_service):
        """Test that invalid duration is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="Test", estimated_duration_minutes=0)

    def test_create_task_negative_duration(self, task_service):
        """Test that negative duration is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="Test", estimated_duration_minutes=-10)

    def test_create_task_invalid_energy_level(self, task_service):
        """Test that invalid energy level is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="Test", energy_level="INVALID")

    def test_create_task_invalid_priority(self, task_service):
        """Test that invalid priority is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="Test", priority="CRITICAL")

    def test_create_task_past_deadline(self, task_service):
        """Test that past deadline is rejected."""
        past_deadline = datetime.utcnow() - timedelta(days=1)

        with pytest.raises(ValidationError):
            task_service.create_task(title="Test", deadline=past_deadline)

    def test_create_task_future_deadline(self, task_service):
        """Test that future deadline is accepted."""
        future_deadline = datetime.utcnow() + timedelta(days=1)

        task = task_service.create_task(title="Test", deadline=future_deadline)

        assert task.deadline == future_deadline

    def test_create_task_with_tags(self, task_service):
        """Test task creation with tags."""
        task = task_service.create_task(title="Test", tags=["work", "urgent"])

        assert task.tags == ["work", "urgent"]


class TestTaskDependencies:
    """Tests for task dependencies."""

    def test_create_task_with_dependencies(self, task_service):
        """Test creating task with dependencies."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        assert len(task2.dependencies) == 1
        assert task2.dependencies[0].id == task1.id

    def test_create_task_with_nonexistent_dependency(self, task_service):
        """Test that nonexistent dependency is rejected."""
        with pytest.raises(UserFacingError, match="does not exist"):
            task_service.create_task(title="Test", dependency_ids=["nonexistent-id"])

    def test_dependencies_satisfied_no_deps(self, task_service):
        """Test that task with no dependencies is ready."""
        task = task_service.create_task(title="Task without deps")

        ready_tasks = task_service.get_tasks_ready_to_start()

        assert task.id in [t.id for t in ready_tasks]

    def test_dependencies_satisfied_incomplete_deps(self, task_service):
        """Test that task with incomplete dependencies is not ready."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        ready_tasks = task_service.get_tasks_ready_to_start()

        assert task1.id in [t.id for t in ready_tasks]
        assert task2.id not in [t.id for t in ready_tasks]

    def test_dependencies_satisfied_completed_deps(self, task_service):
        """Test that task with completed dependencies is ready."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        task_service.complete_task(task1.id)

        ready_tasks = task_service.get_tasks_ready_to_start()

        assert task2.id in [t.id for t in ready_tasks]

    def test_cannot_start_task_with_incomplete_dependencies(self, task_service):
        """Test that task with incomplete dependencies cannot be started."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        with pytest.raises(UserFacingError, match="dependencies"):
            task_service.start_task(task2.id)

    def test_can_start_task_with_completed_dependencies(self, task_service):
        """Test that task can be started once dependencies are completed."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        task_service.complete_task(task1.id)
        started = task_service.start_task(task2.id)

        assert started.status == "IN_PROGRESS"


class TestTaskStatusTransitions:
    """Tests for task status transitions."""

    def test_start_task_not_started(self, task_service):
        """Test starting a NOT_STARTED task."""
        task = task_service.create_task(title="Test task")

        assert task.status == "NOT_STARTED"

        started = task_service.start_task(task.id)

        assert started.status == "IN_PROGRESS"

    def test_start_task_already_in_progress(self, task_service):
        """Test starting an already IN_PROGRESS task."""
        task = task_service.create_task(title="Test task")
        task_service.start_task(task.id)

        started = task_service.start_task(task.id)

        assert started.status == "IN_PROGRESS"

    def test_cannot_start_completed_task(self, task_service):
        """Test that completed tasks cannot be started."""
        task = task_service.create_task(title="Test task")
        task_service.start_task(task.id)
        task_service.complete_task(task.id)

        with pytest.raises(UserFacingError, match="completed"):
            task_service.start_task(task.id)

    def test_complete_task(self, task_service):
        """Test completing a task."""
        task = task_service.create_task(title="Test task")
        task_service.start_task(task.id)

        completed = task_service.complete_task(task.id, actual_duration_minutes=45)

        assert completed.status == "COMPLETED"
        assert completed.completed_at is not None
        assert completed.actual_duration_minutes == 45

    def test_complete_task_without_actual_duration(self, task_service):
        """Test completing a task without recording actual duration."""
        task = task_service.create_task(title="Test task")
        task_service.start_task(task.id)

        completed = task_service.complete_task(task.id)

        assert completed.status == "COMPLETED"
        assert completed.completed_at is not None
        assert completed.actual_duration_minutes is None

    def test_complete_already_completed_task(self, task_service):
        """Test completing an already completed task."""
        task = task_service.create_task(title="Test task")
        task_service.start_task(task.id)
        task_service.complete_task(task.id)

        completed = task_service.complete_task(task.id)

        assert completed.status == "COMPLETED"


class TestUpdateTask:
    """Tests for task updates."""

    def test_update_task_title(self, task_service):
        """Test updating task title."""
        task = task_service.create_task(title="Original title")

        updated = task_service.update_task(task.id, title="Updated title")

        assert updated.title == "Updated title"

    def test_update_task_priority(self, task_service):
        """Test updating task priority."""
        task = task_service.create_task(title="Test", priority="LOW")

        updated = task_service.update_task(task.id, priority="HIGH")

        assert updated.priority == "HIGH"

    def test_update_task_duration(self, task_service):
        """Test updating task duration."""
        task = task_service.create_task(title="Test", estimated_duration_minutes=30)

        updated = task_service.update_task(task.id, estimated_duration_minutes=60)

        assert updated.estimated_duration_minutes == 60

    def test_update_task_energy_level(self, task_service):
        """Test updating task energy level."""
        task = task_service.create_task(title="Test", energy_level="LOW")

        updated = task_service.update_task(task.id, energy_level="HIGH")

        assert updated.estimated_energy_level == "HIGH"

    def test_update_nonexistent_task(self, task_service):
        """Test updating a nonexistent task."""
        with pytest.raises(UserFacingError, match="does not exist"):
            task_service.update_task("nonexistent-id", title="Updated")

    def test_update_task_with_invalid_priority(self, task_service):
        """Test that invalid priority update is rejected."""
        task = task_service.create_task(title="Test")

        with pytest.raises(ValidationError):
            task_service.update_task(task.id, priority="INVALID")


class TestDeleteTask:
    """Tests for task deletion."""

    def test_delete_task(self, task_service):
        """Test deleting a task."""
        task = task_service.create_task(title="Test task")

        task_service.delete_task(task.id)

        assert task_service.get_task(task.id) is None

    def test_delete_nonexistent_task(self, task_service):
        """Test deleting a nonexistent task."""
        with pytest.raises(UserFacingError, match="Task not found"):
            task_service.delete_task("nonexistent-id")

    def test_cannot_delete_task_with_dependents(self, task_service):
        """Test that tasks with dependents cannot be deleted."""
        task1 = task_service.create_task(title="Task 1")
        task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        with pytest.raises(UserFacingError, match="dependents"):
            task_service.delete_task(task1.id)

    def test_can_delete_task_after_dependents_removed(self, task_service):
        """Test that task can be deleted after removing dependents."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        task_service.delete_task(task2.id)
        task_service.delete_task(task1.id)

        assert task_service.get_task(task1.id) is None


class TestTaskFiltering:
    """Tests for task filtering and listing."""

    def test_list_tasks_filter_by_status(self, task_service):
        """Test filtering tasks by status."""
        task_service.create_task(title="Task 1", priority="URGENT")
        task_service.create_task(title="Task 2", priority="HIGH")
        task_service.create_task(title="Task 3", priority="LOW")

        not_started = task_service.list_tasks(status="NOT_STARTED")

        assert len(not_started) == 3

    def test_list_tasks_filter_by_priority(self, task_service):
        """Test filtering tasks by priority."""
        task_service.create_task(title="Urgent task", priority="URGENT")
        task_service.create_task(title="High task", priority="HIGH")
        task_service.create_task(title="Low task", priority="LOW")

        urgent_tasks = task_service.list_tasks(priority="URGENT")

        assert len(urgent_tasks) == 1
        assert urgent_tasks[0].title == "Urgent task"

    def test_list_tasks_filter_by_context(self, task_service):
        """Test filtering tasks by context."""
        task_service.create_task(title="Work task", context_category="work")
        task_service.create_task(title="Personal task", context_category="personal")

        work_tasks = task_service.list_tasks(context_category="work")

        assert len(work_tasks) == 1
        assert work_tasks[0].title == "Work task"

    def test_list_tasks_filter_by_tag(self, task_service):
        """Test filtering tasks by tag."""
        task_service.create_task(title="Task 1", tags=["urgent", "work"])
        task_service.create_task(title="Task 2", tags=["personal"])
        task_service.create_task(title="Task 3", tags=["urgent", "personal"])

        urgent_tasks = task_service.list_tasks(tag="urgent")

        assert len(urgent_tasks) == 2

    def test_list_tasks_overdue_only(self, task_service):
        """Test filtering for overdue tasks."""
        future = datetime.utcnow() + timedelta(days=1)

        task_service.create_task(title="Future task", deadline=future)
        task_service.create_task(title="No deadline")

        # Test that the method returns a list
        overdue = task_service.list_tasks(overdue_only=True)

        assert isinstance(overdue, list)
        # Since we can only create tasks with future deadlines, list should be empty
        assert len(overdue) == 0

    def test_list_tasks_with_limit(self, task_service):
        """Test limiting number of returned tasks."""
        task_service.create_task(title="Task 1")
        task_service.create_task(title="Task 2")
        task_service.create_task(title="Task 3")

        tasks = task_service.list_tasks(limit=2)

        assert len(tasks) <= 2

    def test_get_tasks_by_status(self, task_service):
        """Test getting tasks by specific status."""
        task_service.create_task(title="Task 1")
        task_service.create_task(title="Task 2")

        not_started = task_service.get_tasks_by_status("NOT_STARTED")

        assert len(not_started) == 2

    def test_get_overdue_tasks(self, task_service):
        """Test getting overdue tasks."""
        future = datetime.utcnow() + timedelta(days=1)

        task_service.create_task(title="Future", deadline=future)
        task_service.create_task(title="No deadline")

        overdue = task_service.get_overdue_tasks()

        # Should return a list
        assert isinstance(overdue, list)
        # Since we only created tasks with future deadlines, should be empty
        assert len(overdue) == 0

    def test_get_tasks_ready_to_start(self, task_service):
        """Test getting tasks ready to start."""
        task_service.create_task(title="Task 1")
        task_service.create_task(title="Task 2")

        ready = task_service.get_tasks_ready_to_start()

        assert len(ready) == 2


class TestTaskRetrieval:
    """Tests for task retrieval."""

    def test_get_task_by_id(self, task_service):
        """Test retrieving a task by ID."""
        task = task_service.create_task(title="Test task")

        retrieved = task_service.get_task(task.id)

        assert retrieved.id == task.id
        assert retrieved.title == "Test task"

    def test_get_nonexistent_task(self, task_service):
        """Test retrieving a nonexistent task."""
        retrieved = task_service.get_task("nonexistent-id")

        assert retrieved is None
