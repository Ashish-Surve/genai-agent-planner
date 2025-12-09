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
