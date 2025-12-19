"""Graph builder for LangGraph workflow."""

from langgraph.graph import END, StateGraph

from adhd_planner.graph.edges import route_to_agent
from adhd_planner.graph.state import AgentState
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)


def build_graph():
    """
    Build and return the compiled LangGraph.

    This is a convenience function for simple graph building.
    For more control, use GraphBuilder directly.
    """
    from adhd_planner.database.connection import get_db
    from adhd_planner.services.calendar_service import CalendarService
    from adhd_planner.services.llm_service import get_llm_service
    from adhd_planner.services.task_service import TaskService

    # Initialize services
    llm_service = get_llm_service()
    db = get_db()
    session = db.session_factory()

    task_service = TaskService(session)
    calendar_service = CalendarService(session)

    # Build graph
    builder = GraphBuilder(llm_service, task_service, calendar_service)
    return builder.build_graph()


class GraphBuilder:
    """Builds and manages the LangGraph workflow."""

    def __init__(
        self,
        llm_service,
        task_service,
        calendar_service,
    ):
        """
        Initialize graph builder with services.

        Args:
            llm_service: LLM service instance
            task_service: Task service instance
            calendar_service: Calendar service instance
        """
        self.llm_service = llm_service
        self.task_service = task_service
        self.calendar_service = calendar_service
        self.agents_dict = None
        self.graph = None
        self.compiled_graph = None

    def build_graph(self):
        """Build the LangGraph."""
        # Lazy import to avoid circular imports
        from adhd_planner.agents.planning_agent import PlanningAgent
        from adhd_planner.agents.scheduling_agent import SchedulingAgent
        from adhd_planner.agents.suggestion_agent import SuggestionAgent
        from adhd_planner.agents.supervisor import SupervisorAgent
        from adhd_planner.graph.nodes import create_node_functions

        # Create agent instances
        self.agents_dict = {
            "supervisor": SupervisorAgent(llm_service=self.llm_service),
            "planning_agent": PlanningAgent(
                llm_service=self.llm_service,
                task_service=self.task_service,
            ),
            "scheduling_agent": SchedulingAgent(
                llm_service=self.llm_service,
                task_service=self.task_service,
                calendar_service=self.calendar_service,
            ),
            "suggestion_agent": SuggestionAgent(
                llm_service=self.llm_service,
                task_service=self.task_service,
                calendar_service=self.calendar_service,
            ),
        }

        # Create node functions
        nodes = create_node_functions(self.agents_dict)

        # Create graph
        self.graph = StateGraph(AgentState)

        # Add nodes
        for node_name, node_func in nodes.items():
            self.graph.add_node(node_name, node_func)

        # Add conditional edges from supervisor
        self.graph.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {
                "planning_agent": "planning_agent",
                "scheduling_agent": "scheduling_agent",
                "suggestion_agent": "suggestion_agent",
                "END": END,
            },
        )

        # Add edges from specialist agents to END
        self.graph.add_edge("planning_agent", END)
        self.graph.add_edge("scheduling_agent", END)
        self.graph.add_edge("suggestion_agent", END)

        # Set entry point
        self.graph.set_entry_point("supervisor")

        # Compile graph
        self.compiled_graph = self.graph.compile()

        logger.info("LangGraph built and compiled successfully")
        return self.compiled_graph

    def invoke(self, user_input: str) -> dict:
        """
        Invoke the graph with user input.

        Args:
            user_input: User's input message

        Returns:
            Final state after graph execution
        """
        if not self.compiled_graph:
            self.build_graph()

        from adhd_planner.graph.state_utils import StateManager

        initial_state = StateManager.create_initial_state(user_input)

        result = self.compiled_graph.invoke(initial_state)

        logger.info(f"Graph execution completed with routing: {result.get('routing_decision')}")
        return result

    def get_graph(self):
        """Get the compiled graph."""
        if not self.compiled_graph:
            self.build_graph()
        return self.compiled_graph
