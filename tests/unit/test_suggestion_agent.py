"""Tests for Suggestion Agent."""

from unittest.mock import MagicMock, Mock

import pytest
from models.enums import EnergyLevel, Priority

from adhd_planner.agents.suggestion_agent import SuggestionAgent
from adhd_planner.graph.state_utils import StateManager


class TestSuggestionAgent:
    """Test suggestion agent functionality."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
            "calendar_service": Mock(),
        }

    @pytest.fixture
    def suggestion_agent(self, mock_services):
        """Create suggestion agent with mocks."""
        return SuggestionAgent(**mock_services)

    def test_initialization(self, suggestion_agent):
        """Test agent initialization."""
        assert suggestion_agent.name == "suggestion_agent"
        assert suggestion_agent.description == "Recommends tasks to work on"

    def test_get_suggestions(self, suggestion_agent, mock_services):
        """Test task suggestions."""
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.title = "Urgent task"
        mock_task1.priority = Priority.HIGH
        mock_task1.energy_level = EnergyLevel.HIGH
        mock_task1.estimated_duration_minutes = 60
        mock_task1.deadline = None

        mock_task2 = MagicMock()
        mock_task2.id = 2
        mock_task2.title = "Regular task"
        mock_task2.priority = Priority.MEDIUM
        mock_task2.energy_level = EnergyLevel.MEDIUM
        mock_task2.estimated_duration_minutes = 45
        mock_task2.deadline = None

        mock_services["task_service"].get_incomplete_tasks.return_value = [
            mock_task1,
            mock_task2,
        ]

        state = StateManager.create_initial_state("What should I work on?")
        result = suggestion_agent.execute(state)

        assert result["routing_decision"] == "END"
        assert len(result["messages"]) == 2
        assert "Recommended Tasks" in result["messages"][1].content

    def test_no_tasks_available(self, suggestion_agent, mock_services):
        """Test when no tasks are available."""
        mock_services["task_service"].get_incomplete_tasks.return_value = []

        state = StateManager.create_initial_state("What should I work on?")
        result = suggestion_agent.execute(state)

        assert result["routing_decision"] == "END"
        assert "No tasks available" in result["messages"][1].content

    def test_error_handling(self, suggestion_agent, mock_services):
        """Test error handling."""
        mock_services["task_service"].get_incomplete_tasks.side_effect = Exception("Service error")

        state = StateManager.create_initial_state("What should I work on?")
        result = suggestion_agent.execute(state)

        assert result["error"] is not None
