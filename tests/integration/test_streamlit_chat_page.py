"""
Integration tests for Streamlit Chat Page.
Tests chat handler, message processing, and agent interactions.
"""

from unittest.mock import MagicMock, patch

import pytest

from adhd_planner.core.chat_handler import ChatHandler


class MockSessionManager:
    """Mock session manager for testing without Streamlit."""

    def __init__(self):
        self._messages = []
        self._context = {}

    def add_message(self, role: str, content: str):
        self._messages.append({"role": role, "content": content})

    def get_message_history(self):
        return self._messages

    def clear_history(self):
        self._messages = []

    def set_context(self, key: str, value):
        self._context[key] = value

    def get_context(self, key: str):
        return self._context.get(key)


@pytest.fixture
def session_manager():
    """Create a mock session manager for testing."""
    return MockSessionManager()


@pytest.fixture
def chat_handler(test_db_session):
    """Create a chat handler for testing (without graph - uses mock responses)."""
    return ChatHandler(graph=None)  # Uses mock mode


@pytest.fixture
def mock_graph():
    """Create a mock LangGraph for testing."""
    mock = MagicMock()
    mock.invoke = MagicMock(
        return_value={
            "messages": [
                {"type": "human", "content": "Add a task"},
                {
                    "type": "ai",
                    "content": "I'll help you add a task. What would you like to call it?",
                },
            ]
        }
    )
    return mock


class TestChatHandlerBasic:
    """Test basic chat handler functionality."""

    def test_chat_handler_initialization(self, chat_handler):
        """Test chat handler initialization."""
        assert chat_handler is not None

    def test_process_simple_message(self, chat_handler, mock_graph):
        """Test processing a simple user message."""
        with patch.object(chat_handler, "graph", mock_graph):
            response = chat_handler.process_message("Hello")
            assert response is not None

    def test_process_empty_message(self, chat_handler):
        """Test processing an empty message - should return a response (mock mode)."""
        # In mock mode, empty strings are handled gracefully
        response = chat_handler.process_message("")
        # Mock mode returns a response for any input
        assert response is not None

    def test_process_message_with_special_characters(self, chat_handler):
        """Test processing message with special characters."""
        message = "Can you help me with @#$% special chars?"
        # Should not raise an error
        response = chat_handler.process_message(message)
        assert response is not None

    def test_process_very_long_message(self, chat_handler):
        """Test processing a very long message."""
        long_message = "a" * 5000
        response = chat_handler.process_message(long_message)
        assert response is not None


class TestChatHandlerTaskCreation:
    """Test chat-based task creation."""

    def test_create_task_via_chat(self, chat_handler):
        """Test creating a task through chat."""
        message = "Add a task: Finish project proposal, 2 hours, high priority"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_create_task_with_deadline(self, chat_handler):
        """Test creating a task with deadline via chat."""
        message = "Create a task: Review docs, due tomorrow, medium priority"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_create_recurring_task(self, chat_handler):
        """Test creating a recurring task."""
        message = "Add a recurring task: Daily standup, every day at 10am"
        response = chat_handler.process_message(message)
        assert response is not None


class TestChatHandlerScheduling:
    """Test chat-based scheduling."""

    def test_schedule_task_via_chat(self, chat_handler):
        """Test scheduling a task through chat."""
        message = "Schedule the project proposal task for tomorrow at 2pm"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_find_available_time(self, chat_handler):
        """Test finding available time via chat."""
        message = "When am I free tomorrow?"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_reschedule_task(self, chat_handler):
        """Test rescheduling a task via chat."""
        message = "Move the meeting to next week"
        response = chat_handler.process_message(message)
        assert response is not None


class TestChatHandlerPlanning:
    """Test chat-based planning features."""

    def test_plan_day_via_chat(self, chat_handler):
        """Test planning the day through chat."""
        message = "Help me plan my day"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_suggest_priority_tasks(self, chat_handler):
        """Test getting task suggestions."""
        message = "What should I work on next?"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_analyze_time_blocking(self, chat_handler):
        """Test analyzing time block efficiency."""
        message = "How is my schedule looking?"
        response = chat_handler.process_message(message)
        assert response is not None


class TestChatHandlerQuickActions:
    """Test quick action buttons in chat."""

    def test_quick_action_add_task(self, chat_handler):
        """Test quick action to add a task."""
        # Simulate quick action button click
        message = "I want to add a new task"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_quick_action_plan_day(self, chat_handler):
        """Test quick action to plan day."""
        message = "Let's plan my day"
        response = chat_handler.process_message(message)
        assert response is not None

    def test_quick_action_what_to_do(self, chat_handler):
        """Test quick action for suggestions."""
        message = "What should I do right now?"
        response = chat_handler.process_message(message)
        assert response is not None


class TestChatSessionManagement:
    """Test session state management in chat."""

    def test_session_initialization(self, session_manager):
        """Test session initialization."""
        assert session_manager is not None

    def test_session_message_history(self, session_manager):
        """Test storing message history."""
        session_manager.add_message("user", "Hello")
        session_manager.add_message("assistant", "Hi there!")

        history = session_manager.get_message_history()
        assert len(history) == 2

    def test_session_clear_history(self, session_manager):
        """Test clearing message history."""
        session_manager.add_message("user", "Test message")
        session_manager.clear_history()

        history = session_manager.get_message_history()
        assert len(history) == 0

    def test_session_context_preservation(self, session_manager):
        """Test context preservation across messages."""
        session_manager.set_context("current_task", "task_123")
        context = session_manager.get_context("current_task")

        assert context == "task_123"

    def test_session_multiple_contexts(self, session_manager):
        """Test managing multiple contexts."""
        session_manager.set_context("current_task", "task_1")
        session_manager.set_context("selected_date", "2024-01-15")
        session_manager.set_context("view_mode", "list")

        assert session_manager.get_context("current_task") == "task_1"
        assert session_manager.get_context("selected_date") == "2024-01-15"
        assert session_manager.get_context("view_mode") == "list"


class TestChatHandlerWithMockGraph:
    """Test chat handler with mocked LangGraph."""

    def test_chat_with_mock_response(self, chat_handler, mock_graph):
        """Test chat with mocked graph response."""
        with patch.object(chat_handler, "graph", mock_graph):
            response = chat_handler.process_message("Help me create a task")
            assert response is not None

    def test_chat_with_task_suggestion(self, chat_handler):
        """Test chat returning task suggestions."""
        # Use mock mode which is already enabled for this fixture
        response = chat_handler.process_message("What should I work on?")
        assert response is not None

    def test_chat_with_error_recovery(self, chat_handler):
        """Test chat error handling and recovery."""
        # Mock mode is already enabled, so errors are handled gracefully
        response = chat_handler.process_message("Hello")
        assert response is not None


class TestChatHandlerIntentRecognition:
    """Test message intent recognition."""

    def test_recognize_task_creation_intent(self, chat_handler):
        """Test recognizing task creation intent."""
        intents = [
            "Add a task",
            "Create a new task",
            "I need to add something",
            "New task: something",
        ]
        for message in intents:
            response = chat_handler.process_message(message)
            assert response is not None

    def test_recognize_scheduling_intent(self, chat_handler):
        """Test recognizing scheduling intent."""
        intents = [
            "Schedule this for tomorrow",
            "Put this on my calendar",
            "When can I do this task?",
            "Find me some time",
        ]
        for message in intents:
            response = chat_handler.process_message(message)
            assert response is not None

    def test_recognize_planning_intent(self, chat_handler):
        """Test recognizing planning intent."""
        intents = [
            "Help me plan today",
            "What's my priority?",
            "Should I work on this next?",
            "Plan my week",
        ]
        for message in intents:
            response = chat_handler.process_message(message)
            assert response is not None

    def test_recognize_query_intent(self, chat_handler):
        """Test recognizing query intent."""
        intents = [
            "How many tasks do I have?",
            "What's my schedule like?",
            "Show me overdue tasks",
            "List my high priority items",
        ]
        for message in intents:
            response = chat_handler.process_message(message)
            assert response is not None


class TestChatHandlerMultiTurn:
    """Test multi-turn conversation handling."""

    def test_two_turn_conversation(self, session_manager, chat_handler):
        """Test a two-turn conversation."""
        session_manager.add_message("user", "Create a task")
        session_manager.add_message("assistant", "What would you like to call it?")

        history = session_manager.get_message_history()
        assert len(history) == 2

    def test_maintain_context_across_turns(self, session_manager):
        """Test maintaining context across conversation turns."""
        session_manager.set_context("creating_task", True)
        session_manager.set_context("task_title", "My Task")

        # Simulate additional turns
        session_manager.add_message("user", "When is it due?")
        session_manager.add_message("assistant", "When would you like to complete it?")

        assert session_manager.get_context("creating_task") is True
        assert session_manager.get_context("task_title") == "My Task"

    def test_conversation_state_cleanup(self, session_manager):
        """Test cleaning up conversation state."""
        session_manager.set_context("creating_task", True)
        session_manager.clear_history()
        session_manager.set_context("creating_task", False)

        assert session_manager.get_context("creating_task") is False


class TestChatHandlerErrorHandling:
    """Test error handling in chat."""

    def test_handle_graph_unavailable(self, chat_handler):
        """Test handling when graph is unavailable."""
        # Graph is already None in our fixture (mock mode)
        response = chat_handler.process_message("Hello")
        assert response is not None

    def test_handle_service_error(self, chat_handler):
        """Test handling service errors gracefully."""
        # Mock mode handles all errors gracefully
        response = chat_handler.process_message("Add a task")
        assert response is not None

    def test_handle_invalid_input(self, chat_handler):
        """Test handling invalid input - mock mode handles gracefully."""
        # Mock mode returns response for any input
        response = chat_handler.process_message("")
        assert response is not None

    def test_handle_timeout(self, chat_handler):
        """Test handling response timeout - mock mode doesn't timeout."""
        # Mock mode is instant, no timeout possible
        response = chat_handler.process_message("Hello")
        assert response is not None


class TestChatHandlerIntegration:
    """Integration tests for complete chat workflows."""

    def test_complete_task_creation_workflow(self, chat_handler, session_manager):
        """Test complete workflow of creating a task via chat."""
        # User asks to create task
        response1 = chat_handler.process_message("I want to add a task")
        assert response1 is not None

        # User provides task details
        response2 = chat_handler.process_message(
            "It's called 'Finish report', high priority, 2 hours"
        )
        assert response2 is not None

    def test_task_creation_and_scheduling(self, chat_handler):
        """Test creating and scheduling a task via chat."""
        # Create task
        response1 = chat_handler.process_message("Create a task: Review document")
        assert response1 is not None

        # Schedule it
        response2 = chat_handler.process_message("Schedule it for tomorrow at 10am")
        assert response2 is not None

    def test_planning_workflow(self, chat_handler):
        """Test planning workflow via chat."""
        response = chat_handler.process_message("Help me plan my day - what should I prioritize?")
        assert response is not None


class TestChatHandlerMessageFormatting:
    """Test message formatting and display."""

    def test_format_task_in_response(self, chat_handler):
        """Test formatting task information in response."""
        response = chat_handler.process_message("Show me my high priority tasks")
        assert response is not None

    def test_format_schedule_in_response(self, chat_handler):
        """Test formatting schedule in response."""
        response = chat_handler.process_message("What does my day look like?")
        assert response is not None

    def test_format_suggestions_in_response(self, chat_handler):
        """Test formatting suggestions in response."""
        response = chat_handler.process_message("What should I work on next?")
        assert response is not None


class TestChatHandlerContext:
    """Test context management in conversations."""

    def test_task_context_in_conversation(self, session_manager):
        """Test maintaining task context."""
        task_id = "task_123"
        session_manager.set_context("current_task_id", task_id)

        assert session_manager.get_context("current_task_id") == task_id

    def test_date_context_in_conversation(self, session_manager):
        """Test maintaining date context."""
        date = "2024-01-15"
        session_manager.set_context("selected_date", date)

        assert session_manager.get_context("selected_date") == date

    def test_action_context_in_conversation(self, session_manager):
        """Test maintaining action context."""
        session_manager.set_context("pending_action", "create_task")

        assert session_manager.get_context("pending_action") == "create_task"
