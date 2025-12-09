"""Tests for BaseAgent."""

import pytest

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.graph.state_utils import StateManager


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def execute(self, state: AgentState) -> AgentState:
        """Mock execution."""
        self.log_execution(state)
        return self.add_response(state, f"{self.name} executed successfully")


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_initialization(self):
        """Test agent initialization."""
        agent = MockAgent(
            name="test_agent",
            description="A test agent",
            test_service="mock_service"
        )

        assert agent.name == "test_agent"
        assert agent.description == "A test agent"
        assert agent.services["test_service"] == "mock_service"
        assert agent.state_manager is not None

    def test_get_service_success(self):
        """Test getting a service successfully."""
        agent = MockAgent(
            name="test_agent",
            description="Test",
            task_service="TaskService",
            llm_service="LLMService"
        )

        assert agent.get_service("task_service") == "TaskService"
        assert agent.get_service("llm_service") == "LLMService"

    def test_get_service_missing(self):
        """Test getting a missing service raises error."""
        agent = MockAgent(name="test_agent", description="Test")

        with pytest.raises(ValueError, match="missing required service"):
            agent.get_service("nonexistent_service")

    def test_execute(self):
        """Test agent execution."""
        agent = MockAgent(name="test_agent", description="Test")
        state = StateManager.create_initial_state("Test input")

        result = agent.execute(state)

        # Should have added a response message
        assert len(result["messages"]) == 2
        assert result["messages"][1].content == "test_agent executed successfully"

    def test_handle_error(self):
        """Test error handling."""
        agent = MockAgent(name="test_agent", description="Test")
        state = StateManager.create_initial_state("Test")

        error = ValueError("Test error")
        result = agent.handle_error(state, error)

        assert result["error"] is not None
        assert "test_agent" in result["error"]
        assert "Test error" in result["error"]

    def test_add_response(self):
        """Test adding a response."""
        agent = MockAgent(name="test_agent", description="Test")
        state = StateManager.create_initial_state("Test")

        result = agent.add_response(state, "Agent response")

        assert len(result["messages"]) == 2
        assert result["messages"][1].content == "Agent response"
        assert result["messages"][1].additional_kwargs["agent"] == "test_agent"

    def test_get_context(self):
        """Test getting context."""
        agent = MockAgent(name="test_agent", description="Test")
        state = StateManager.create_initial_state("Test")
        state = StateManager.update_context(state, "key1", "value1")

        assert agent.get_context(state, "key1") == "value1"
        assert agent.get_context(state, "missing", "default") == "default"

    def test_update_context(self):
        """Test updating context."""
        agent = MockAgent(name="test_agent", description="Test")
        state = StateManager.create_initial_state("Test")

        result = agent.update_context(state, "tasks", [{"id": 1}])

        assert result["context"]["tasks"] == [{"id": 1}]

    def test_repr(self):
        """Test string representation."""
        agent = MockAgent(name="test_agent", description="Test")

        assert repr(agent) == "<MockAgent(name=test_agent)>"
