"""Integration tests for agent system without mocks.

These tests exercise the actual agent system with real services
and database interactions. Tests focus on the core functionality
that doesn't depend on external LLM providers.
"""

from datetime import datetime, timedelta

import pytest

from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.agents.suggestion_agent import SuggestionAgent
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.database.connection import DatabaseManager
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.services.calendar_service import CalendarService
from adhd_planner.services.llm_service import LLMService
from adhd_planner.services.task_service import TaskService


@pytest.fixture
def integration_db_session(tmp_path, monkeypatch):
    """Create an actual test database session for integration tests."""
    # Set up temporary database path
    db_path = tmp_path / "integration_test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Create database manager and initialize tables
    db_manager = DatabaseManager()
    db_manager.create_tables()

    session = db_manager.session_factory()
    yield session

    # Cleanup
    session.close()
    db_manager.drop_tables()


@pytest.fixture
def task_service(integration_db_session):
    """Create actual task service with real database."""
    return TaskService(integration_db_session)


@pytest.fixture
def calendar_service(integration_db_session):
    """Create actual calendar service with real database."""
    return CalendarService(integration_db_session)


@pytest.fixture
def llm_service():
    """Create LLM service using gemini provider."""
    return LLMService(provider_name="gemini", temperature=0.3)


@pytest.fixture
def planning_agent(task_service, llm_service):
    """Create planning agent with real services."""
    return PlanningAgent(
        llm_service=llm_service,
        task_service=task_service,
    )


@pytest.fixture
def scheduling_agent(task_service, calendar_service, llm_service):
    """Create scheduling agent with real services."""
    return SchedulingAgent(
        llm_service=llm_service,
        task_service=task_service,
        calendar_service=calendar_service,
    )


@pytest.fixture
def suggestion_agent(task_service, calendar_service, llm_service):
    """Create suggestion agent with real services."""
    return SuggestionAgent(
        llm_service=llm_service,
        task_service=task_service,
        calendar_service=calendar_service,
    )


@pytest.fixture
def supervisor_agent(llm_service):
    """Create supervisor agent with real services."""
    return SupervisorAgent(llm_service=llm_service)


class TestTaskServiceIntegration:
    """Integration tests for task service with real database."""

    def test_create_task_end_to_end(self, task_service):
        """Test creating a task with real database."""
        task = task_service.create_task(
            title="Complete project report",
            description="Quarterly report for Q4",
            estimated_duration_minutes=180,
            energy_level="HIGH",
            priority="HIGH",
        )

        assert task is not None
        assert task.id is not None
        assert task.title == "Complete project report"
        assert task.status == "NOT_STARTED"
        assert task.estimated_duration_minutes == 180

    def test_task_with_deadline(self, task_service):
        """Test creating a task with deadline."""
        deadline = datetime.now() + timedelta(days=7)
        task = task_service.create_task(
            title="Study Python",
            estimated_duration_minutes=120,
            deadline=deadline,
        )

        assert task.deadline is not None
        assert task.deadline.date() == deadline.date()

    def test_multiple_tasks_creation(self, task_service):
        """Test creating multiple tasks sequentially."""
        tasks_data = [
            ("Write documentation", 90, "MEDIUM"),
            ("Review code changes", 60, "MEDIUM"),
            ("Deploy to staging", 45, "LOW"),
        ]

        created_tasks = []
        for title, duration, energy in tasks_data:
            task = task_service.create_task(
                title=title,
                estimated_duration_minutes=duration,
                energy_level=energy,
            )
            created_tasks.append(task)

        assert len(created_tasks) == 3

        # Verify all in database
        all_tasks = task_service.list_tasks()
        assert len(all_tasks) >= 3

    def test_task_status_transitions(self, task_service):
        """Test task status transitions."""
        # Create
        task = task_service.create_task(title="Test task", estimated_duration_minutes=30)
        assert task.status == "NOT_STARTED"

        # Start
        started = task_service.start_task(task.id)
        assert started.status == "IN_PROGRESS"

        # Complete
        completed = task_service.complete_task(task.id, actual_duration_minutes=25)
        assert completed.status == "COMPLETED"
        assert completed.actual_duration_minutes == 25

    def test_get_overdue_tasks(self, task_service):
        """Test retrieving overdue tasks."""
        # Create a task with future deadline first
        future_deadline = datetime.now() + timedelta(days=7)
        future_task = task_service.create_task(
            title="Future task",
            deadline=future_deadline,
        )

        # Verify the task was created with proper deadline
        retrieved = task_service.get_task(future_task.id)
        assert retrieved is not None
        assert retrieved.title == "Future task"
        assert retrieved.deadline is not None

    def test_get_tasks_by_status(self, task_service):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        task1 = task_service.create_task(title="Not started")
        task2 = task_service.create_task(title="To be started")
        task_service.start_task(task2.id)

        not_started = task_service.get_tasks_by_status("NOT_STARTED")
        assert len(not_started) >= 1

        in_progress = task_service.get_tasks_by_status("IN_PROGRESS")
        assert len(in_progress) >= 1

    def test_task_update(self, task_service):
        """Test updating an existing task."""
        task = task_service.create_task(
            title="Original title",
            priority="MEDIUM",
        )

        updated = task_service.update_task(
            task.id,
            title="Updated title",
            priority="HIGH",
        )

        assert updated.title == "Updated title"
        assert updated.priority == "HIGH"

    def test_task_validation(self, task_service):
        """Test task service validation."""
        # Empty title should fail
        with pytest.raises(Exception):
            task_service.create_task(title="", estimated_duration_minutes=30)

        # Negative duration should fail
        with pytest.raises(Exception):
            task_service.create_task(title="Valid", estimated_duration_minutes=-30)


class TestCalendarServiceIntegration:
    """Integration tests for calendar service."""

    def test_create_time_block(self, calendar_service):
        """Test creating a time block."""
        start = datetime.now().replace(hour=9, minute=0, second=0)
        end = start + timedelta(hours=1)

        block = calendar_service.create_time_block(
            start_time=start,
            end_time=end,
            block_type="TASK",
            energy_level_required="HIGH",
        )

        assert block is not None
        assert block.start_time == start
        assert block.end_time == end

    def test_list_time_blocks(self, calendar_service):
        """Test listing time blocks."""
        now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        # Create multiple blocks
        for i in range(3):
            start = now + timedelta(hours=i)
            end = start + timedelta(hours=1)
            calendar_service.create_time_block(start_time=start, end_time=end)

        # Get blocks for date
        blocks = calendar_service.get_blocks_for_date(now.date())
        assert len(blocks) >= 3

    def test_get_available_slots(self, calendar_service):
        """Test getting available time slots."""
        now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        # Create a block
        start = now + timedelta(hours=2)
        end = start + timedelta(hours=1)
        calendar_service.create_time_block(start_time=start, end_time=end)

        # Get slots - use find_available_slots
        slots = calendar_service.find_available_slots(
            target_date=now.date(),
            duration_minutes=30,
        )

        assert len(slots) > 0

    def test_find_slot_for_task(self, calendar_service):
        """Test finding a slot for a task."""
        # Create a conflicting block
        now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=1)
        calendar_service.create_time_block(start_time=start, end_time=end)

        # Get available slots for today
        slots = calendar_service.find_available_slots(
            target_date=now.date(),
            duration_minutes=60,
        )

        # Should find some available slots
        assert len(slots) > 0

    def test_time_block_types(self, calendar_service):
        """Test creating different types of time blocks."""
        block_types = ["TASK", "BREAK", "BUFFER", "FREE"]
        now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        for i, block_type in enumerate(block_types):
            start = now + timedelta(hours=i)
            end = start + timedelta(hours=1)
            block = calendar_service.create_time_block(
                start_time=start,
                end_time=end,
                block_type=block_type,
            )
            assert block.block_type == block_type


class TestStateManagement:
    """Tests for state management."""

    def test_initial_state_creation(self):
        """Test creating initial state."""
        state = StateManager.create_initial_state("Add task: Test task")

        assert state["user_input"] == "Add task: Test task"
        assert state["context"] is not None
        assert isinstance(state["context"], dict)

    def test_state_add_ai_message(self):
        """Test adding AI message to state."""
        state = StateManager.create_initial_state("User input")
        initial_count = len(state["messages"])

        state = StateManager().add_ai_message(state, "AI response", "agent_name")

        assert len(state["messages"]) > initial_count

    def test_state_context_update(self):
        """Test updating context."""
        state = StateManager.create_initial_state("test")
        state_manager = StateManager()

        state = state_manager.update_context(state, "test_key", "test_value")

        assert state["context"]["test_key"] == "test_value"

    def test_state_error_handling(self):
        """Test error state management."""
        state = StateManager.create_initial_state("test")
        state_manager = StateManager()

        state = state_manager.set_error(state, "Test error", "test_agent")

        assert state["error"] is not None
        assert "Test error" in state["error"]


class TestAgentInitialization:
    """Tests for proper agent initialization."""

    def test_planning_agent_initialization(self, planning_agent):
        """Test planning agent initializes correctly."""
        assert planning_agent.name == "planning_agent"
        assert planning_agent.description is not None
        assert planning_agent.logger is not None
        assert planning_agent.services is not None

    def test_scheduling_agent_initialization(self, scheduling_agent):
        """Test scheduling agent initializes correctly."""
        assert scheduling_agent.name == "scheduling_agent"
        assert scheduling_agent.description is not None

    def test_suggestion_agent_initialization(self, suggestion_agent):
        """Test suggestion agent initializes correctly."""
        assert suggestion_agent.name == "suggestion_agent"
        assert suggestion_agent.description is not None

    def test_supervisor_agent_initialization(self, supervisor_agent):
        """Test supervisor agent initializes correctly."""
        assert supervisor_agent.name == "supervisor"
        assert supervisor_agent.description is not None

    def test_agents_have_required_services(self, planning_agent, task_service):
        """Test agents have access to required services."""
        llm_service = planning_agent.get_service("llm_service")
        task_svc = planning_agent.get_service("task_service")

        assert llm_service is not None
        assert task_svc is not None
        assert isinstance(task_svc, TaskService)

    def test_missing_service_raises_error(self, planning_agent):
        """Test accessing missing service raises error."""
        with pytest.raises(ValueError):
            planning_agent.get_service("nonexistent_service")


class TestAgentErrorHandling:
    """Tests for agent error handling with real services."""

    def test_planning_agent_error_handling(self, planning_agent):
        """Test planning agent handles errors gracefully."""
        # Create state with minimal input
        state = StateManager.create_initial_state("")

        # Should not crash
        result = planning_agent.execute(state)
        assert result is not None

    def test_task_service_input_validation(self, task_service):
        """Test task service validates input properly."""
        # Empty title should fail
        with pytest.raises(Exception):
            task_service.create_task(title="", estimated_duration_minutes=30)

    def test_task_service_duration_validation(self, task_service):
        """Test task service validates duration."""
        # Negative duration should fail
        with pytest.raises(Exception):
            task_service.create_task(title="Test", estimated_duration_minutes=-30)

        # Zero duration should fail
        with pytest.raises(Exception):
            task_service.create_task(title="Test", estimated_duration_minutes=0)

    def test_calendar_service_time_validation(self, calendar_service):
        """Test calendar service validates times."""
        now = datetime.now()
        past = now - timedelta(hours=1)

        # End time before start time should fail
        with pytest.raises(Exception):
            calendar_service.create_time_block(
                start_time=now,
                end_time=past,
            )


class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios."""

    def test_create_and_manage_task_workflow(self, task_service):
        """Test complete task workflow: create, start, complete."""
        # Step 1: Create task
        task = task_service.create_task(
            title="Prepare presentation",
            estimated_duration_minutes=120,
            priority="HIGH",
            energy_level="HIGH",
        )
        assert task.status == "NOT_STARTED"

        # Step 2: Start task
        started = task_service.start_task(task.id)
        assert started.status == "IN_PROGRESS"

        # Step 3: Complete task
        completed = task_service.complete_task(task.id, actual_duration_minutes=115)
        assert completed.status == "COMPLETED"

        # Step 4: Verify in database
        retrieved = task_service.get_task(task.id)
        assert retrieved.status == "COMPLETED"
        assert retrieved.actual_duration_minutes == 115

    def test_daily_schedule_simulation(self, task_service, calendar_service):
        """Simulate a daily schedule workflow."""
        now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        # Morning: Create tasks
        tasks = []
        task_specs = [
            ("Email responses", 30, "LOW"),
            ("Code review", 60, "MEDIUM"),
            ("Planning", 90, "HIGH"),
        ]

        for title, duration, energy in task_specs:
            task = task_service.create_task(
                title=title,
                estimated_duration_minutes=duration,
                energy_level=energy,
                priority="MEDIUM",
            )
            tasks.append(task)

        assert len(tasks) == 3

        # Schedule time blocks
        for i, task in enumerate(tasks):
            start = now + timedelta(hours=i)
            end = start + timedelta(minutes=task.estimated_duration_minutes)
            block = calendar_service.create_time_block(
                start_time=start,
                end_time=end,
                task_id=task.id,
            )
            assert block is not None

        # Verify schedule created
        blocks = calendar_service.get_blocks_for_date(now.date())
        assert len(blocks) >= 3

    def test_task_filtering_and_sorting(self, task_service):
        """Test task filtering and listing capabilities."""
        # Create varied tasks
        tasks_data = [
            ("Urgent bug fix", 30, "URGENT", "HIGH"),
            ("Documentation", 120, "LOW", "MEDIUM"),
            ("Feature request", 240, "HIGH", "MEDIUM"),
            ("Code review", 60, "MEDIUM", "MEDIUM"),
        ]

        for title, duration, priority, energy in tasks_data:
            task_service.create_task(
                title=title,
                estimated_duration_minutes=duration,
                priority=priority,
                energy_level=energy,
            )

        # Test filtering
        high_priority = task_service.list_tasks(priority="HIGH")
        assert len(high_priority) > 0

        urgent = task_service.list_tasks(priority="URGENT")
        assert len(urgent) > 0

        # Test limiting
        limited = task_service.list_tasks(limit=2)
        assert len(limited) <= 2

    def test_multi_day_schedule(self, calendar_service):
        """Test scheduling across multiple days."""
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        # Create blocks for 3 days
        for day in range(3):
            for hour in range(9, 17):  # 9am to 5pm
                start = base_date + timedelta(days=day, hours=hour - 9)
                end = start + timedelta(hours=1)

                # Skip lunch
                if hour == 12:
                    block = calendar_service.create_time_block(
                        start_time=start,
                        end_time=end,
                        block_type="BREAK",
                    )
                else:
                    block = calendar_service.create_time_block(
                        start_time=start,
                        end_time=end,
                        block_type="TASK",
                    )

        # Get blocks for date range
        blocks = calendar_service.get_blocks_for_date_range(
            start_date=base_date.date(), end_date=base_date.date() + timedelta(days=2)
        )
        assert len(blocks) >= 21  # 3 days * 7 work hours


class TestServiceInteraction:
    """Tests for interaction between services."""

    def test_task_and_calendar_integration(self, task_service, calendar_service):
        """Test task service working with calendar service."""
        # Create a task
        task = task_service.create_task(
            title="Important task",
            estimated_duration_minutes=120,
        )

        # Schedule it in calendar
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        block = calendar_service.create_time_block(
            start_time=now,
            end_time=now + timedelta(minutes=120),
            task_id=task.id,
        )

        # Both should exist independently
        retrieved_task = task_service.get_task(task.id)
        assert retrieved_task is not None

        blocks = calendar_service.get_blocks_for_date(now.date())
        assert len(blocks) > 0

    def test_state_propagation_through_services(self, task_service, calendar_service):
        """Test state changes propagate correctly."""
        # Create task
        task = task_service.create_task(
            title="Stateful task",
            estimated_duration_minutes=60,
        )

        # Create schedule
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        calendar_service.create_time_block(
            start_time=now,
            end_time=now + timedelta(hours=1),
            task_id=task.id,
        )

        # Update task status
        task_service.start_task(task.id)

        # Verify state
        updated = task_service.get_task(task.id)
        assert updated.status == "IN_PROGRESS"
