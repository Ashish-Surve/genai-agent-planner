"""Edge functions for LangGraph routing."""

from typing import Literal

from adhd_planner.graph.state import AgentState
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

# Type for valid agent routes
AgentRoute = Literal[
    "planning_agent",
    "scheduling_agent",
    "suggestion_agent",
    "sync_agent",
    "energy_agent",
    "END",
]


def route_to_agent(state: AgentState) -> AgentRoute:
    """
    Determine which agent to route to next based on supervisor's decision.

    This function is used as a conditional edge in the LangGraph.
    It reads the routing_decision from state and returns the agent name.

    Args:
        state: Current agent state with routing_decision set

    Returns:
        Name of the agent to route to, or "END" to finish
    """
    routing_decision = state.get("routing_decision")

    if not routing_decision:
        logger.warning("No routing decision found, ending conversation")
        return "END"

    # Map routing decision to actual agent
    # In the future, we might have more complex logic here
    valid_routes: list[AgentRoute] = [
        "planning_agent",
        "scheduling_agent",
        "suggestion_agent",
        "sync_agent",
        "energy_agent",
        "END",
    ]

    if routing_decision not in valid_routes:
        logger.error(
            f"Invalid routing decision: {routing_decision}, ending conversation"
        )
        return "END"

    logger.info(f"Routing to: {routing_decision}")
    return routing_decision  # type: ignore


def should_continue(state: AgentState) -> Literal["continue", "END"]:
    """
    Determine if the graph should continue or end.

    Args:
        state: Current agent state

    Returns:
        "continue" to keep processing, "END" to finish
    """
    # Check for errors
    if state.get("error"):
        logger.info("Error detected, ending conversation")
        return "END"

    # Check routing decision
    routing_decision = state.get("routing_decision")
    if routing_decision == "END":
        return "END"

    return "continue"


def route_after_specialist(state: AgentState) -> Literal["supervisor", "END"]:
    """
    Route after a specialist agent completes.

    Determines if we should route back to supervisor for further processing
    or end the conversation.

    Args:
        state: Current agent state

    Returns:
        "supervisor" to continue, "END" to finish
    """
    # Check if there's more to do
    needs_follow_up = state.get("context", {}).get("needs_follow_up", False)

    if needs_follow_up:
        logger.info("Follow-up needed, routing back to supervisor")
        return "supervisor"

    # Default: end conversation after specialist completes
    logger.info("No follow-up needed, ending conversation")
    return "END"
