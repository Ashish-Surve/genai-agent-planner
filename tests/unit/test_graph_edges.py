"""Tests for graph edge functions."""

import pytest

from adhd_planner.graph.edges import (
    route_to_agent,
    should_continue,
    route_after_specialist,
)
from adhd_planner.graph.state_utils import StateManager


class TestEdgeFunctions:
    """Test graph edge routing functions."""

    def test_route_to_planning_agent(self):
        """Test routing to planning agent."""
        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "planning_agent"

        result = route_to_agent(state)
        assert result == "planning_agent"

    def test_route_to_scheduling_agent(self):
        """Test routing to scheduling agent."""
        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "scheduling_agent"

        result = route_to_agent(state)
        assert result == "scheduling_agent"

    def test_route_to_end(self):
        """Test routing to END."""
        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "END"

        result = route_to_agent(state)
        assert result == "END"

    def test_route_with_no_decision(self):
        """Test routing when no decision is set."""
        state = StateManager.create_initial_state("Test")
        # Don't set routing_decision

        result = route_to_agent(state)
        assert result == "END"  # Should default to END

    def test_route_with_invalid_decision(self):
        """Test routing with invalid agent name."""
        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "invalid_agent"

        result = route_to_agent(state)
        assert result == "END"  # Should fallback to END

    def test_should_continue_with_no_error(self):
        """Test should_continue with no error."""
        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "planning_agent"

        result = should_continue(state)
        assert result == "continue"

    def test_should_continue_with_error(self):
        """Test should_continue with error."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.set_error(state, "Test error", "test_agent")

        result = should_continue(state)
        assert result == "END"

    def test_should_continue_with_end_routing(self):
        """Test should_continue when routing is END."""
        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "END"

        result = should_continue(state)
        assert result == "END"

    def test_route_after_specialist_with_follow_up(self):
        """Test routing back to supervisor when follow-up needed."""
        state = StateManager.create_initial_state("Test")
        state = StateManager.update_context(state, "needs_follow_up", True)

        result = route_after_specialist(state)
        assert result == "supervisor"

    def test_route_after_specialist_no_follow_up(self):
        """Test ending after specialist when no follow-up needed."""
        state = StateManager.create_initial_state("Test")

        result = route_after_specialist(state)
        assert result == "END"
