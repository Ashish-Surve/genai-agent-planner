# ADHD-12: Supervisor Agent

## Story Information
- **Epic**: Epic 3 - LangGraph Agents
- **Story ID**: ADHD-12
- **Estimated Time**: 3 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-11: LangGraph State & Base Agent
  - ✅ ADHD-7: LLM Service & Provider Factory

## Description

Implement the Supervisor Agent, the central coordinator of the multi-agent system. The supervisor analyzes user requests, determines which specialized agent should handle them (planning, scheduling, suggestion, sync, energy), and routes accordingly. It also synthesizes responses from multiple agents when needed.

This agent is the "brain" that orchestrates all other agents and ensures the right specialist handles each request.

## Goals

1. Implement supervisor agent with routing logic
2. Create intent classification using LLM
3. Build routing decision logic for all agent types
4. Implement response synthesis for multi-agent workflows
5. Create edge functions for LangGraph routing
6. Handle errors and fallback cases

## Acceptance Criteria

### Supervisor Agent Implementation
- [ ] Inherits from BaseAgent
- [ ] Classifies user intent using LLM
- [ ] Routes to appropriate specialist agent
- [ ] Handles multi-turn conversations
- [ ] Synthesizes responses when needed
- [ ] Graceful error handling

### Intent Classification
- [ ] Identifies planning requests (create/modify tasks)
- [ ] Identifies scheduling requests (plan day/week)
- [ ] Identifies suggestion requests (what to work on)
- [ ] Identifies sync requests (sync with Apple)
- [ ] Identifies energy tracking requests
- [ ] Identifies general questions

### Routing Logic
- [ ] Returns correct agent name for each intent
- [ ] Handles ambiguous requests
- [ ] Falls back to direct response when appropriate
- [ ] Logs routing decisions
- [ ] Updates state with routing decision

### Edge Functions
- [ ] `route_to_agent()` function for graph edges
- [ ] Reads routing_decision from state
- [ ] Returns agent name for graph to follow
- [ ] Handles END case for completion
- [ ] Error handling for invalid routes

### Testing
- [ ] Unit tests for intent classification
- [ ] Unit tests for routing logic
- [ ] Integration tests with mock LLM
- [ ] Edge function tests
- [ ] Error case handling tests

## Files to Create/Modify

### New Files
```
src/adhd_planner/agents/
└── supervisor.py                 # Supervisor agent implementation

src/adhd_planner/graph/
└── edges.py                      # Edge routing functions

src/adhd_planner/utils/prompts/
├── __init__.py
└── supervisor_prompts.py         # Supervisor LLM prompts

tests/unit/
├── test_supervisor_agent.py     # Supervisor tests
└── test_graph_edges.py          # Edge function tests
```

## Implementation Steps

### Step 1: Create Supervisor Prompts (30 min)

Create `src/adhd_planner/utils/prompts/supervisor_prompts.py`:

```python
"""Prompts for the Supervisor Agent."""

SUPERVISOR_SYSTEM_PROMPT = """You are the Supervisor Agent for ADHD Planner, an AI-powered planning assistant.

Your role is to:
1. Understand user requests
2. Route them to the appropriate specialist agent
3. Synthesize responses when multiple agents are involved

Available specialist agents:
- **planning_agent**: Create, modify, or analyze tasks
- **scheduling_agent**: Generate daily/weekly schedules, optimize time blocks
- **suggestion_agent**: Recommend what to work on based on context
- **sync_agent**: Sync with Apple Reminders/Calendar
- **energy_agent**: Track and analyze energy patterns

Routing guidelines:
- Use planning_agent for: "add task", "create task", "update task", "task details"
- Use scheduling_agent for: "plan my day", "schedule", "time blocks", "optimize schedule"
- Use suggestion_agent for: "what should I do", "recommend", "what's next"
- Use sync_agent for: "sync with apple", "sync reminders", "sync calendar"
- Use energy_agent for: "log energy", "energy patterns", "when am I productive"
- Use "direct_response" for: greetings, general questions, clarifications

Respond in JSON format:
{
  "intent": "description of what user wants",
  "agent": "agent_name or direct_response",
  "reasoning": "why you chose this agent",
  "needs_context": ["list", "of", "context", "needed"]
}
"""


def get_routing_prompt(user_input: str, conversation_history: str = "") -> str:
    """
    Create prompt for routing decision.

    Args:
        user_input: Current user message
        conversation_history: Previous conversation context

    Returns:
        Formatted prompt for LLM
    """
    prompt = f"""Analyze this user request and determine which agent should handle it.

User request: "{user_input}"
"""

    if conversation_history:
        prompt += f"\nConversation context:\n{conversation_history}\n"

    prompt += """
Respond with JSON only, following this format:
{
  "intent": "what the user wants to accomplish",
  "agent": "planning_agent|scheduling_agent|suggestion_agent|sync_agent|energy_agent|direct_response",
  "reasoning": "explanation of routing decision",
  "needs_context": ["tasks", "calendar", "energy_patterns"]
}
"""

    return prompt


DIRECT_RESPONSE_PROMPT = """You are a helpful AI planning assistant for people with ADHD.

Respond to the user's message naturally and helpfully. Keep responses concise and clear.

User message: {user_input}

Response:"""
```

### Step 2: Create Supervisor Agent (60 min)

Create `src/adhd_planner/agents/supervisor.py`:

```python
"""Supervisor Agent - Routes requests to specialized agents."""

import json
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.utils.prompts.supervisor_prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    get_routing_prompt,
    DIRECT_RESPONSE_PROMPT,
)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent coordinates all specialized agents.

    Responsibilities:
    - Analyze user requests and classify intent
    - Route to appropriate specialist agent
    - Handle direct responses for simple queries
    - Synthesize multi-agent responses
    - Manage conversation flow
    """

    def __init__(self, llm_service):
        """
        Initialize supervisor agent.

        Args:
            llm_service: LLM service for intent classification
        """
        super().__init__(
            name="supervisor",
            description="Routes requests to specialized agents",
            llm_service=llm_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute supervisor logic: classify intent and route.

        Args:
            state: Current agent state

        Returns:
            Updated state with routing decision
        """
        try:
            self.log_execution(state)

            # Get user input
            user_input = state["user_input"]

            # Get conversation history for context
            conversation_history = self._get_conversation_context(state)

            # Classify intent and determine routing
            routing_decision = self._classify_and_route(user_input, conversation_history)

            # Update state with routing decision
            state["routing_decision"] = routing_decision["agent"]
            state = self.update_context(state, "supervisor_analysis", routing_decision)

            # If direct response, handle it now
            if routing_decision["agent"] == "direct_response":
                state = self._handle_direct_response(state, user_input)
                state["routing_decision"] = "END"  # No further routing needed

            self.logger.info(
                f"Routing decision: {routing_decision['agent']} - {routing_decision['reasoning']}"
            )

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _classify_and_route(
        self, user_input: str, conversation_history: str
    ) -> dict[str, Any]:
        """
        Classify user intent and determine routing.

        Args:
            user_input: User's message
            conversation_history: Previous conversation

        Returns:
            Routing decision dict with agent, intent, reasoning
        """
        llm_service = self.get_service("llm_service")

        # Create routing prompt
        prompt = get_routing_prompt(user_input, conversation_history)

        # Get LLM decision
        try:
            response = llm_service.generate(
                prompt=prompt,
                system_prompt=SUPERVISOR_SYSTEM_PROMPT,
                temperature=0.1,  # Low temperature for consistent routing
            )

            # Parse JSON response
            routing_decision = json.loads(response)

            # Validate required fields
            required_fields = ["intent", "agent", "reasoning"]
            for field in required_fields:
                if field not in routing_decision:
                    raise ValueError(f"Missing required field: {field}")

            # Validate agent name
            valid_agents = [
                "planning_agent",
                "scheduling_agent",
                "suggestion_agent",
                "sync_agent",
                "energy_agent",
                "direct_response",
            ]

            if routing_decision["agent"] not in valid_agents:
                self.logger.warning(
                    f"Invalid agent: {routing_decision['agent']}, defaulting to direct_response"
                )
                routing_decision["agent"] = "direct_response"

            return routing_decision

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse routing decision: {e}")
            # Fallback to direct response
            return {
                "intent": "unclear",
                "agent": "direct_response",
                "reasoning": "Could not parse routing decision, handling directly",
                "needs_context": [],
            }

    def _get_conversation_context(self, state: AgentState) -> str:
        """
        Extract relevant conversation history.

        Args:
            state: Current state

        Returns:
            Formatted conversation context
        """
        messages = self.state_manager.get_message_history(state, last_n=5)

        context_parts = []
        for msg in messages:
            role = "User" if msg.type == "human" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")

        return "\n".join(context_parts)

    def _handle_direct_response(self, state: AgentState, user_input: str) -> AgentState:
        """
        Generate direct response without routing to specialist.

        Args:
            state: Current state
            user_input: User's message

        Returns:
            Updated state with response
        """
        llm_service = self.get_service("llm_service")

        prompt = DIRECT_RESPONSE_PROMPT.format(user_input=user_input)

        response = llm_service.generate(prompt=prompt, temperature=0.7)

        return self.add_response(state, response)

    def should_end_conversation(self, state: AgentState) -> bool:
        """
        Determine if conversation should end.

        Args:
            state: Current state

        Returns:
            True if conversation should end
        """
        routing_decision = state.get("routing_decision")
        has_error = state.get("error") is not None

        return routing_decision == "END" or has_error
```

### Step 3: Create Edge Functions (30 min)

Create `src/adhd_planner/graph/edges.py`:

```python
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
```

### Step 4: Update Package Initialization (10 min)

Update `src/adhd_planner/utils/prompts/__init__.py`:

```python
"""Prompt templates for LLM interactions."""

from adhd_planner.utils.prompts.supervisor_prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    get_routing_prompt,
    DIRECT_RESPONSE_PROMPT,
)

__all__ = [
    "SUPERVISOR_SYSTEM_PROMPT",
    "get_routing_prompt",
    "DIRECT_RESPONSE_PROMPT",
]
```

Update `src/adhd_planner/graph/__init__.py`:

```python
"""LangGraph state and graph building utilities."""

from adhd_planner.graph.state import AgentState
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.graph.edges import route_to_agent, should_continue, route_after_specialist

__all__ = [
    "AgentState",
    "StateManager",
    "route_to_agent",
    "should_continue",
    "route_after_specialist",
]
```

Update `src/adhd_planner/agents/__init__.py`:

```python
"""AI agents for the ADHD Planner system."""

from adhd_planner.agents.base import BaseAgent
from adhd_planner.agents.supervisor import SupervisorAgent

__all__ = ["BaseAgent", "SupervisorAgent"]
```

### Step 5: Create Tests (60 min)

Create `tests/unit/test_supervisor_agent.py`:

```python
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
```

Create `tests/unit/test_graph_edges.py`:

```python
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
```

### Step 6: Create Integration Test Example (20 min)

Create `tests/integration/test_supervisor_routing.py`:

```python
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
```

## Testing Checklist

- [ ] Run `uv run pytest tests/unit/test_supervisor_agent.py -v`
- [ ] All supervisor tests pass
- [ ] Run `uv run pytest tests/unit/test_graph_edges.py -v`
- [ ] All edge function tests pass
- [ ] Run `uv run pytest tests/integration/test_supervisor_routing.py -v`
- [ ] Integration tests pass
- [ ] Supervisor correctly routes to all agent types
- [ ] Direct response works for simple queries
- [ ] Error handling works correctly
- [ ] Edge functions route correctly
- [ ] Invalid routing falls back gracefully

## Success Criteria

### Functionality
- [ ] Supervisor classifies intents correctly
- [ ] Routes to appropriate specialist agents
- [ ] Handles direct responses
- [ ] Edge functions work with LangGraph
- [ ] Error handling is robust
- [ ] All tests pass

### Code Quality
- [ ] Type hints on all functions
- [ ] Comprehensive docstrings
- [ ] Logging for debugging
- [ ] Clean separation of concerns
- [ ] Follows project patterns

### Testing
- [ ] Unit tests for all routing cases
- [ ] Edge function tests
- [ ] Integration tests
- [ ] Error case coverage
- [ ] Mock LLM service works well

## Implementation Notes

### Intent Classification

The supervisor uses an LLM to classify user intent because:
1. Natural language is ambiguous
2. Users phrase requests differently
3. Context matters for intent
4. LLM can handle nuance better than regex

### Routing Strategy

The supervisor returns a `routing_decision` in state, which edge functions read. This separates:
- **Agent logic**: What to do with the request
- **Graph structure**: How to route between agents

### Error Handling

Errors are handled gracefully:
1. Invalid JSON → fallback to direct response
2. Invalid agent name → fallback to direct response
3. LLM service error → set error in state

### Testing with Mocks

We mock the LLM service for testing because:
1. Tests run fast without API calls
2. Deterministic behavior
3. Easy to test edge cases
4. No API costs

## Next Story

After completing this story, proceed to:
- **ADHD-13**: Planning Agent - First specialist agent implementation

## Questions or Issues?

If you encounter issues:
1. Verify LLM service is properly mocked in tests
2. Check JSON parsing in supervisor
3. Review edge function logic
4. Check the test output for specific failures

Good luck! 🚀
