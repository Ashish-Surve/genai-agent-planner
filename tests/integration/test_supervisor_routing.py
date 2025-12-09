"""Integration tests for supervisor routing."""

import pytest
from unittest.mock import Mock

from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.graph.edges import route_to_agent


class TestSupervisorIntegration:
    """Integration tests for supervisor with edge functions."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create mock LLM service with realistic responses."""
        service = Mock()

        # Set up realistic routing responses
        def generate_side_effect(*args, **kwargs):
            prompt = kwargs.get("prompt", "")

            if "add task" in prompt.lower() or "create task" in prompt.lower():
                return '{"intent": "Create task", "agent": "planning_agent", "reasoning": "Task creation", "needs_context": ["tasks"]}'
            elif "plan my day" in prompt.lower():
                return '{"intent": "Schedule day", "agent": "scheduling_agent", "reasoning": "Schedule generation", "needs_context": ["tasks", "calendar"]}'
            elif "what should i" in prompt.lower():
                return '{"intent": "Get suggestion", "agent": "suggestion_agent", "reasoning": "Task suggestion", "needs_context": ["tasks"]}'
            else:
                return '{"intent": "General query", "agent": "direct_response", "reasoning": "Direct response", "needs_context": []}'

        service.generate.side_effect = generate_side_effect
        return service

    @pytest.fixture
    def supervisor(self, mock_llm_service):
        """Create supervisor with mock LLM."""
        return SupervisorAgent(llm_service=mock_llm_service)

    def test_full_routing_flow_to_planning(self, supervisor):
        """Test complete flow: state → supervisor → edge → next agent."""
        # Create initial state
        state = StateManager.create_initial_state("Add task: write report")

        # Execute supervisor
        state = supervisor.execute(state)

        # Route to next agent
        next_agent = route_to_agent(state)

        # Verify flow
        assert state["routing_decision"] == "planning_agent"
        assert next_agent == "planning_agent"

    def test_full_routing_flow_to_scheduling(self, supervisor):
        """Test routing to scheduling agent."""
        state = StateManager.create_initial_state("Plan my day")
        state = supervisor.execute(state)
        next_agent = route_to_agent(state)

        assert next_agent == "scheduling_agent"

    def test_full_routing_flow_direct_response(self, supervisor, mock_llm_service):
        """Test direct response flow."""
        # Add response for direct handling
        responses = [
            '{"intent": "Greeting", "agent": "direct_response", "reasoning": "Simple greeting", "needs_context": []}',
            "Hello! How can I help?",
        ]
        mock_llm_service.generate.side_effect = responses

        state = StateManager.create_initial_state("Hello")
        state = supervisor.execute(state)
        next_agent = route_to_agent(state)

        # Should end after direct response
        assert next_agent == "END"
        assert len(state["messages"]) == 2  # User + AI response
