"""Tests for Planning Agent."""

import json
from unittest.mock import MagicMock, Mock

import pytest
from models.enums import EnergyLevel, Priority

from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.graph.state_utils import StateManager


class TestPlanningAgent:
    """Test planning agent functionality."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
        }

    @pytest.fixture
    def planning_agent(self, mock_services):
        """Create planning agent with mocks."""
        return PlanningAgent(**mock_services)

    def test_initialization(self, planning_agent):
        """Test agent initialization."""
        assert planning_agent.name == "planning_agent"
        assert planning_agent.description == "Creates and modifies tasks from natural language"

    def test_extract_and_create_task(self, planning_agent, mock_services):
        """Test full task creation flow."""
        task_extraction = {
            "title": "Write report",
            "description": "Quarterly report",
            "estimated_duration_minutes": 120,
            "priority": "high",
            "energy_level": "high",
            "category": "work",
            "needs_clarification": False,
        }

        mock_services["llm_service"].generate.return_value = json.dumps(task_extraction)

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Write report"
        mock_task.description = "Quarterly report"
        mock_task.estimated_duration_minutes = 120
        mock_task.priority = Priority.HIGH
        mock_task.energy_level = EnergyLevel.HIGH
        mock_task.deadline = None
        mock_services["task_service"].create_task.return_value = mock_task

        state = StateManager.create_initial_state("Add task: write report, 2 hours")
        result = planning_agent.execute(state)

        assert mock_services["task_service"].create_task.called
        assert result["routing_decision"] == "END"
        assert len(result["messages"]) == 2
        assert "Write report" in result["messages"][1].content

    def test_needs_clarification(self, planning_agent, mock_services):
        """Test when agent needs clarification."""
        task_extraction = {
            "title": "",
            "needs_clarification": True,
            "clarification_question": "What task would you like to create?",
        }

        mock_services["llm_service"].generate.return_value = json.dumps(task_extraction)

        state = StateManager.create_initial_state("Add a task")
        result = planning_agent.execute(state)

        assert not mock_services["task_service"].create_task.called
        assert "What task would you like to create?" in result["messages"][1].content

    def test_error_handling(self, planning_agent, mock_services):
        """Test error handling."""
        mock_services["llm_service"].generate.side_effect = Exception("LLM error")

        state = StateManager.create_initial_state("Add task")
        result = planning_agent.execute(state)

        assert result["error"] is not None
        assert "planning_agent" in result["error"]
