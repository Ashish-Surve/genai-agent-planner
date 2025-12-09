"""Tests for Supervisor Agent."""

import json
import pytest
from unittest.mock import Mock

from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.graph.state_utils import StateManager


class TestSupervisorAgent:
    """Test supervisor agent routing and classification."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create mock LLM service."""
        service = Mock()
        return service

    @pytest.fixture
    def supervisor(self, mock_llm_service):
        """Create supervisor agent with mock LLM."""
        return SupervisorAgent(llm_service=mock_llm_service)

    def test_initialization(self, supervisor):
        """Test supervisor initialization."""
        assert supervisor.name == "supervisor"
        assert supervisor.description == "Routes requests to specialized agents"

    def test_route_to_planning_agent(self, supervisor, mock_llm_service):
        """Test routing to planning agent."""
        # Mock LLM response
        routing_response = {
            "intent": "Create a new task",
            "agent": "planning_agent",
            "reasoning": "User wants to create a task",
            "needs_context": ["tasks"],
        }
        mock_llm_service.generate.return_value = json.dumps(routing_response)

        # Create state
        state = StateManager.create_initial_state("Add task: write report")

        # Execute
        result = supervisor.execute(state)

        # Verify routing decision
        assert result["routing_decision"] == "planning_agent"
        assert result["context"]["supervisor_analysis"]["agent"] == "planning_agent"

    def test_route_to_scheduling_agent(self, supervisor, mock_llm_service):
        """Test routing to scheduling agent."""
        routing_response = {
            "intent": "Plan the day",
            "agent": "scheduling_agent",
            "reasoning": "User wants daily schedule",
            "needs_context": ["tasks", "calendar"],
        }
        mock_llm_service.generate.return_value = json.dumps(routing_response)

        state = StateManager.create_initial_state("Plan my day")
        result = supervisor.execute(state)

        assert result["routing_decision"] == "scheduling_agent"

    def test_route_to_suggestion_agent(self, supervisor, mock_llm_service):
        """Test routing to suggestion agent."""
        routing_response = {
            "intent": "Get task recommendation",
            "agent": "suggestion_agent",
            "reasoning": "User wants task suggestion",
            "needs_context": ["tasks", "energy_level"],
        }
        mock_llm_service.generate.return_value = json.dumps(routing_response)

        state = StateManager.create_initial_state("What should I work on?")
        result = supervisor.execute(state)

        assert result["routing_decision"] == "suggestion_agent"

    def test_direct_response(self, supervisor, mock_llm_service):
        """Test direct response without routing."""
        # First call for routing decision
        routing_response = {
            "intent": "Greeting",
            "agent": "direct_response",
            "reasoning": "Simple greeting",
            "needs_context": [],
        }
        # Second call for actual response
        direct_response = "Hello! How can I help you today?"

        mock_llm_service.generate.side_effect = [
            json.dumps(routing_response),
            direct_response,
        ]

        state = StateManager.create_initial_state("Hello!")
        result = supervisor.execute(state)

        # Should end conversation with direct response
        assert result["routing_decision"] == "END"
        assert len(result["messages"]) == 2  # User message + AI response

    def test_invalid_json_fallback(self, supervisor, mock_llm_service):
        """Test fallback when LLM returns invalid JSON."""
        # Return invalid JSON
        mock_llm_service.generate.side_effect = [
            "This is not JSON",
            "I'm not sure what you mean.",
        ]

        state = StateManager.create_initial_state("Some input")
        result = supervisor.execute(state)

        # Should fallback to direct response
        assert result["routing_decision"] == "END"

    def test_invalid_agent_name_fallback(self, supervisor, mock_llm_service):
        """Test fallback when LLM returns invalid agent name."""
        routing_response = {
            "intent": "Something",
            "agent": "invalid_agent_name",
            "reasoning": "Invalid",
            "needs_context": [],
        }

        mock_llm_service.generate.side_effect = [
            json.dumps(routing_response),
            "Let me help you with that.",
        ]

        state = StateManager.create_initial_state("Test")
        result = supervisor.execute(state)

        # Should use direct_response and end
        assert result["routing_decision"] == "END"

    def test_conversation_context(self, supervisor, mock_llm_service):
        """Test that conversation history is included in routing."""
        routing_response = {
            "intent": "Follow up",
            "agent": "planning_agent",
            "reasoning": "Follow-up to previous conversation",
            "needs_context": ["tasks"],
        }
        mock_llm_service.generate.return_value = json.dumps(routing_response)

        # Create state with message history
        state = StateManager.create_initial_state("Add another task")
        state = StateManager.add_ai_message(
            state, "I added your task", "planning_agent"
        )

        result = supervisor.execute(state)

        # Verify LLM was called with context
        call_args = mock_llm_service.generate.call_args
        prompt = call_args.kwargs["prompt"]
        assert "User:" in prompt or "Assistant:" in prompt  # Has conversation context

    def test_error_handling(self, supervisor, mock_llm_service):
        """Test error handling."""
        # Make LLM service raise exception
        mock_llm_service.generate.side_effect = Exception("LLM service error")

        state = StateManager.create_initial_state("Test")
        result = supervisor.execute(state)

        # Should have error in state
        assert result["error"] is not None
        assert "supervisor" in result["error"]
