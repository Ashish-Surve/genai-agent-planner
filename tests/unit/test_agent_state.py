"""Tests for AgentState and StateManager."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from adhd_planner.graph.state import AgentState
from adhd_planner.graph.state_utils import StateManager


class TestStateManager:
    """Test StateManager utilities."""

    def test_create_initial_state(self):
        """Test creating initial state."""
        state = StateManager.create_initial_state("Hello, assistant!")

        assert state["user_input"] == "Hello, assistant!"
        assert state["current_agent"] == "supervisor"
        assert len(state["messages"]) == 1
        assert isinstance(state["messages"][0], HumanMessage)
        assert state["messages"][0].content == "Hello, assistant!"
        assert state["routing_decision"] is None
        assert state["error"] is None

    def test_add_message(self):
        """Test adding messages to state."""
        state = StateManager.create_initial_state("Test")

        # Add AI message
        ai_msg = AIMessage(content="Response")
        state = StateManager.add_message(state, ai_msg)

        assert len(state["messages"]) == 2
        assert state["messages"][1] == ai_msg

    def test_add_ai_message(self):
        """Test adding AI message with agent name."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.add_ai_message(state, "Agent response", "planning_agent")

        assert len(state["messages"]) == 2
        ai_message = state["messages"][1]
        assert isinstance(ai_message, AIMessage)
        assert ai_message.content == "Agent response"
        assert ai_message.additional_kwargs["agent"] == "planning_agent"

    def test_update_context(self):
        """Test updating context."""
        state = StateManager.create_initial_state("Test")

        state = StateManager.update_context(state, "tasks", [{"id": 1, "title": "Task 1"}])
        state = StateManager.update_context(state, "energy_level", "high")

        assert state["context"]["tasks"] == [{"id": 1, "title": "Task 1"}]
        assert state["context"]["energy_level"] == "high"

    def test_get_context(self):
        """Test getting context values."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.update_context(state, "key1", "value1")

        assert StateManager.get_context(state, "key1") == "value1"
        assert StateManager.get_context(state, "nonexistent") is None
        assert StateManager.get_context(state, "nonexistent", "default") == "default"

    def test_set_error(self):
        """Test setting error in state."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.set_error(state, "Something went wrong", "planning_agent")

        assert state["error"] == "Something went wrong"
        assert state["metadata"]["error_agent"] == "planning_agent"

    def test_set_routing_decision(self):
        """Test setting routing decision."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.set_routing_decision(state, "scheduling_agent")

        assert state["routing_decision"] == "scheduling_agent"

    def test_get_message_history(self):
        """Test getting message history."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.add_ai_message(state, "Response 1", "agent1")
        state = StateManager.add_ai_message(state, "Response 2", "agent2")
        state = StateManager.add_ai_message(state, "Response 3", "agent3")

        # Get all messages
        all_messages = StateManager.get_message_history(state)
        assert len(all_messages) == 4

        # Get last 2 messages
        last_2 = StateManager.get_message_history(state, last_n=2)
        assert len(last_2) == 2
        assert last_2[-1].content == "Response 3"

    def test_validate_state_success(self):
        """Test state validation with valid state."""
        state = StateManager.create_initial_state("Test")
        assert StateManager.validate_state(state) is True

    def test_validate_state_missing_field(self):
        """Test state validation with missing field."""
        invalid_state = AgentState(
            messages=[],
            user_input="test",
            # Missing current_agent
            routing_decision=None,
            context={},
            error=None,
            metadata={}
        )

        with pytest.raises(ValueError, match="missing required field"):
            StateManager.validate_state(invalid_state)

    def test_validate_state_invalid_messages(self):
        """Test state validation with invalid messages type."""
        invalid_state = AgentState(
            messages="not a list",  # Should be a sequence
            user_input="test",
            current_agent="supervisor",
            routing_decision=None,
            context={},
            error=None,
            metadata={}
        )

        with pytest.raises(ValueError, match="must be a sequence"):
            StateManager.validate_state(invalid_state)
