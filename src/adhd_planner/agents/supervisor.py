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
