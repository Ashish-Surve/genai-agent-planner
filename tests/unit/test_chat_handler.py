"""Tests for ChatHandler."""

from unittest.mock import MagicMock

from adhd_planner.core.chat_handler import ChatHandler


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
