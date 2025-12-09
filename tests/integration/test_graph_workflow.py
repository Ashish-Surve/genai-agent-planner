"""Integration tests for graph workflow."""

import pytest
from unittest.mock import Mock, MagicMock

from adhd_planner.graph.builder import GraphBuilder
from models.enums import Priority, EnergyLevel


class TestGraphWorkflow:
    """Test end-to-end graph workflow."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
            "calendar_service": Mock(),
        }

    @pytest.fixture
    def graph_builder(self, mock_services):
        """Create graph builder with mocks."""
        return GraphBuilder(**mock_services)

    def test_graph_builds_successfully(self, graph_builder):
        """Test that graph builds without errors."""
        graph = graph_builder.build_graph()
        assert graph is not None
        assert graph_builder.compiled_graph is not None

    def test_graph_routing_to_planning_agent(self, graph_builder, mock_services):
        """Test graph routing to planning agent."""
        # Mock routing decision
        import json

        routing_response = {
            "intent": "Create a new task",
            "agent": "planning_agent",
            "reasoning": "User wants to create a task",
            "needs_context": ["tasks"],
        }

        task_extraction = {
            "title": "Test task",
            "estimated_duration_minutes": 60,
            "priority": "medium",
            "energy_level": "medium",
            "category": "work",
            "needs_clarification": False,
        }

        mock_services["llm_service"].generate.side_effect = [
            json.dumps(routing_response),  # Supervisor routing
            json.dumps(task_extraction),  # Planning extraction
        ]

        # Mock task creation
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Test task"
        mock_task.estimated_duration_minutes = 60
        mock_task.priority = Priority.MEDIUM
        mock_task.energy_level = EnergyLevel.MEDIUM
        mock_task.deadline = None
        mock_services["task_service"].create_task.return_value = mock_task

        # Invoke graph
        result = graph_builder.invoke("Add task: test task")

        # Verify execution
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 1

    def test_graph_get_compiled_graph(self, graph_builder):
        """Test getting compiled graph."""
        graph = graph_builder.get_graph()
        assert graph is not None
        assert graph_builder.compiled_graph is not None

    def test_graph_caches_compiled_graph(self, graph_builder):
        """Test that graph is cached after first build."""
        graph1 = graph_builder.get_graph()
        graph2 = graph_builder.get_graph()
        assert graph1 is graph2  # Same object
