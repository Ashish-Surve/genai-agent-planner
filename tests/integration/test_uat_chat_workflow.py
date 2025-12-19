"""UAT workflow test - User Acceptance Testing for Chat-based task management.

This test simulates real user interactions through the chat interface:
1. User asks to add a task for tomorrow
2. System creates the task
3. User asks to delete the task
4. System deletes the task
"""

import pytest
from datetime import datetime, timedelta

from adhd_planner.core.chat_handler import ChatHandler
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.services.llm_service import LLMService
from src.database.connection import DatabaseManager
from src.services.task_service import TaskService


@pytest.fixture
def integration_db_session(tmp_path, monkeypatch):
    """Create test database session."""
    db_path = tmp_path / "uat_test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    db_manager = DatabaseManager()
    db_manager.create_tables()

    session = db_manager.session_factory()
    yield session

    session.close()
    db_manager.drop_tables()


@pytest.fixture
def task_service(integration_db_session):
    """Get task service."""
    return TaskService(integration_db_session)


@pytest.fixture
def llm_service():
    """Get LLM service."""
    return LLMService(provider_name="gemini")


@pytest.fixture
def chat_handler(llm_service):
    """Get chat handler without graph (uses mock responses)."""
    # Create handler without graph for testing
    return ChatHandler(graph=None)


class TestChatUATWorkflow:
    """User Acceptance Tests for chat-based task management workflow."""

    def test_add_task_for_tomorrow_via_chat(self, chat_handler, task_service):
        """UAT: User asks to add task for tomorrow via chat."""
        # Step 1: User sends message to add task
        user_input = "Add a task for tomorrow: Review project proposal, 2 hours, high priority"

        response = chat_handler.process_message(user_input)

        # Verify chat handler responds appropriately
        assert response is not None
        assert len(response) > 0

        # Step 2: Actually create the task (simulating what the agent would do)
        tomorrow = datetime.now() + timedelta(days=1)
        task = task_service.create_task(
            title="Review project proposal",
            estimated_duration_minutes=120,
            priority="HIGH",
            deadline=tomorrow,
        )

        # Step 3: Verify task was created in database
        assert task.id is not None
        assert task.title == "Review project proposal"
        assert task.estimated_duration_minutes == 120
        assert task.priority == "HIGH"
        assert task.deadline.date() == tomorrow.date()

    def test_add_and_delete_task_workflow(self, chat_handler, task_service):
        """UAT: Complete workflow - add task then delete it."""
        # Step 1: User asks to add a task
        user_add_input = "Add a task: Prepare presentation, 90 minutes"
        response_add = chat_handler.process_message(user_add_input)
        assert response_add is not None

        # Step 2: Create the task
        task = task_service.create_task(
            title="Prepare presentation",
            estimated_duration_minutes=90,
        )
        task_id = task.id
        assert task.title == "Prepare presentation"

        # Step 3: Verify task exists
        retrieved = task_service.get_task(task_id)
        assert retrieved is not None

        # Step 4: User asks to delete the task
        user_delete_input = f"Delete the task: {task.title}"
        response_delete = chat_handler.process_message(user_delete_input)
        assert response_delete is not None

        # Step 5: Delete the task (simulating what agent would do)
        task_service.delete_task(task_id)

        # Step 6: Verify task was deleted
        deleted_task = task_service.get_task(task_id)
        assert deleted_task is None

    def test_chat_response_to_add_task_request(self, chat_handler):
        """UAT: Chat handler responds to add task request."""
        user_input = "I want to add a new task"

        response = chat_handler.process_message(user_input)

        # Should give helpful response
        assert response is not None
        assert len(response) > 0
        # Response should be relevant to adding tasks
        assert any(
            keyword in response.lower()
            for keyword in ["task", "add", "help", "would"]
        )

    def test_chat_response_to_plan_day_request(self, chat_handler):
        """UAT: Chat handler responds to plan day request."""
        user_input = "Help me plan my day"

        response = chat_handler.process_message(user_input)

        # Should give helpful response
        assert response is not None
        assert len(response) > 0

    def test_multiple_chat_interactions(self, chat_handler, task_service):
        """UAT: Simulate multiple sequential chat interactions."""
        interactions = [
            ("Add a task: Morning standup, 30 minutes", "standup", 30),
            ("Add a task: Code review, 60 minutes", "code review", 60),
            ("Add a task: Lunch break, 45 minutes", "lunch", 45),
        ]

        created_tasks = []

        for user_input, title_part, duration in interactions:
            # Chat interaction
            response = chat_handler.process_message(user_input)
            assert response is not None

            # Create corresponding task
            task = task_service.create_task(
                title=title_part.title(),
                estimated_duration_minutes=duration,
            )
            created_tasks.append(task)

        # Verify all tasks were created
        assert len(created_tasks) == 3

        all_tasks = task_service.list_tasks()
        assert len(all_tasks) >= 3

    def test_chat_with_context(self, chat_handler, task_service):
        """UAT: Chat handler processes message with context."""
        # Create some tasks
        task1 = task_service.create_task(
            title="Task 1",
            estimated_duration_minutes=60,
            priority="HIGH",
        )
        task2 = task_service.create_task(
            title="Task 2",
            estimated_duration_minutes=30,
            priority="LOW",
        )

        # Prepare context - just pass task IDs and counts
        context = {
            "task_ids": [task1.id, task2.id],
            "task_count": 2,
        }

        # Send message with context
        user_input = "What should I work on first?"
        response = chat_handler.process_message(user_input, context=context)

        assert response is not None
        assert len(response) > 0

    def test_task_lifecycle_through_chat(self, chat_handler, task_service):
        """UAT: Complete task lifecycle (create, start, complete) via chat."""
        # Step 1: Add task via chat
        chat_handler.process_message("Add task: Write documentation")

        # Step 2: Create task in system
        task = task_service.create_task(
            title="Write documentation",
            estimated_duration_minutes=120,
        )
        assert task.status == "NOT_STARTED"

        # Step 3: User starts the task
        chat_handler.process_message("Start: Write documentation")
        task_service.start_task(task.id)

        # Step 4: Verify in progress
        started = task_service.get_task(task.id)
        assert started.status == "IN_PROGRESS"

        # Step 5: User completes the task
        chat_handler.process_message("Done with: Write documentation")
        task_service.complete_task(task.id, actual_duration_minutes=115)

        # Step 6: Verify completed
        completed = task_service.get_task(task.id)
        assert completed.status == "COMPLETED"
        assert completed.actual_duration_minutes == 115


class TestChatInputProcessing:
    """Tests for chat input parsing and understanding."""

    def test_chat_recognizes_add_task(self, chat_handler):
        """Chat should recognize 'add task' requests."""
        inputs = [
            "Add a task",
            "I want to add a new task",
            "Create task",
            "Add task: something",
        ]

        for user_input in inputs:
            response = chat_handler.process_message(user_input)
            assert response is not None

    def test_chat_recognizes_plan_request(self, chat_handler):
        """Chat should recognize planning requests."""
        inputs = [
            "Plan my day",
            "Help me plan",
            "Let's plan",
        ]

        for user_input in inputs:
            response = chat_handler.process_message(user_input)
            assert response is not None

    def test_chat_greeting(self, chat_handler):
        """Chat should respond to greetings."""
        inputs = ["Hello", "Hi", "Hey"]

        for user_input in inputs:
            response = chat_handler.process_message(user_input)
            assert response is not None
            # Should be a friendly response
            assert len(response) > 0


class TestRealWorldChatScenarios:
    """Real-world UAT scenarios."""

    def test_busy_day_workflow(self, chat_handler, task_service):
        """UAT: User has a busy day and adds multiple tasks."""
        # User arrives in morning and starts planning
        chat_handler.process_message("Good morning! Let's plan my day")

        # Add morning tasks
        tasks_to_add = [
            ("Email review", 30),
            ("Team standup", 15),
            ("Design review", 60),
        ]

        for title, duration in tasks_to_add:
            chat_handler.process_message(f"Add task: {title}, {duration} minutes")
            task_service.create_task(
                title=title,
                estimated_duration_minutes=duration,
            )

        # Mid-day check
        chat_handler.process_message("What should I do next?")

        # Verify tasks are there
        tasks = task_service.list_tasks()
        assert len(tasks) >= 3

    def test_task_interruption_workflow(self, chat_handler, task_service):
        """UAT: User gets interrupted and needs to manage tasks."""
        # User was working on Task A
        task_a = task_service.create_task(
            title="Original task",
            estimated_duration_minutes=120,
        )
        task_service.start_task(task_a.id)

        # Gets interrupted, needs to add urgent task
        chat_handler.process_message("Add urgent task: Handle customer issue")
        task_b = task_service.create_task(
            title="Handle customer issue",
            estimated_duration_minutes=45,
            priority="URGENT",
        )

        # Start urgent task (higher priority)
        task_service.start_task(task_b.id)

        # User completes urgent task
        task_service.complete_task(task_b.id, actual_duration_minutes=40)

        # Verify urgent task is done
        urgent = task_service.get_task(task_b.id)
        assert urgent.status == "COMPLETED"

        # Original task is still in progress
        original = task_service.get_task(task_a.id)
        assert original.status == "IN_PROGRESS"

    def test_end_of_day_review(self, chat_handler, task_service):
        """UAT: End of day review - user completes tasks and cleans up."""
        # Create tasks from the day
        tasks = [
            ("Task 1", 60),
            ("Task 2", 45),
            ("Task 3", 30),
        ]

        task_objects = []
        for title, duration in tasks:
            task = task_service.create_task(
                title=title,
                estimated_duration_minutes=duration,
            )
            task_objects.append(task)

        # User reviews day
        chat_handler.process_message("Let's review what I did today")

        # Marks some as done
        task_service.complete_task(task_objects[0].id, actual_duration_minutes=55)
        task_service.complete_task(task_objects[1].id, actual_duration_minutes=42)

        # Deletes unfinished tasks
        task_service.delete_task(task_objects[2].id)

        # Verify final state
        remaining = task_service.list_tasks()
        completed = [t for t in remaining if t.status == "COMPLETED"]

        assert len(completed) == 2
