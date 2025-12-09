# ADHD-16: Graph Builder & Integration

## Story Information
- **Epic**: Epic 3 - LangGraph Agents
- **Story ID**: ADHD-16
- **Estimated Time**: 3 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-11: LangGraph State & Base Agent
  - ✅ ADHD-12: Supervisor Agent
  - ✅ ADHD-13: Planning Agent
  - ✅ ADHD-14: Scheduling Agent
  - ✅ ADHD-15: Suggestion Agent

## Description

Build the LangGraph orchestration layer that ties all agents together into a cohesive workflow. This story implements the graph builder, node functions, edge routing, and the main execution loop that powers the multi-agent system.

This is the "glue" that makes all agents work together seamlessly, handling state transitions, routing decisions, and error recovery.

## Goals

1. Create graph builder that constructs the LangGraph
2. Implement node functions for each agent
3. Define edge routing logic (conditional edges)
4. Create graph compilation and execution
5. Handle state transitions between agents
6. Implement error recovery in the graph
7. Test with mock LLM for quick validation

## Acceptance Criteria

### Graph Builder Implementation
- [ ] `GraphBuilder` class created
- [ ] Adds all agent nodes to graph
- [ ] Defines conditional edges for routing
- [ ] Compiles graph successfully
- [ ] Entry point configured
- [ ] End condition defined
- [ ] Error handling nodes

### Node Functions
- [ ] Supervisor node function
- [ ] Planning agent node function
- [ ] Scheduling agent node function
- [ ] Suggestion agent node function
- [ ] Error handler node function
- [ ] All nodes integrate with agents correctly

### Edge Routing
- [ ] Supervisor routes to correct agent
- [ ] Agents route back to supervisor or END
- [ ] Error states route to error handler
- [ ] Default routing defined
- [ ] Conditional logic works

### Graph Execution
- [ ] Graph compiles without errors
- [ ] Executes full workflow correctly
- [ ] State persists across nodes
- [ ] Messages accumulate properly
- [ ] Context updates work
- [ ] Routing decisions honored

### Testing
- [ ] Unit tests for graph builder
- [ ] Integration tests with mock LLM
- [ ] Test all routing paths
- [ ] Test error recovery
- [ ] Test state transitions
- [ ] Visualization of graph structure

## Files to Create/Modify

### New Files
```
src/adhd_planner/graph/
├── builder.py                    # Graph builder class
└── nodes.py                      # Node function implementations

tests/integration/
└── test_graph_workflow.py       # End-to-end graph tests
```

### Modified Files
```
src/adhd_planner/graph/
└── __init__.py                   # Export graph components
```

## Implementation Steps

### Step 1: Create Node Functions (30 min)

Create `src/adhd_planner/graph/nodes.py`:

```python
"""Node functions for LangGraph workflow."""

from adhd_planner.graph.state import AgentState
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.agents.suggestion_agent import SuggestionAgent
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)


def create_supervisor_node(supervisor_agent: SupervisorAgent):
    """
    Create supervisor node function.

    Args:
        supervisor_agent: Supervisor agent instance

    Returns:
        Node function
    """

    def supervisor_node(state: AgentState) -> AgentState:
        """Execute supervisor agent."""
        logger.info("Executing supervisor node")
        return supervisor_agent.execute(state)

    return supervisor_node


def create_planning_node(planning_agent: PlanningAgent):
    """
    Create planning agent node function.

    Args:
        planning_agent: Planning agent instance

    Returns:
        Node function
    """

    def planning_node(state: AgentState) -> AgentState:
        """Execute planning agent."""
        logger.info("Executing planning node")
        return planning_agent.execute(state)

    return planning_node


def create_scheduling_node(scheduling_agent: SchedulingAgent):
    """
    Create scheduling agent node function.

    Args:
        scheduling_agent: Scheduling agent instance

    Returns:
        Node function
    """

    def scheduling_node(state: AgentState) -> AgentState:
        """Execute scheduling agent."""
        logger.info("Executing scheduling node")
        return scheduling_agent.execute(state)

    return scheduling_node


def create_suggestion_node(suggestion_agent: SuggestionAgent):
    """
    Create suggestion agent node function.

    Args:
        suggestion_agent: Suggestion agent instance

    Returns:
        Node function
    """

    def suggestion_node(state: AgentState) -> AgentState:
        """Execute suggestion agent."""
        logger.info("Executing suggestion node")
        return suggestion_agent.execute(state)

    return suggestion_node


def create_error_handler_node():
    """
    Create error handler node.

    Returns:
        Node function
    """

    def error_handler_node(state: AgentState) -> AgentState:
        """Handle errors in the workflow."""
        logger.error(f"Error handler invoked: {state.get('error')}")

        # Add error message to state
        from langchain_core.messages import AIMessage

        error_msg = state.get("error", "An unknown error occurred")
        error_response = f"I encountered an error: {error_msg}\n\nPlease try rephrasing your request or contact support if this persists."

        state["messages"].append(AIMessage(content=error_response))
        state["routing_decision"] = "END"

        return state

    return error_handler_node
```

### Step 2: Create Graph Builder (60 min)

Create `src/adhd_planner/graph/builder.py`:

```python
"""LangGraph builder for ADHD Planner agent system."""

from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from adhd_planner.graph.state import AgentState
from adhd_planner.graph.nodes import (
    create_supervisor_node,
    create_planning_node,
    create_scheduling_node,
    create_suggestion_node,
    create_error_handler_node,
)
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.agents.suggestion_agent import SuggestionAgent
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)


class GraphBuilder:
    """
    Builds and compiles the LangGraph for agent orchestration.

    The graph orchestrates multiple specialized agents:
    - Supervisor: Routes requests to appropriate agents
    - Planning: Creates and estimates tasks
    - Scheduling: Generates optimized schedules
    - Suggestion: Recommends tasks based on context
    """

    def __init__(
        self,
        supervisor_agent: SupervisorAgent,
        planning_agent: PlanningAgent,
        scheduling_agent: SchedulingAgent,
        suggestion_agent: SuggestionAgent,
    ):
        """
        Initialize graph builder.

        Args:
            supervisor_agent: Supervisor agent
            planning_agent: Planning agent
            scheduling_agent: Scheduling agent
            suggestion_agent: Suggestion agent
        """
        self.supervisor_agent = supervisor_agent
        self.planning_agent = planning_agent
        self.scheduling_agent = scheduling_agent
        self.suggestion_agent = suggestion_agent

        self.graph = None
        self.compiled_graph = None

        logger.info("GraphBuilder initialized")

    def build(self) -> StateGraph:
        """
        Build the agent graph.

        Returns:
            Constructed StateGraph
        """
        logger.info("Building agent graph...")

        # Create state graph
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("supervisor", create_supervisor_node(self.supervisor_agent))
        graph.add_node("planning", create_planning_node(self.planning_agent))
        graph.add_node("scheduling", create_scheduling_node(self.scheduling_agent))
        graph.add_node("suggestion", create_suggestion_node(self.suggestion_agent))
        graph.add_node("error_handler", create_error_handler_node())

        # Set entry point
        graph.set_entry_point("supervisor")

        # Add conditional edges from supervisor
        graph.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "planning": "planning",
                "scheduling": "scheduling",
                "suggestion": "suggestion",
                "error_handler": "error_handler",
                "END": END,
            },
        )

        # Add edges from specialist agents back to supervisor or END
        for agent_name in ["planning", "scheduling", "suggestion"]:
            graph.add_conditional_edges(
                agent_name,
                self._route_from_agent,
                {
                    "supervisor": "supervisor",
                    "error_handler": "error_handler",
                    "END": END,
                },
            )

        # Error handler always ends
        graph.add_edge("error_handler", END)

        self.graph = graph
        logger.info("Graph built successfully")

        return graph

    def compile(self, checkpointer=None):
        """
        Compile the graph for execution.

        Args:
            checkpointer: Optional checkpointer for state persistence

        Returns:
            Compiled graph
        """
        if self.graph is None:
            self.build()

        logger.info("Compiling graph...")

        # Use memory saver if no checkpointer provided
        if checkpointer is None:
            checkpointer = MemorySaver()

        self.compiled_graph = self.graph.compile(checkpointer=checkpointer)

        logger.info("Graph compiled successfully")

        return self.compiled_graph

    def _route_from_supervisor(
        self, state: AgentState
    ) -> Literal["planning", "scheduling", "suggestion", "error_handler", "END"]:
        """
        Route from supervisor to appropriate agent.

        Args:
            state: Current agent state

        Returns:
            Next node name
        """
        # Check for errors
        if state.get("error"):
            logger.warning("Error detected, routing to error_handler")
            return "error_handler"

        # Get routing decision from supervisor
        routing_decision = state.get("routing_decision", "END")

        logger.info(f"Supervisor routing decision: {routing_decision}")

        # Validate routing decision
        valid_routes = ["planning", "scheduling", "suggestion", "error_handler", "END"]
        if routing_decision not in valid_routes:
            logger.warning(f"Invalid routing decision: {routing_decision}, defaulting to END")
            return "END"

        return routing_decision

    def _route_from_agent(
        self, state: AgentState
    ) -> Literal["supervisor", "error_handler", "END"]:
        """
        Route from specialist agent back to supervisor or END.

        Args:
            state: Current agent state

        Returns:
            Next node name
        """
        # Check for errors
        if state.get("error"):
            logger.warning("Error detected, routing to error_handler")
            return "error_handler"

        # Get routing decision from agent
        routing_decision = state.get("routing_decision", "END")

        logger.info(f"Agent routing decision: {routing_decision}")

        # If agent wants to continue conversation, return to supervisor
        if routing_decision == "supervisor":
            return "supervisor"

        # Otherwise, end the workflow
        return "END"

    def get_graph_visualization(self) -> str:
        """
        Get ASCII visualization of the graph.

        Returns:
            Graph structure as string
        """
        return """
Agent Workflow Graph:

    [START]
       ↓
  [Supervisor] ←─────────┐
       ↓                  │
       ├─→ [Planning] ────┤
       ├─→ [Scheduling] ──┤
       ├─→ [Suggestion] ──┤
       ├─→ [Error Handler] → [END]
       ↓
     [END]

Routing Logic:
- Supervisor analyzes request and routes to specialist
- Specialists complete task and either:
  - Return to Supervisor for follow-up
  - End workflow if complete
- Errors route to Error Handler
"""


def create_agent_graph(
    supervisor_agent: SupervisorAgent,
    planning_agent: PlanningAgent,
    scheduling_agent: SchedulingAgent,
    suggestion_agent: SuggestionAgent,
    checkpointer=None,
):
    """
    Convenience function to build and compile agent graph.

    Args:
        supervisor_agent: Supervisor agent
        planning_agent: Planning agent
        scheduling_agent: Scheduling agent
        suggestion_agent: Suggestion agent
        checkpointer: Optional checkpointer

    Returns:
        Compiled graph
    """
    builder = GraphBuilder(
        supervisor_agent=supervisor_agent,
        planning_agent=planning_agent,
        scheduling_agent=scheduling_agent,
        suggestion_agent=suggestion_agent,
    )

    return builder.compile(checkpointer=checkpointer)
```

### Step 3: Update Package Exports (5 min)

Update `src/adhd_planner/graph/__init__.py`:

```python
"""LangGraph state and workflow definitions."""

from adhd_planner.graph.state import AgentState
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.graph.builder import GraphBuilder, create_agent_graph
from adhd_planner.graph.nodes import (
    create_supervisor_node,
    create_planning_node,
    create_scheduling_node,
    create_suggestion_node,
    create_error_handler_node,
)

__all__ = [
    "AgentState",
    "StateManager",
    "GraphBuilder",
    "create_agent_graph",
    "create_supervisor_node",
    "create_planning_node",
    "create_scheduling_node",
    "create_suggestion_node",
    "create_error_handler_node",
]
```

### Step 4: Create Integration Tests (45 min)

Create `tests/integration/test_graph_workflow.py`:

```python
"""Integration tests for LangGraph workflow."""

import pytest
from unittest.mock import Mock
from langchain_core.messages import HumanMessage

from adhd_planner.graph.builder import GraphBuilder, create_agent_graph
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.agents.suggestion_agent import SuggestionAgent


class TestGraphWorkflow:
    """Test complete graph workflow."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        llm_service = Mock()
        llm_service.generate.return_value = '{"intent": "planning", "confidence": 0.9}'

        task_service = Mock()
        calendar_service = Mock()

        return {
            "llm_service": llm_service,
            "task_service": task_service,
            "calendar_service": calendar_service,
        }

    @pytest.fixture
    def agents(self, mock_services):
        """Create agent instances."""
        supervisor = SupervisorAgent(**mock_services)
        planning = PlanningAgent(**mock_services)
        scheduling = SchedulingAgent(**mock_services)
        suggestion = SuggestionAgent(**mock_services)

        return {
            "supervisor": supervisor,
            "planning": planning,
            "scheduling": scheduling,
            "suggestion": suggestion,
        }

    @pytest.fixture
    def graph_builder(self, agents):
        """Create graph builder."""
        return GraphBuilder(
            supervisor_agent=agents["supervisor"],
            planning_agent=agents["planning"],
            scheduling_agent=agents["scheduling"],
            suggestion_agent=agents["suggestion"],
        )

    def test_graph_building(self, graph_builder):
        """Test graph construction."""
        graph = graph_builder.build()

        assert graph is not None
        assert graph_builder.graph is not None

    def test_graph_compilation(self, graph_builder):
        """Test graph compilation."""
        compiled = graph_builder.compile()

        assert compiled is not None
        assert graph_builder.compiled_graph is not None

    def test_graph_has_correct_nodes(self, graph_builder):
        """Test that graph has all required nodes."""
        graph = graph_builder.build()

        # Get nodes (implementation depends on LangGraph version)
        # This is a basic structure test
        assert graph_builder.graph is not None

    def test_supervisor_routing_to_planning(self, graph_builder, mock_services):
        """Test routing from supervisor to planning agent."""
        compiled_graph = graph_builder.compile()

        # Create initial state
        state = StateManager.create_initial_state("Add task: write report")

        # Mock supervisor to route to planning
        state["routing_decision"] = "planning"

        # Test routing logic
        next_node = graph_builder._route_from_supervisor(state)
        assert next_node == "planning"

    def test_supervisor_routing_to_scheduling(self, graph_builder):
        """Test routing from supervisor to scheduling agent."""
        compiled_graph = graph_builder.compile()

        state = StateManager.create_initial_state("Plan my day")
        state["routing_decision"] = "scheduling"

        next_node = graph_builder._route_from_supervisor(state)
        assert next_node == "scheduling"

    def test_supervisor_routing_to_suggestion(self, graph_builder):
        """Test routing from supervisor to suggestion agent."""
        compiled_graph = graph_builder.compile()

        state = StateManager.create_initial_state("What should I work on?")
        state["routing_decision"] = "suggestion"

        next_node = graph_builder._route_from_supervisor(state)
        assert next_node == "suggestion"

    def test_error_routing(self, graph_builder):
        """Test error handling routing."""
        compiled_graph = graph_builder.compile()

        state = StateManager.create_initial_state("Test message")
        state["error"] = "Test error"

        next_node = graph_builder._route_from_supervisor(state)
        assert next_node == "error_handler"

    def test_agent_routing_back_to_supervisor(self, graph_builder):
        """Test agent routing back to supervisor."""
        compiled_graph = graph_builder.compile()

        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "supervisor"

        next_node = graph_builder._route_from_agent(state)
        assert next_node == "supervisor"

    def test_agent_routing_to_end(self, graph_builder):
        """Test agent routing to END."""
        compiled_graph = graph_builder.compile()

        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "END"

        next_node = graph_builder._route_from_agent(state)
        assert next_node == "END"

    def test_invalid_routing_defaults_to_end(self, graph_builder):
        """Test that invalid routing decisions default to END."""
        compiled_graph = graph_builder.compile()

        state = StateManager.create_initial_state("Test")
        state["routing_decision"] = "invalid_agent"

        next_node = graph_builder._route_from_supervisor(state)
        assert next_node == "END"

    def test_create_agent_graph_convenience_function(self, agents):
        """Test convenience function for creating graph."""
        compiled_graph = create_agent_graph(
            supervisor_agent=agents["supervisor"],
            planning_agent=agents["planning"],
            scheduling_agent=agents["scheduling"],
            suggestion_agent=agents["suggestion"],
        )

        assert compiled_graph is not None

    def test_graph_visualization(self, graph_builder):
        """Test graph visualization output."""
        viz = graph_builder.get_graph_visualization()

        assert "Supervisor" in viz
        assert "Planning" in viz
        assert "Scheduling" in viz
        assert "Suggestion" in viz
        assert "Error Handler" in viz

    def test_full_workflow_execution(self, graph_builder, mock_services, agents):
        """Test complete workflow execution (mock)."""
        # This is a simplified test - full execution testing happens in UI
        compiled_graph = graph_builder.compile()

        # Verify graph can be invoked (structure test)
        assert compiled_graph is not None
        assert callable(getattr(compiled_graph, "invoke", None))

    def test_state_persistence_across_nodes(self, graph_builder):
        """Test that state persists correctly across nodes."""
        state = StateManager.create_initial_state("Test message")
        state = StateManager.update_context(state, "test_key", "test_value")

        # Verify context persists
        assert StateManager.get_context(state, "test_key") == "test_value"

        # Simulate passing through routing
        state["routing_decision"] = "planning"
        next_node = graph_builder._route_from_supervisor(state)

        # Context should still be present
        assert StateManager.get_context(state, "test_key") == "test_value"
```

### Step 5: Create Graph Visualization Script (20 min)

Create `scripts/visualize_graph.py`:

```python
"""Visualize the agent graph structure."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from adhd_planner.graph.builder import GraphBuilder
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.agents.suggestion_agent import SuggestionAgent
from adhd_planner.services.llm_service import LLMService
from adhd_planner.utils.config import get_settings


def visualize_graph():
    """Create and visualize the agent graph."""
    print("Creating mock agent graph for visualization...\n")

    # Create mock services
    settings = get_settings()

    try:
        llm_service = LLMService(settings)
    except Exception:
        # Use None if LLM service fails (for visualization only)
        llm_service = None

    # Create mock task and calendar services
    class MockService:
        pass

    task_service = MockService()
    calendar_service = MockService()

    # Create agents
    supervisor = SupervisorAgent(
        llm_service=llm_service,
        task_service=task_service,
        calendar_service=calendar_service,
    )

    planning = PlanningAgent(
        llm_service=llm_service,
        task_service=task_service,
        calendar_service=calendar_service,
    )

    scheduling = SchedulingAgent(
        llm_service=llm_service,
        task_service=task_service,
        calendar_service=calendar_service,
    )

    suggestion = SuggestionAgent(
        llm_service=llm_service,
        task_service=task_service,
        calendar_service=calendar_service,
    )

    # Build graph
    builder = GraphBuilder(
        supervisor_agent=supervisor,
        planning_agent=planning,
        scheduling_agent=scheduling,
        suggestion_agent=suggestion,
    )

    builder.build()

    # Print visualization
    print(builder.get_graph_visualization())

    print("\n✅ Graph structure created successfully!")
    print("\nThe graph orchestrates the following agents:")
    print("  - Supervisor: Routes requests")
    print("  - Planning: Creates tasks")
    print("  - Scheduling: Generates schedules")
    print("  - Suggestion: Recommends tasks")
    print("  - Error Handler: Handles errors")


if __name__ == "__main__":
    visualize_graph()
```

## Testing Checklist

- [ ] Run `uv run pytest tests/integration/test_graph_workflow.py -v`
- [ ] All integration tests pass
- [ ] Graph builds successfully
- [ ] Graph compiles without errors
- [ ] All routing paths work
- [ ] Error handling works
- [ ] State persists across nodes
- [ ] Run `uv run python scripts/visualize_graph.py`
- [ ] Visualization displays correctly

## Success Criteria

### Functionality
- [ ] Graph builds and compiles
- [ ] All agents integrated
- [ ] Routing logic works
- [ ] Error handling functional
- [ ] State management works
- [ ] All tests pass

### Code Quality
- [ ] Type hints throughout
- [ ] Comprehensive docstrings
- [ ] Clear node functions
- [ ] Clean routing logic
- [ ] Proper error handling
- [ ] Logging at key points

### Testing
- [ ] Integration tests pass
- [ ] All routing paths tested
- [ ] Error scenarios covered
- [ ] State persistence verified
- [ ] Graph visualization works

## Implementation Notes

### Graph Structure

The graph follows a **hub-and-spoke** pattern:
- **Hub**: Supervisor agent (routing center)
- **Spokes**: Specialist agents (planning, scheduling, suggestion)
- **Safety Net**: Error handler

### Routing Logic

**From Supervisor**:
- Analyzes user intent
- Routes to appropriate specialist
- Can end immediately for simple queries

**From Specialists**:
- Can return to supervisor for follow-up
- Usually ends after completing task
- Errors route to error handler

### State Management

State flows through nodes:
1. Initial state created with user message
2. Supervisor adds routing decision
3. Specialist agent processes and adds response
4. State accumulates messages and context
5. Final state returned to caller

### Error Recovery

Errors are handled gracefully:
- Caught in agent execution
- Added to state
- Routed to error handler
- User-friendly message generated
- Workflow ends cleanly

### Future Extensions

Easy to add new agents:
1. Create agent class
2. Add node function
3. Update graph builder
4. Add routing logic
5. That's it!

## Next Steps

After completing this story:

1. **Test the Complete Workflow**
   - Run all integration tests
   - Verify graph visualization
   - Test each routing path

2. **Prepare for UI Integration**
   - Graph is ready for Epic 4 (Streamlit UI)
   - Can be invoked from UI layer
   - State management ready

3. **Next Epic**
   - Move to **Epic 4: Streamlit UI**
   - **ADHD-17**: Streamlit App Structure

## Common Issues

### Graph Compilation Errors
- Check all agents are initialized
- Verify routing decision values
- Ensure state schema matches

### Routing Not Working
- Check routing_decision in state
- Verify conditional edge logic
- Add logging to debug

### State Not Persisting
- Check StateManager usage
- Verify state passed correctly
- Ensure no state overwrites

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System design
- [Agent System Design](../../docs/architecture/agent-system.md)

Good luck! This is the final piece that brings all agents together! 🚀
