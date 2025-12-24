"""Tests for ChatHandler - includes real CRUD operations with TaskService."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from adhd_planner.core.chat_handler import ChatHandler
from adhd_planner.services.task_service import TaskService
from adhd_planner.utils.errors import UserFacingError
from adhd_planner.utils.validation import ValidationError


class TestChatHandler:
    """Test ChatHandler functionality."""

    def test_initialization_without_graph(self):
        """Test initialization without graph uses mock."""
        handler = ChatHandler()
        assert handler._use_mock is True

    def test_initialization_with_graph(self):
        """Test initialization with graph."""
        mock_graph = MagicMock()
        handler = ChatHandler(graph=mock_graph)
        assert handler._use_mock is False
        assert handler.graph == mock_graph

    def test_mock_response_greeting(self):
        """Test mock response for greeting."""
        handler = ChatHandler()
        response = handler.process_message("Hello!")

        assert "Hello" in response or "👋" in response
        assert "help" in response.lower()

    def test_mock_response_add_task(self):
        """Test mock response for adding task."""
        handler = ChatHandler()
        response = handler.process_message("Add task: write report")

        assert "task" in response.lower()

    def test_mock_response_plan_day(self):
        """Test mock response for planning day."""
        handler = ChatHandler()
        response = handler.process_message("Plan my day")

        assert "plan" in response.lower() or "morning" in response.lower()

    def test_mock_response_generic(self):
        """Test mock response for generic input."""
        handler = ChatHandler()
        response = handler.process_message("Something random")

        assert len(response) > 0

    def test_process_with_graph(self):
        """Test processing with actual graph."""
        mock_graph = MagicMock()

        # Mock the graph invoke to return a state with messages
        from langchain_core.messages import AIMessage

        mock_graph.invoke.return_value = {"messages": [AIMessage(content="Graph response")]}

        handler = ChatHandler(graph=mock_graph)
        response = handler.process_message("Test input")

        assert response == "Graph response"
        mock_graph.invoke.assert_called_once()

    def test_error_handling(self):
        """Test error handling when graph fails."""
        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = Exception("Graph error")

        handler = ChatHandler(graph=mock_graph)
        response = handler.process_message("Test")

        assert "error" in response.lower()

    def test_stream_response(self):
        """Test streaming response."""
        handler = ChatHandler()

        words = list(handler.stream_response("Hello"))

        assert len(words) > 0
        # Reconstruct and verify
        full_response = "".join(words)
        assert len(full_response) > 0


# ============================================================================
# CRUD OPERATIONS TESTS - Real implementation without mocks
# ============================================================================


@pytest.fixture
def chat_handler():
    """Create chat handler without graph (mock mode)."""
    return ChatHandler()


@pytest.fixture
def task_service(test_db_session):
    """Create task service with real database."""
    return TaskService(test_db_session)


class TestGetChatHandlerWithTaskCRUD:
    """Integration tests for get_chat_handler with real task CRUD operations."""

    # ========================================================================
    # ADD TASK TESTS
    # ========================================================================

    def test_add_single_task(self, task_service, chat_handler):
        """Test adding a single task through chat handler context."""
        # Create a task using the real service
        task = task_service.create_task(
            title="Write report",
            description="Complete quarterly report",
            estimated_duration_minutes=120,
            priority="HIGH",
            energy_level="HIGH",
        )

        # Verify task was created
        assert task.id is not None
        assert task.title == "Write report"
        assert task.status == "NOT_STARTED"

        # Chat handler should be able to process this context
        response = chat_handler.process_message("I just added a task")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_add_task_with_all_fields(self, task_service):
        """Test adding task with all optional fields."""
        deadline = datetime.utcnow() + timedelta(days=7)
        task = task_service.create_task(
            title="Complete project",
            description="Finish the main project deliverable",
            estimated_duration_minutes=480,
            energy_level="HIGH",
            priority="URGENT",
            deadline=deadline,
            context_category="WORK",
            requires_focus=True,
            tags=["project", "deadline", "important"],
            sync_enabled=True,
        )

        assert task.title == "Complete project"
        assert task.priority == "URGENT"
        assert task.tags == ["project", "deadline", "important"]
        assert task.context_category == "WORK"
        assert task.deadline == deadline

    def test_add_multiple_tasks(self, task_service):
        """Test adding multiple tasks in sequence."""
        task1 = task_service.create_task(title="Task 1", priority="HIGH")
        task2 = task_service.create_task(title="Task 2", priority="MEDIUM")
        task3 = task_service.create_task(title="Task 3", priority="LOW")

        assert task1.id != task2.id
        assert task2.id != task3.id
        assert task1.title == "Task 1"
        assert task2.title == "Task 2"
        assert task3.title == "Task 3"

    def test_add_task_with_dependencies(self, task_service):
        """Test adding task with dependencies on other tasks."""
        # Create first task
        task1 = task_service.create_task(title="Task 1", priority="HIGH")

        # Create second task with first task as dependency
        task2 = task_service.create_task(
            title="Task 2", priority="MEDIUM", dependency_ids=[task1.id]
        )

        assert task2.id is not None
        assert len(task2.dependencies) > 0
        assert task2.dependencies[0].id == task1.id

    def test_add_task_validation_empty_title(self, task_service):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="")

    def test_add_task_validation_invalid_priority(self, task_service):
        """Test that invalid priority is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="Task", priority="INVALID")

    def test_add_task_validation_invalid_energy_level(self, task_service):
        """Test that invalid energy level is rejected."""
        with pytest.raises(ValidationError):
            task_service.create_task(title="Task", energy_level="EXTREME")

    # ========================================================================
    # LIST TASKS TESTS
    # ========================================================================

    def test_list_all_tasks_empty(self, task_service):
        """Test listing tasks when database is empty."""
        tasks = task_service.list_tasks()
        assert tasks == []

    def test_list_all_tasks_after_adding(self, task_service):
        """Test listing all tasks after adding several."""
        task1 = task_service.create_task(title="Task 1", priority="HIGH")
        task2 = task_service.create_task(title="Task 2", priority="MEDIUM")
        task3 = task_service.create_task(title="Task 3", priority="LOW")

        tasks = task_service.list_tasks()
        assert len(tasks) == 3
        assert task1 in tasks
        assert task2 in tasks
        assert task3 in tasks

    def test_list_tasks_filter_by_priority(self, task_service):
        """Test listing tasks filtered by priority."""
        task_service.create_task(title="High 1", priority="HIGH")
        task_service.create_task(title="High 2", priority="HIGH")
        task_service.create_task(title="Medium 1", priority="MEDIUM")

        high_tasks = task_service.list_tasks(priority="HIGH")
        assert len(high_tasks) == 2
        assert all(t.priority == "HIGH" for t in high_tasks)

    def test_list_tasks_filter_by_status(self, task_service):
        """Test listing tasks filtered by status."""
        task1 = task_service.create_task(title="Task 1", priority="HIGH")
        task_service.create_task(title="Task 2", priority="HIGH")

        # Change status of one task
        task_service.start_task(task1.id)

        not_started = task_service.list_tasks(status="NOT_STARTED")
        in_progress = task_service.list_tasks(status="IN_PROGRESS")

        assert len(not_started) == 1
        assert len(in_progress) == 1
        assert not_started[0].title == "Task 2"
        assert in_progress[0].title == "Task 1"

    def test_list_tasks_filter_by_tag(self, task_service):
        """Test listing tasks filtered by tag."""
        task_service.create_task(title="Work 1", tags=["work", "urgent"])
        task_service.create_task(title="Work 2", tags=["work"])
        task_service.create_task(title="Personal", tags=["personal"])

        work_tasks = task_service.list_tasks(tag="work")
        assert len(work_tasks) == 2
        assert all("work" in t.tags for t in work_tasks)

    def test_list_tasks_filter_by_context(self, task_service):
        """Test listing tasks filtered by context category."""
        task_service.create_task(title="Work task", context_category="WORK")
        task_service.create_task(title="Home task", context_category="HOME")
        task_service.create_task(title="Work task 2", context_category="WORK")

        work_tasks = task_service.list_tasks(context_category="WORK")
        assert len(work_tasks) == 2
        assert all(t.context_category == "WORK" for t in work_tasks)

    def test_list_tasks_with_limit(self, task_service):
        """Test listing tasks with limit."""
        for i in range(5):
            task_service.create_task(title=f"Task {i+1}", priority="HIGH")

        limited_tasks = task_service.list_tasks(limit=3)
        assert len(limited_tasks) == 3

    def test_list_incomplete_tasks(self, task_service):
        """Test listing only incomplete tasks."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2")
        task3 = task_service.create_task(title="Task 3")

        # Complete one task
        task_service.complete_task(task2.id)

        incomplete = task_service.get_incomplete_tasks()
        assert len(incomplete) == 2
        assert task1 in incomplete
        assert task3 in incomplete
        assert task2 not in incomplete

    def test_list_tasks_by_status(self, task_service):
        """Test getting tasks by specific status."""
        task_service.create_task(title="Not started")
        task2 = task_service.create_task(title="In progress")

        task_service.start_task(task2.id)

        not_started_tasks = task_service.get_tasks_by_status("NOT_STARTED")
        in_progress_tasks = task_service.get_tasks_by_status("IN_PROGRESS")

        assert len(not_started_tasks) == 1
        assert len(in_progress_tasks) == 1

    # ========================================================================
    # EDIT/UPDATE TASK TESTS
    # ========================================================================

    def test_edit_task_title(self, task_service):
        """Test updating task title."""
        task = task_service.create_task(title="Original title")
        updated = task_service.update_task(task.id, title="Updated title")

        assert updated.title == "Updated title"
        assert updated.id == task.id

    def test_edit_task_priority(self, task_service):
        """Test updating task priority."""
        task = task_service.create_task(title="Task", priority="LOW")
        updated = task_service.update_task(task.id, priority="URGENT")

        assert updated.priority == "URGENT"

    def test_edit_task_description(self, task_service):
        """Test updating task description."""
        task = task_service.create_task(title="Task", description="Old description")
        updated = task_service.update_task(task.id, description="New description")

        assert updated.description == "New description"

    def test_edit_task_duration(self, task_service):
        """Test updating estimated duration."""
        task = task_service.create_task(title="Task", estimated_duration_minutes=60)
        updated = task_service.update_task(task.id, estimated_duration_minutes=120)

        assert updated.estimated_duration_minutes == 120

    def test_edit_task_energy_level(self, task_service):
        """Test updating energy level."""
        task = task_service.create_task(title="Task", energy_level="LOW")
        updated = task_service.update_task(task.id, energy_level="HIGH")

        assert updated.estimated_energy_level == "HIGH"

    def test_edit_task_multiple_fields(self, task_service):
        """Test updating multiple fields at once."""
        task = task_service.create_task(
            title="Original",
            priority="LOW",
            energy_level="LOW",
            estimated_duration_minutes=30,
        )

        updated = task_service.update_task(
            task.id,
            title="Updated",
            priority="URGENT",
            energy_level="HIGH",
            estimated_duration_minutes=240,
        )

        assert updated.title == "Updated"
        assert updated.priority == "URGENT"
        assert updated.estimated_energy_level == "HIGH"
        assert updated.estimated_duration_minutes == 240

    def test_edit_nonexistent_task(self, task_service):
        """Test editing a task that doesn't exist."""
        with pytest.raises(UserFacingError):
            task_service.update_task("nonexistent_id", title="New title")

    def test_edit_task_invalid_priority(self, task_service):
        """Test that invalid priority update is rejected."""
        task = task_service.create_task(title="Task", priority="HIGH")

        with pytest.raises(ValidationError):
            task_service.update_task(task.id, priority="INVALID")

    # ========================================================================
    # DELETE TASK TESTS
    # ========================================================================

    def test_delete_single_task(self, task_service):
        """Test deleting a single task."""
        task = task_service.create_task(title="Task to delete")
        task_service.delete_task(task.id)

        retrieved = task_service.get_task(task.id)
        assert retrieved is None

    def test_delete_nonexistent_task(self, task_service):
        """Test deleting a task that doesn't exist."""
        with pytest.raises(UserFacingError):
            task_service.delete_task("nonexistent_id")

    def test_delete_task_with_dependents(self, task_service):
        """Test that deleting a task with dependents is rejected."""
        task1 = task_service.create_task(title="Task 1")
        task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        # Try to delete task1 which has task2 depending on it
        with pytest.raises(UserFacingError) as exc_info:
            task_service.delete_task(task1.id)

        assert "depend" in str(exc_info.value).lower()

    # ========================================================================
    # GET TASK TESTS
    # ========================================================================

    def test_get_single_task_by_id(self, task_service):
        """Test retrieving a single task by ID."""
        created = task_service.create_task(title="Test task")
        retrieved = task_service.get_task(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test task"

    def test_get_nonexistent_task(self, task_service):
        """Test retrieving a task that doesn't exist."""
        retrieved = task_service.get_task("nonexistent_id")
        assert retrieved is None

    # ========================================================================
    # STATE CHANGE TESTS
    # ========================================================================

    def test_start_task(self, task_service):
        """Test starting a task (transitioning to IN_PROGRESS)."""
        task = task_service.create_task(title="Task")
        assert task.status == "NOT_STARTED"

        started = task_service.start_task(task.id)
        assert started.status == "IN_PROGRESS"

    def test_start_already_started_task(self, task_service):
        """Test starting a task that's already in progress."""
        task = task_service.create_task(title="Task")
        task_service.start_task(task.id)

        # Should not raise error, just return the task
        result = task_service.start_task(task.id)
        assert result.status == "IN_PROGRESS"

    def test_complete_task(self, task_service):
        """Test completing a task."""
        task = task_service.create_task(title="Task")
        completed = task_service.complete_task(task.id)

        assert completed.status == "COMPLETED"
        assert completed.completed_at is not None

    def test_complete_task_with_actual_duration(self, task_service):
        """Test completing a task and recording actual duration."""
        task = task_service.create_task(title="Task", estimated_duration_minutes=60)
        completed = task_service.complete_task(task.id, actual_duration_minutes=45)

        assert completed.status == "COMPLETED"
        assert completed.actual_duration_minutes == 45

    def test_complete_already_completed_task(self, task_service):
        """Test completing a task that's already completed."""
        task = task_service.create_task(title="Task")
        task_service.complete_task(task.id)

        # Should not raise error
        result = task_service.complete_task(task.id)
        assert result.status == "COMPLETED"

    def test_cannot_start_completed_task(self, task_service):
        """Test that completed task cannot be started again."""
        task = task_service.create_task(title="Task")
        task_service.complete_task(task.id)

        with pytest.raises(UserFacingError):
            task_service.start_task(task.id)

    # ========================================================================
    # DEPENDENCY TESTS
    # ========================================================================

    def test_cannot_start_task_with_incomplete_dependencies(self, task_service):
        """Test that task with incomplete dependencies cannot be started."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        with pytest.raises(UserFacingError) as exc_info:
            task_service.start_task(task2.id)

        assert "depend" in str(exc_info.value).lower()

    def test_can_start_task_after_dependencies_completed(self, task_service):
        """Test that task can be started after dependencies are completed."""
        task1 = task_service.create_task(title="Task 1")
        task2 = task_service.create_task(title="Task 2", dependency_ids=[task1.id])

        # Complete the dependency
        task_service.complete_task(task1.id)

        # Now should be able to start task2
        started = task_service.start_task(task2.id)
        assert started.status == "IN_PROGRESS"

    def test_invalid_dependency_id(self, task_service):
        """Test creating task with non-existent dependency."""
        with pytest.raises(UserFacingError):
            task_service.create_task(title="Task", dependency_ids=["nonexistent_id"])

    # ========================================================================
    # CHAT HANDLER INTEGRATION TESTS
    # ========================================================================

    def test_chat_handler_add_task_prompt(self, chat_handler):
        """Test chat handler response to add task request."""
        response = chat_handler.process_message("Add task: learn Python")
        assert isinstance(response, str)
        assert len(response) > 0
        assert "task" in response.lower()

    def test_chat_handler_plan_day_prompt(self, chat_handler):
        """Test chat handler response to planning request."""
        response = chat_handler.process_message("Plan my day")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_chat_handler_list_tasks_context(self, task_service, chat_handler):
        """Test chat handler with task list context."""
        task_service.create_task(title="Task 1", priority="HIGH")
        task_service.create_task(title="Task 2", priority="MEDIUM")

        # Chat handler should be able to process with context
        tasks = task_service.list_tasks()
        assert len(tasks) == 2

        # Handler processes message
        response = chat_handler.process_message("What tasks do I have?")
        assert isinstance(response, str)

    def test_chat_handler_stream_response(self, chat_handler):
        """Test chat handler streaming response."""
        words = list(chat_handler.stream_response("What should I do?"))
        assert len(words) > 0

        # Should be able to reconstruct response
        full = "".join(words)
        assert len(full) > 0
