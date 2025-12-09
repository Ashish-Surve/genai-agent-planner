"""Node functions for LangGraph workflow."""

from adhd_planner.graph.state import AgentState


def create_node_functions(agents_dict: dict):
    """
    Create node functions for all agents.

    Args:
        agents_dict: Dictionary with agent instances

    Returns:
        Dictionary of node functions
    """

    def supervisor_node(state: AgentState) -> AgentState:
        """Supervisor node."""
        state["current_agent"] = "supervisor"
        return agents_dict["supervisor"].execute(state)

    def planning_agent_node(state: AgentState) -> AgentState:
        """Planning agent node."""
        state["current_agent"] = "planning_agent"
        return agents_dict["planning_agent"].execute(state)

    def scheduling_agent_node(state: AgentState) -> AgentState:
        """Scheduling agent node."""
        state["current_agent"] = "scheduling_agent"
        return agents_dict["scheduling_agent"].execute(state)

    def suggestion_agent_node(state: AgentState) -> AgentState:
        """Suggestion agent node."""
        state["current_agent"] = "suggestion_agent"
        return agents_dict["suggestion_agent"].execute(state)

    return {
        "supervisor": supervisor_node,
        "planning_agent": planning_agent_node,
        "scheduling_agent": scheduling_agent_node,
        "suggestion_agent": suggestion_agent_node,
    }
