"""Tests for Scheduling Agent."""

import pytest
from unittest.mock import Mock, MagicMock

from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.graph.state_utils import StateManager
from models.enums import Priority, EnergyLevel


class TestSchedulingAgent:
    """Test scheduling agent functionality."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
            "calendar_service": Mock(),
        }

    @pytest.fixture
    def scheduling_agent(self, mock_services):
        """Create scheduling agent with mocks."""
        return SchedulingAgent(**mock_services)

    def test_initialization(self, scheduling_agent):
        """Test agent initialization."""
        assert scheduling_agent.name == "scheduling_agent"
        assert scheduling_agent.description == "Generates ADHD-friendly schedules"

    def test_generate_schedule(self, scheduling_agent, mock_services):
        """Test schedule generation."""
        mock_task1 = MagicMock()
        mock_task1.id = 1
        mock_task1.title = "Write report"
        mock_task1.priority = Priority.HIGH
        mock_task1.energy_level = EnergyLevel.HIGH
        mock_task1.estimated_duration_minutes = 120
        mock_task1.deadline = None

        mock_task2 = MagicMock()
        mock_task2.id = 2
        mock_task2.title = "Review emails"
        mock_task2.priority = Priority.LOW
        mock_task2.energy_level = EnergyLevel.LOW
        mock_task2.estimated_duration_minutes = 30
        mock_task2.deadline = None

        mock_services["task_service"].get_incomplete_tasks.return_value = [
            mock_task1,
            mock_task2,
        ]

        state = StateManager.create_initial_state("Plan my day")
        result = scheduling_agent.execute(state)

        assert result["routing_decision"] == "END"
        assert len(result["messages"]) == 2
        assert "Suggested Schedule" in result["messages"][1].content

    def test_no_tasks_available(self, scheduling_agent, mock_services):
        """Test when no tasks are available."""
        mock_services["task_service"].get_incomplete_tasks.return_value = []

        state = StateManager.create_initial_state("Plan my day")
        result = scheduling_agent.execute(state)

        assert result["routing_decision"] == "END"
        assert "No tasks to schedule" in result["messages"][1].content

    def test_error_handling(self, scheduling_agent, mock_services):
        """Test error handling."""
        mock_services["task_service"].get_incomplete_tasks.side_effect = Exception(
            "Service error"
        )

        state = StateManager.create_initial_state("Plan my day")
        result = scheduling_agent.execute(state)

        assert result["error"] is not None
