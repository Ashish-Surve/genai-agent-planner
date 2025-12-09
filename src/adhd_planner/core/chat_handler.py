"""Chat handler for processing user messages through the agent system."""

from collections.abc import Generator

from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)


class ChatHandler:
    """
    Handles chat interactions between UI and agent system.

    Processes user messages through the LangGraph agent system
    and returns responses.
    """

    def __init__(self, graph=None):
        """
        Initialize chat handler.

        Args:
            graph: Optional LangGraph instance. If None, uses mock responses.
        """
        self.graph = graph
        self._use_mock = graph is None

    def process_message(self, user_input: str, context: dict = None) -> str:
        """
        Process a user message and return agent response.

        Args:
            user_input: The user's message
            context: Optional context dict (tasks, calendar, etc.)

        Returns:
            Agent response string
        """
        logger.info(f"Processing message: {user_input[:50]}...")

        if self._use_mock:
            return self._mock_response(user_input)

        try:
            # Run through agent graph
            result = self._run_graph(user_input, context or {})
            return result
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def _run_graph(self, user_input: str, context: dict) -> str:
        """Run message through the agent graph."""
        try:
            from adhd_planner.graph.state_utils import StateManager

            # Create initial state
            state = StateManager.create_initial_state(user_input)
            state["context"] = context

            # Run graph
            result = self.graph.invoke(state)

            # Extract response from last AI message
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.type == "ai":
                    return msg.content

            return "I processed your request but have no response."
        except Exception as e:
            logger.error(f"Error running graph: {e}")
            raise

    def _mock_response(self, user_input: str) -> str:
        """Generate mock response for development/testing."""
        user_lower = user_input.lower()

        if "add task" in user_lower or "create task" in user_lower:
            return "I'd be happy to help you add a task! Could you tell me:\n- What's the task?\n- How long do you think it will take?\n- What's the priority (high/medium/low)?"

        if "plan" in user_lower and "day" in user_lower:
            return "Let me help you plan your day! Based on your tasks, I suggest:\n\n1. **Morning** (High energy): Focus on your most important task\n2. **Midday**: Handle meetings and collaborative work\n3. **Afternoon**: Lighter tasks and admin work\n\nWould you like me to create time blocks for this?"

        if "schedule" in user_lower:
            return "I can help with scheduling! Tell me what you'd like to schedule and I'll find the best time based on your energy patterns."

        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return "Hello! 👋 I'm your ADHD planning assistant. I can help you:\n- Add and manage tasks\n- Plan your day\n- Schedule activities\n- Track your energy\n\nWhat would you like to do?"

        return "I understand you want to: " + user_input + "\n\nHow can I help you with this?"

    def stream_response(self, user_input: str, context: dict = None) -> Generator[str, None, None]:
        """
        Stream response word by word for better UX.

        Args:
            user_input: User message
            context: Optional context

        Yields:
            Response words/chunks
        """
        response = self.process_message(user_input, context)

        # Simple word-by-word streaming
        words = response.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
