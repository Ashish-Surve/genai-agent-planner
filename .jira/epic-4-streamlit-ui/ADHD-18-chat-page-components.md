# ADHD-18: Chat Page & Components

## Story Information
- **Epic**: Epic 4 - Streamlit UI
- **Story ID**: ADHD-18
- **Estimated Time**: 3 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-17: Streamlit App Structure
  - ✅ ADHD-16: Graph Builder & Integration

## Description

Implement the chat page with a conversational interface for interacting with the AI planning assistant. Users can add tasks, ask questions, and get scheduling suggestions through natural language.

**MVP Focus**: Working chat interface that connects to the agent system. Keep UI simple.

## Goals

1. Create chat interface with message history display
2. Connect chat to LangGraph agent system
3. Handle user input and agent responses
4. Display typing indicators and loading states

## Acceptance Criteria

### Chat Interface
- [ ] Message history display with user/assistant bubbles
- [ ] Chat input at bottom of page
- [ ] Clear conversation button
- [ ] Auto-scroll to latest message

### Agent Integration
- [ ] User messages sent to agent graph
- [ ] Agent responses displayed in chat
- [ ] Error handling for agent failures
- [ ] Loading state while agent processes

### User Experience
- [ ] Messages persist in session state
- [ ] Responsive layout
- [ ] Clear visual distinction between user and assistant messages

## Files to Create/Modify

### Files to Modify
```
src/adhd_planner/ui/pages/1_💬_Chat.py    # Full implementation
```

### New Files
```
src/adhd_planner/ui/components/
├── chat_message.py             # Message display component
└── chat_input.py               # Input component

src/adhd_planner/core/
└── chat_handler.py             # Agent integration logic

tests/unit/
└── test_chat_handler.py        # Chat handler tests
```

## Implementation Steps

### Step 1: Create Chat Handler (45 min)

Create `src/adhd_planner/core/chat_handler.py`:

```python
"""Chat handler for processing user messages through the agent system."""

from typing import Generator

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
```

### Step 2: Create Chat Message Component (30 min)

Create `src/adhd_planner/ui/components/chat_message.py`:

```python
"""Chat message display component."""

import streamlit as st


def display_message(role: str, content: str) -> None:
    """
    Display a chat message.

    Args:
        role: "user" or "assistant"
        content: Message content (supports markdown)
    """
    avatar = "👤" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def display_message_history(messages: list) -> None:
    """
    Display all messages in history.

    Args:
        messages: List of {"role": str, "content": str} dicts
    """
    for msg in messages:
        display_message(msg["role"], msg["content"])
```

### Step 3: Create Chat Input Component (20 min)

Create `src/adhd_planner/ui/components/chat_input.py`:

```python
"""Chat input component."""

import streamlit as st
from typing import Callable


def chat_input_area(on_submit: Callable[[str], None], placeholder: str = "What would you like to do?") -> None:
    """
    Display chat input with submit handling.

    Args:
        on_submit: Callback function when user submits message
        placeholder: Input placeholder text
    """
    if prompt := st.chat_input(placeholder):
        on_submit(prompt)
```

### Step 4: Implement Full Chat Page (45 min)

Update `src/adhd_planner/ui/pages/1_💬_Chat.py`:

```python
"""Chat page - conversational interface with AI assistant."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.core.chat_handler import ChatHandler
from adhd_planner.ui.components.chat_message import display_message_history, display_message

st.set_page_config(page_title="Chat - ADHD Planner", page_icon="💬", layout="wide")

# Initialize session
SessionManager.initialize()


def get_chat_handler() -> ChatHandler:
    """Get or create chat handler."""
    if "chat_handler" not in st.session_state:
        # Try to load real graph, fall back to mock
        try:
            from adhd_planner.graph.builder import build_graph
            graph = build_graph()
            st.session_state["chat_handler"] = ChatHandler(graph=graph)
        except Exception:
            # Use mock handler for development
            st.session_state["chat_handler"] = ChatHandler()

    return st.session_state["chat_handler"]


def handle_user_input(user_input: str) -> None:
    """Process user input and get agent response."""
    # Add user message
    SessionManager.add_message("user", user_input)

    # Get response from agent
    handler = get_chat_handler()

    with st.spinner("Thinking..."):
        response = handler.process_message(user_input)

    # Add assistant response
    SessionManager.add_message("assistant", response)


def main():
    """Main chat page."""
    # Header
    st.title("💬 Chat with your Assistant")

    # Sidebar actions
    with st.sidebar:
        st.markdown("### Chat Actions")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            SessionManager.clear_messages()
            st.rerun()

        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("📝 Add a task", use_container_width=True):
            handle_user_input("I want to add a new task")
            st.rerun()

        if st.button("📅 Plan my day", use_container_width=True):
            handle_user_input("Help me plan my day")
            st.rerun()

        if st.button("💡 What should I do?", use_container_width=True):
            handle_user_input("What should I work on right now?")
            st.rerun()

    # Display message history
    messages = SessionManager.get_messages()

    if not messages:
        # Welcome message for empty chat
        st.markdown("""
        👋 **Welcome!** I'm your ADHD planning assistant.

        Try asking me to:
        - "Add task: write report, 2 hours, high priority"
        - "Plan my day"
        - "What should I work on now?"

        Or use the quick actions in the sidebar!
        """)
    else:
        display_message_history(messages)

    # Chat input
    if prompt := st.chat_input("What would you like to do?"):
        # Display user message immediately
        display_message("user", prompt)

        # Process and display response
        handle_user_input(prompt)
        st.rerun()


if __name__ == "__main__":
    main()
else:
    main()
```

### Step 5: Update Components Init (10 min)

Create/update `src/adhd_planner/ui/components/__init__.py`:

```python
"""Reusable UI components."""

from adhd_planner.ui.components.chat_message import display_message, display_message_history

__all__ = ["display_message", "display_message_history"]
```

### Step 6: Create Tests (30 min)

Create `tests/unit/test_chat_handler.py`:

```python
"""Tests for ChatHandler."""

import pytest
from unittest.mock import MagicMock, patch

from adhd_planner.core.chat_handler import ChatHandler


class TestChatHandler:
    """Test ChatHandler functionality."""

    def test_initialization_without_graph(self):
        """Test initialization without graph uses mock."""
        handler = ChatHandler()
        assert handler._use_mock is True

    def test_initialization_with_graph(self):
        """Test initialization with graph."""
        mock_graph = MagicMock()
        handler = ChatHandler(graph=mock_graph)
        assert handler._use_mock is False
        assert handler.graph == mock_graph

    def test_mock_response_greeting(self):
        """Test mock response for greeting."""
        handler = ChatHandler()
        response = handler.process_message("Hello!")

        assert "Hello" in response or "👋" in response
        assert "help" in response.lower()

    def test_mock_response_add_task(self):
        """Test mock response for adding task."""
        handler = ChatHandler()
        response = handler.process_message("Add task: write report")

        assert "task" in response.lower()

    def test_mock_response_plan_day(self):
        """Test mock response for planning day."""
        handler = ChatHandler()
        response = handler.process_message("Plan my day")

        assert "plan" in response.lower() or "morning" in response.lower()

    def test_mock_response_generic(self):
        """Test mock response for generic input."""
        handler = ChatHandler()
        response = handler.process_message("Something random")

        assert len(response) > 0

    def test_process_with_graph(self):
        """Test processing with actual graph."""
        mock_graph = MagicMock()

        # Mock the graph invoke to return a state with messages
        from langchain_core.messages import AIMessage
        mock_graph.invoke.return_value = {
            "messages": [AIMessage(content="Graph response")]
        }

        handler = ChatHandler(graph=mock_graph)
        response = handler.process_message("Test input")

        assert response == "Graph response"
        mock_graph.invoke.assert_called_once()

    def test_error_handling(self):
        """Test error handling when graph fails."""
        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = Exception("Graph error")

        handler = ChatHandler(graph=mock_graph)
        response = handler.process_message("Test")

        assert "error" in response.lower()

    def test_stream_response(self):
        """Test streaming response."""
        handler = ChatHandler()

        words = list(handler.stream_response("Hello"))

        assert len(words) > 0
        # Reconstruct and verify
        full_response = "".join(words)
        assert len(full_response) > 0
```

## Testing Checklist

- [ ] Run `uv run streamlit run src/adhd_planner/ui/app.py`
- [ ] Navigate to Chat page
- [ ] Type a message and press Enter
- [ ] Message appears in chat history
- [ ] Assistant responds (mock response)
- [ ] Clear chat button works
- [ ] Quick action buttons work
- [ ] Messages persist when switching pages and returning
- [ ] Run `uv run pytest tests/unit/test_chat_handler.py -v`
- [ ] All tests pass

## Success Criteria

- [ ] Chat interface displays messages correctly
- [ ] User can send messages and receive responses
- [ ] Mock responses work for development
- [ ] Agent integration works when graph is available
- [ ] Session state preserves messages
- [ ] Tests pass

## Implementation Notes

### Mock vs Real Agent
The `ChatHandler` defaults to mock responses when no graph is provided. This allows UI development to proceed independently of agent implementation. When the graph is available, it uses the real agent system.

### Streamlit Chat Components
We use Streamlit's native `st.chat_message` and `st.chat_input` for consistent styling and behavior. The `st.rerun()` call refreshes the page to show new messages.

### MVP Approach
- No streaming display (just show complete response)
- No typing indicators (just spinner)
- No advanced formatting
- Keep it functional first

## Next Story

After completing this story, proceed to:
- **ADHD-19**: Tasks Page & Components - Task list and management interface
