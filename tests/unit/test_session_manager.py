"""Tests for SessionManager."""

from unittest.mock import patch

import pytest


class TestSessionManager:
    """Test SessionManager functionality."""

    @pytest.fixture
    def mock_session_state(self):
        """Create mock session state."""
        return {}

    @patch("streamlit.session_state", new_callable=dict)
    def test_initialize(self, mock_state):
        """Test session initialization."""
        from adhd_planner.core.session_manager import SessionManager

        SessionManager.initialize()

        assert mock_state.get("initialized") is True
        assert mock_state.get("user_id") == "default_user"
        assert mock_state.get("messages") == []

    @patch("streamlit.session_state", new_callable=dict)
    def test_get_and_set(self, mock_state):
        """Test get and set operations."""
        from adhd_planner.core.session_manager import SessionManager

        SessionManager.set("test_key", "test_value")
        assert SessionManager.get("test_key") == "test_value"
        assert SessionManager.get("missing_key", "default") == "default"

    @patch("streamlit.session_state", new_callable=dict)
    def test_message_management(self, mock_state):
        """Test message add and get."""
        from adhd_planner.core.session_manager import SessionManager

        mock_state["messages"] = []

        SessionManager.add_message("user", "Hello")
        SessionManager.add_message("assistant", "Hi there!")

        messages = SessionManager.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["content"] == "Hi there!"

    @patch("streamlit.session_state", new_callable=dict)
    def test_clear_messages(self, mock_state):
        """Test clearing messages."""
        from adhd_planner.core.session_manager import SessionManager

        mock_state["messages"] = [{"role": "user", "content": "test"}]

        SessionManager.clear_messages()

        assert mock_state["messages"] == []
