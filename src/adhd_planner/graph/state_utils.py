"""Utilities for managing AgentState in the LangGraph system."""

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

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
            metadata={},
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
        message = AIMessage(content=content, additional_kwargs={"agent": agent_name})
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

        if not isinstance(state.get("messages"), list | tuple):
            raise ValueError("State 'messages' must be a sequence")

        return True
