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
