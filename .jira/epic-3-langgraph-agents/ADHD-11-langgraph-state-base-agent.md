# ADHD-11: LangGraph State & Base Agent

## Story Information
- **Epic**: Epic 3 - LangGraph Agents
- **Story ID**: ADHD-11
- **Estimated Time**: 3 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-10: Time Estimation Service
  - ✅ ADHD-9: Calendar Service
  - ✅ ADHD-8: Task Service
  - ✅ ADHD-7: LLM Service & Provider Factory

## Description

Create the foundational components for the LangGraph agent system: define the `AgentState` TypedDict that flows through the graph, implement the `BaseAgent` abstract class that all specialized agents will inherit from, and build state management utilities.

This story establishes the contract and patterns that all agents will follow, enabling consistent agent behavior and easy addition of new agents in the future.

## Goals

1. Define `AgentState` TypedDict with all necessary state fields
2. Implement `BaseAgent` abstract class with common agent functionality
3. Create state management utilities for adding messages, updating context, etc.
4. Build agent testing utilities for consistent testing patterns
5. Document the agent development pattern for future extensions

## Acceptance Criteria

### AgentState TypedDict
- [ ] Contains all required state fields (messages, context, user_input, etc.)
- [ ] Uses proper TypedDict annotations
- [ ] Includes operator annotations for list fields (messages should append)
- [ ] Well-documented with field descriptions
- [ ] Supports both read and write operations

### BaseAgent Abstract Class
- [ ] Defines abstract `execute()` method signature
- [ ] Provides common utilities (logging, state access, error handling)
- [ ] Includes agent name and description attributes
- [ ] Supports dependency injection for services
- [ ] Has proper type hints

### State Management Utilities
- [ ] Helper to add messages to state
- [ ] Helper to update context
- [ ] Helper to extract user input
- [ ] Helper to format agent responses
- [ ] Validation utilities for state

### Testing Support
- [ ] Mock state builder for testing
- [ ] Agent test harness
- [ ] Example test demonstrating pattern
- [ ] Testing documentation

### Documentation
- [ ] Docstrings on all classes and methods
- [ ] Agent development guide
- [ ] State flow diagram
- [ ] Example agent implementation

## Files to Create/Modify

### New Files
```
src/adhd_planner/graph/
├── __init__.py                    # Package initialization
├── state.py                       # AgentState TypedDict definition
└── state_utils.py                 # State management utilities

src/adhd_planner/agents/
├── __init__.py                    # Package initialization
└── base.py                        # BaseAgent abstract class

tests/unit/
├── test_agent_state.py           # State tests
└── test_base_agent.py            # Base agent tests

docs/technical/
└── agent-development-guide.md    # How to create new agents
```

## Implementation Steps

### Step 1: Create AgentState TypedDict (45 min)

Create `src/adhd_planner/graph/state.py`:

```python
"""LangGraph state definition for ADHD Planner agent system."""

from typing import TypedDict, Annotated, Sequence
from operator import add
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State that flows through the LangGraph agent system.

    This state is passed between all agent nodes and modified by each agent
    as they process user requests and coordinate actions.

    Attributes:
        messages: Chat message history (appends with operator.add)
        user_input: Current user input being processed
        current_agent: Name of the agent currently handling the request
        routing_decision: Which agent should handle the request next
        context: Additional context data (tasks, calendar, energy, etc.)
        error: Error information if any agent fails
        metadata: Arbitrary metadata for debugging/logging
    """

    # Message history - uses Annotated with add operator to append messages
    messages: Annotated[Sequence[BaseMessage], add]

    # Current user input being processed
    user_input: str

    # Agent routing information
    current_agent: str
    routing_decision: str | None

    # Context data that agents can read/update
    context: dict

    # Error handling
    error: str | None

    # Metadata for debugging and logging
    metadata: dict
```

**Key Design Decisions:**
- `messages` uses `Annotated[Sequence[BaseMessage], add]` so LangGraph automatically appends new messages
- `context` is a flexible dict that can store tasks, calendar events, energy data, etc.
- `routing_decision` allows supervisor to specify next agent
- `error` field enables graceful error propagation

### Step 2: Create State Management Utilities (45 min)

Create `src/adhd_planner/graph/state_utils.py`:

```python
"""Utilities for managing AgentState in the LangGraph system."""

from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

from adhd_planner.graph.state import AgentState
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """Utilities for working with AgentState."""

    @staticmethod
    def create_initial_state(user_input: str) -> AgentState:
        """
        Create initial state for a new conversation turn.

        Args:
            user_input: The user's input message

        Returns:
            Fresh AgentState ready for processing
        """
        return AgentState(
            messages=[HumanMessage(content=user_input)],
            user_input=user_input,
            current_agent="supervisor",
            routing_decision=None,
            context={},
            error=None,
            metadata={}
        )

    @staticmethod
    def add_message(state: AgentState, message: BaseMessage) -> AgentState:
        """
        Add a message to the state.

        Args:
            state: Current state
            message: Message to add

        Returns:
            Updated state with message appended
        """
        # LangGraph automatically handles the append with the add operator
        state["messages"] = state.get("messages", []) + [message]
        return state

    @staticmethod
    def add_ai_message(state: AgentState, content: str, agent_name: str) -> AgentState:
        """
        Add an AI message from a specific agent.

        Args:
            state: Current state
            content: Message content
            agent_name: Name of the agent sending the message

        Returns:
            Updated state
        """
        message = AIMessage(
            content=content,
            additional_kwargs={"agent": agent_name}
        )
        return StateManager.add_message(state, message)

    @staticmethod
    def update_context(state: AgentState, key: str, value: Any) -> AgentState:
        """
        Update a context value in the state.

        Args:
            state: Current state
            key: Context key
            value: Context value

        Returns:
            Updated state
        """
        context = state.get("context", {}).copy()
        context[key] = value
        state["context"] = context
        return state

    @staticmethod
    def get_context(state: AgentState, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.

        Args:
            state: Current state
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        return state.get("context", {}).get(key, default)

    @staticmethod
    def set_error(state: AgentState, error_message: str, agent_name: str) -> AgentState:
        """
        Set an error in the state.

        Args:
            state: Current state
            error_message: Error description
            agent_name: Agent that encountered the error

        Returns:
            Updated state
        """
        state["error"] = error_message
        state["metadata"]["error_agent"] = agent_name
        logger.error(f"Agent {agent_name} error: {error_message}")
        return state

    @staticmethod
    def set_routing_decision(state: AgentState, next_agent: str) -> AgentState:
        """
        Set which agent should handle the request next.

        Args:
            state: Current state
            next_agent: Name of the next agent to route to

        Returns:
            Updated state
        """
        state["routing_decision"] = next_agent
        logger.debug(f"Routing decision: {next_agent}")
        return state

    @staticmethod
    def get_message_history(state: AgentState, last_n: int | None = None) -> list[BaseMessage]:
        """
        Get message history from state.

        Args:
            state: Current state
            last_n: Optional limit to last N messages

        Returns:
            List of messages
        """
        messages = state.get("messages", [])
        if last_n:
            return messages[-last_n:]
        return messages

    @staticmethod
    def validate_state(state: AgentState) -> bool:
        """
        Validate that state has required fields.

        Args:
            state: State to validate

        Returns:
            True if valid, raises ValueError if not
        """
        required_fields = ["messages", "user_input", "current_agent"]

        for field in required_fields:
            if field not in state:
                raise ValueError(f"State missing required field: {field}")

        if not isinstance(state.get("messages"), (list, tuple)):
            raise ValueError("State 'messages' must be a sequence")

        return True
```

### Step 3: Create BaseAgent Abstract Class (45 min)

Create `src/adhd_planner/agents/base.py`:

```python
"""Base agent class for all LangGraph agents in ADHD Planner."""

from abc import ABC, abstractmethod
from typing import Any

from adhd_planner.graph.state import AgentState
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.utils.logger import get_logger


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    All specialized agents (supervisor, planning, scheduling, etc.) inherit
    from this class and implement the execute() method.

    Provides common functionality:
    - Logging
    - State management utilities
    - Error handling
    - Service access

    Attributes:
        name: Unique identifier for this agent
        description: Human-readable description of agent's purpose
        logger: Logger instance for this agent
    """

    def __init__(
        self,
        name: str,
        description: str,
        **services
    ):
        """
        Initialize the base agent.

        Args:
            name: Agent name (e.g., "planning_agent")
            description: Agent description
            **services: Services this agent depends on (task_service, llm_service, etc.)
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"agent.{name}")
        self.services = services
        self.state_manager = StateManager()

    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute this agent's logic.

        This is the main entry point called by LangGraph. Each agent
        implements its specific behavior here.

        Args:
            state: Current AgentState

        Returns:
            Updated AgentState after agent processing
        """
        pass

    def log_execution(self, state: AgentState) -> None:
        """
        Log that this agent is executing.

        Args:
            state: Current state
        """
        user_input = state.get("user_input", "")
        self.logger.info(f"Executing agent '{self.name}' for input: {user_input[:50]}...")

    def get_service(self, service_name: str) -> Any:
        """
        Get a service by name.

        Args:
            service_name: Name of the service

        Returns:
            Service instance

        Raises:
            ValueError: If service not found
        """
        service = self.services.get(service_name)
        if service is None:
            raise ValueError(f"Agent {self.name} missing required service: {service_name}")
        return service

    def handle_error(self, state: AgentState, error: Exception) -> AgentState:
        """
        Handle an error that occurred during execution.

        Args:
            state: Current state
            error: The exception that occurred

        Returns:
            State with error information
        """
        error_message = f"{self.name}: {str(error)}"
        self.logger.error(error_message, exc_info=True)
        return self.state_manager.set_error(state, error_message, self.name)

    def add_response(self, state: AgentState, response: str) -> AgentState:
        """
        Add this agent's response to the state.

        Args:
            state: Current state
            response: Agent's response message

        Returns:
            Updated state
        """
        return self.state_manager.add_ai_message(state, response, self.name)

    def get_context(self, state: AgentState, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.

        Args:
            state: Current state
            key: Context key
            default: Default value

        Returns:
            Context value or default
        """
        return self.state_manager.get_context(state, key, default)

    def update_context(self, state: AgentState, key: str, value: Any) -> AgentState:
        """
        Update the context.

        Args:
            state: Current state
            key: Context key
            value: Context value

        Returns:
            Updated state
        """
        return self.state_manager.update_context(state, key, value)

    def __repr__(self) -> str:
        """String representation of this agent."""
        return f"<{self.__class__.__name__}(name={self.name})>"
```

### Step 4: Create Package Initializations (15 min)

Update `src/adhd_planner/graph/__init__.py`:

```python
"""LangGraph state and graph building utilities."""

from adhd_planner.graph.state import AgentState
from adhd_planner.graph.state_utils import StateManager

__all__ = ["AgentState", "StateManager"]
```

Update `src/adhd_planner/agents/__init__.py`:

```python
"""AI agents for the ADHD Planner system."""

from adhd_planner.agents.base import BaseAgent

__all__ = ["BaseAgent"]
```

### Step 5: Create Tests (45 min)

Create `tests/unit/test_agent_state.py`:

```python
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
```

Create `tests/unit/test_base_agent.py`:

```python
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
```

### Step 6: Create Agent Development Documentation (15 min)

Create `docs/technical/agent-development-guide.md`:

```markdown
# Agent Development Guide

## Overview

This guide explains how to create new agents for the ADHD Planner system. All agents inherit from `BaseAgent` and follow the LangGraph pattern.

## Agent Architecture

### AgentState

The `AgentState` TypedDict flows through all agents:

\`\`\`python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add]  # Chat history
    user_input: str                                   # Current input
    current_agent: str                                # Agent handling request
    routing_decision: str | None                      # Next agent to route to
    context: dict                                     # Shared context data
    error: str | None                                 # Error information
    metadata: dict                                    # Debug/logging data
\`\`\`

### BaseAgent

All agents inherit from `BaseAgent`:

\`\`\`python
class MyAgent(BaseAgent):
    def execute(self, state: AgentState) -> AgentState:
        # Implement agent logic here
        pass
\`\`\`

## Creating a New Agent

### Step 1: Define the Agent Class

\`\`\`python
from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState

class MyCustomAgent(BaseAgent):
    """Agent that does something specific."""

    def __init__(self, task_service, llm_service):
        super().__init__(
            name="my_custom_agent",
            description="Does something specific",
            task_service=task_service,
            llm_service=llm_service
        )

    def execute(self, state: AgentState) -> AgentState:
        """Execute agent logic."""
        try:
            # Log execution
            self.log_execution(state)

            # Get services
            task_service = self.get_service("task_service")
            llm_service = self.get_service("llm_service")

            # Get user input
            user_input = state["user_input"]

            # Do agent-specific work
            result = self._do_work(user_input, task_service, llm_service)

            # Add response to state
            state = self.add_response(state, result)

            # Update context if needed
            state = self.update_context(state, "my_data", some_value)

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _do_work(self, user_input, task_service, llm_service):
        """Agent-specific implementation."""
        # Your logic here
        pass
\`\`\`

### Step 2: Write Tests

\`\`\`python
import pytest
from adhd_planner.graph.state_utils import StateManager

class TestMyCustomAgent:
    def test_execute(self, mock_task_service, mock_llm_service):
        agent = MyCustomAgent(
            task_service=mock_task_service,
            llm_service=mock_llm_service
        )

        state = StateManager.create_initial_state("Test input")
        result = agent.execute(state)

        # Assert expected behavior
        assert len(result["messages"]) == 2
        assert result["error"] is None
\`\`\`

### Step 3: Integrate with Graph

Add your agent to the LangGraph builder (covered in ADHD-16).

## Best Practices

1. **Error Handling**: Always wrap execute() in try/except and use `handle_error()`
2. **Logging**: Use `self.logger` for debugging
3. **State Immutability**: Treat state as immutable; create updated copies
4. **Context Management**: Use context for sharing data between agents
5. **Service Injection**: Pass services via constructor for testability

## Common Patterns

### Calling LLM

\`\`\`python
llm_service = self.get_service("llm_service")
response = llm_service.generate(prompt, temperature=0.7)
\`\`\`

### Accessing Task Service

\`\`\`python
task_service = self.get_service("task_service")
tasks = task_service.get_incomplete_tasks()
\`\`\`

### Adding Messages

\`\`\`python
state = self.add_response(state, "Here's my response")
\`\`\`

### Updating Context

\`\`\`python
state = self.update_context(state, "analysis_result", analysis_data)
\`\`\`

### Getting Context

\`\`\`python
tasks = self.get_context(state, "tasks", default=[])
\`\`\`

## Testing Utilities

Use `StateManager` to create test states:

\`\`\`python
state = StateManager.create_initial_state("User input")
state = StateManager.update_context(state, "tasks", mock_tasks)
\`\`\`

## Next Steps

- See `ADHD-12` for the Supervisor Agent example
- See `ADHD-13` for the Planning Agent example
- See `ADHD-16` for graph integration
\`\`\`

## Testing Checklist

- [ ] Run `uv run pytest tests/unit/test_agent_state.py -v`
- [ ] All state management tests pass
- [ ] Run `uv run pytest tests/unit/test_base_agent.py -v`
- [ ] All base agent tests pass
- [ ] Import AgentState in Python shell successfully
- [ ] Import BaseAgent successfully
- [ ] StateManager utilities work correctly
- [ ] Mock agent can be created and executed
- [ ] Error handling works as expected
- [ ] Context management works correctly
- [ ] Message management works correctly

## Success Criteria

### Functionality
- [ ] AgentState TypedDict is properly defined with all fields
- [ ] StateManager provides all necessary utilities
- [ ] BaseAgent abstract class enforces the contract
- [ ] All tests pass
- [ ] Documentation is clear and comprehensive

### Code Quality
- [ ] Type hints on all functions
- [ ] Comprehensive docstrings
- [ ] Logging in appropriate places
- [ ] Error handling is robust
- [ ] Code follows project patterns

### Testing
- [ ] Unit tests cover all state utilities
- [ ] Base agent functionality is tested
- [ ] Mock agent demonstrates pattern
- [ ] Edge cases are tested
- [ ] Error conditions are tested

## Implementation Notes

### TypedDict vs Dataclass

We use TypedDict instead of dataclass because LangGraph requires TypedDict for its state management. The `Annotated[Sequence[BaseMessage], add]` syntax tells LangGraph to append new messages instead of replacing them.

### State Immutability

While Python dicts are mutable, treat the state as immutable in your agent code. Always create updated copies rather than modifying in place. This prevents subtle bugs in the graph flow.

### Service Injection

Pass all services through the constructor rather than importing them directly. This makes testing easier (you can inject mocks) and makes dependencies explicit.

### Context vs Messages

- **Messages**: The conversation history shown to the user
- **Context**: Behind-the-scenes data shared between agents (tasks, calendar, analysis results)

Use context for data that agents need but users don't need to see.

## Next Story

After completing this story, proceed to:
- **ADHD-12**: Supervisor Agent - Implements the routing and coordination logic

## Questions or Issues?

If you encounter issues:
1. Check that LangGraph and LangChain are installed
2. Verify imports work correctly
3. Review the test output for specific failures
4. Check the architecture documentation for context

Good luck! 🚀
