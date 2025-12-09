# ADHD-17: Streamlit App Structure

## Story Information
- **Epic**: Epic 4 - Streamlit UI
- **Story ID**: ADHD-17
- **Estimated Time**: 2 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-16: Graph Builder & Integration

## Description

Set up the main Streamlit application structure with multi-page navigation, session state management, and the core session manager. This establishes the UI foundation that all subsequent pages will build upon.

**MVP Focus**: Simple, functional navigation with basic session management. No over-engineering.

## Goals

1. Create main app entry point with page navigation
2. Implement session manager for state persistence
3. Set up basic navigation sidebar
4. Configure Streamlit page settings

## Acceptance Criteria

### Main App
- [ ] Entry point `app.py` with page configuration
- [ ] Multi-page navigation using Streamlit's native page system
- [ ] Basic sidebar with navigation links
- [ ] Page title and favicon configuration

### Session Manager
- [ ] Session state initialization
- [ ] User context management (current user, preferences)
- [ ] Service initialization (lazy loading)
- [ ] Basic state persistence across page navigations

### Navigation
- [ ] Sidebar with 4 page links: Chat, Tasks, Calendar, Settings
- [ ] Current page indicator
- [ ] Clean, minimal styling

## Files to Create/Modify

### New Files
```
src/adhd_planner/ui/
├── app.py                      # Main entry point
├── pages/
│   ├── 1_💬_Chat.py            # Chat page placeholder
│   ├── 2_📋_Tasks.py           # Tasks page placeholder
│   ├── 3_📅_Calendar.py        # Calendar page placeholder
│   └── 4_⚙️_Settings.py        # Settings page placeholder

src/adhd_planner/core/
└── session_manager.py          # Session state management

tests/unit/
└── test_session_manager.py     # Session manager tests
```

## Implementation Steps

### Step 1: Create Session Manager (30 min)

Create `src/adhd_planner/core/session_manager.py`:

```python
"""Session management for Streamlit application."""

from typing import Any
import streamlit as st

from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """
    Manages Streamlit session state for the application.

    Handles initialization of services, user context, and state persistence
    across page navigations.
    """

    # Session state keys
    INITIALIZED = "initialized"
    USER_ID = "user_id"
    MESSAGES = "messages"
    CURRENT_PAGE = "current_page"

    @classmethod
    def initialize(cls) -> None:
        """Initialize session state if not already done."""
        if not st.session_state.get(cls.INITIALIZED):
            logger.info("Initializing session state")
            st.session_state[cls.INITIALIZED] = True
            st.session_state[cls.USER_ID] = "default_user"
            st.session_state[cls.MESSAGES] = []
            st.session_state[cls.CURRENT_PAGE] = "Chat"
            cls._initialize_services()

    @classmethod
    def _initialize_services(cls) -> None:
        """Lazy initialize services in session state."""
        # Services will be initialized on first access
        if "services_initialized" not in st.session_state:
            st.session_state["services_initialized"] = False

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from session state."""
        return st.session_state.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a value in session state."""
        st.session_state[key] = value

    @classmethod
    def get_messages(cls) -> list:
        """Get chat message history."""
        return st.session_state.get(cls.MESSAGES, [])

    @classmethod
    def add_message(cls, role: str, content: str) -> None:
        """Add a message to chat history."""
        if cls.MESSAGES not in st.session_state:
            st.session_state[cls.MESSAGES] = []
        st.session_state[cls.MESSAGES].append({
            "role": role,
            "content": content
        })

    @classmethod
    def clear_messages(cls) -> None:
        """Clear chat message history."""
        st.session_state[cls.MESSAGES] = []

    @classmethod
    def get_user_id(cls) -> str:
        """Get current user ID."""
        return st.session_state.get(cls.USER_ID, "default_user")
```

### Step 2: Create Main App Entry Point (30 min)

Create `src/adhd_planner/ui/app.py`:

```python
"""Main Streamlit application entry point."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="ADHD Planner",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session
SessionManager.initialize()


def main():
    """Main application entry point."""
    # Sidebar
    with st.sidebar:
        st.title("🧠 ADHD Planner")
        st.markdown("---")
        st.markdown("Your AI-powered planning assistant")

        # Navigation info
        st.markdown("### Navigation")
        st.markdown("""
        - 💬 **Chat** - Talk to your assistant
        - 📋 **Tasks** - Manage your tasks
        - 📅 **Calendar** - View your schedule
        - ⚙️ **Settings** - Configure preferences
        """)

    # Main content area - welcome page
    st.title("Welcome to ADHD Planner")
    st.markdown("""
    👋 **Get started by selecting a page from the sidebar!**

    ### Quick Start
    - **Chat**: Ask me to help plan your day or add tasks
    - **Tasks**: View and manage all your tasks
    - **Calendar**: See your schedule at a glance
    - **Settings**: Customize your experience

    ### Tips for ADHD-Friendly Planning
    - 🎯 Start with just 3 important tasks for today
    - ⚡ Schedule high-energy tasks when you feel most alert
    - 🧘 Build in buffer time between tasks
    - 🎉 Celebrate small wins!
    """)


if __name__ == "__main__":
    main()
```

### Step 3: Create Page Placeholders (30 min)

Create `src/adhd_planner/ui/pages/1_💬_Chat.py`:

```python
"""Chat page - conversational interface with AI assistant."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager

st.set_page_config(page_title="Chat - ADHD Planner", page_icon="💬")

SessionManager.initialize()

st.title("💬 Chat")
st.markdown("Talk to your AI planning assistant.")

# Placeholder for chat interface (ADHD-18)
st.info("Chat interface coming soon! This will be implemented in ADHD-18.")

# Basic message display
messages = SessionManager.get_messages()
if messages:
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Simple input for now
if prompt := st.chat_input("What would you like to do?"):
    SessionManager.add_message("user", prompt)
    st.rerun()
```

Create `src/adhd_planner/ui/pages/2_📋_Tasks.py`:

```python
"""Tasks page - task management interface."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager

st.set_page_config(page_title="Tasks - ADHD Planner", page_icon="📋")

SessionManager.initialize()

st.title("📋 Tasks")
st.markdown("Manage your tasks.")

# Placeholder for task list (ADHD-19)
st.info("Task management interface coming soon! This will be implemented in ADHD-19.")

# Basic demo content
st.markdown("### Your Tasks")
st.markdown("- [ ] Example task 1")
st.markdown("- [ ] Example task 2")
st.markdown("- [x] Completed task")
```

Create `src/adhd_planner/ui/pages/3_📅_Calendar.py`:

```python
"""Calendar page - schedule and time block view."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager

st.set_page_config(page_title="Calendar - ADHD Planner", page_icon="📅")

SessionManager.initialize()

st.title("📅 Calendar")
st.markdown("View your schedule and time blocks.")

# Placeholder for calendar view (ADHD-20)
st.info("Calendar view coming soon! This will be implemented in ADHD-20.")

# Basic date display
import datetime
today = datetime.date.today()
st.markdown(f"### Today: {today.strftime('%A, %B %d, %Y')}")
```

Create `src/adhd_planner/ui/pages/4_⚙️_Settings.py`:

```python
"""Settings page - user preferences and configuration."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager

st.set_page_config(page_title="Settings - ADHD Planner", page_icon="⚙️")

SessionManager.initialize()

st.title("⚙️ Settings")
st.markdown("Configure your preferences.")

# Placeholder for settings form (ADHD-21)
st.info("Settings interface coming soon! This will be implemented in ADHD-21.")

# Basic settings preview
st.markdown("### Available Settings")
st.markdown("""
- LLM Provider configuration
- Working hours preferences
- Energy pattern settings
- Apple sync options
""")
```

### Step 4: Update Package Init (10 min)

Update `src/adhd_planner/core/__init__.py`:

```python
"""Core business logic and session management."""

from adhd_planner.core.session_manager import SessionManager

__all__ = ["SessionManager"]
```

### Step 5: Create Tests (20 min)

Create `tests/unit/test_session_manager.py`:

```python
"""Tests for SessionManager."""

import pytest
from unittest.mock import MagicMock, patch


class TestSessionManager:
    """Test SessionManager functionality."""

    @pytest.fixture
    def mock_session_state(self):
        """Create mock session state."""
        return {}

    @patch("streamlit.session_state", new_callable=dict)
    def test_initialize(self, mock_state):
        """Test session initialization."""
        from adhd_planner.core.session_manager import SessionManager

        SessionManager.initialize()

        assert mock_state["initialized"] is True
        assert mock_state["user_id"] == "default_user"
        assert mock_state["messages"] == []

    @patch("streamlit.session_state", new_callable=dict)
    def test_get_and_set(self, mock_state):
        """Test get and set operations."""
        from adhd_planner.core.session_manager import SessionManager

        SessionManager.set("test_key", "test_value")
        assert SessionManager.get("test_key") == "test_value"
        assert SessionManager.get("missing_key", "default") == "default"

    @patch("streamlit.session_state", new_callable=dict)
    def test_message_management(self, mock_state):
        """Test message add and get."""
        from adhd_planner.core.session_manager import SessionManager

        mock_state["messages"] = []

        SessionManager.add_message("user", "Hello")
        SessionManager.add_message("assistant", "Hi there!")

        messages = SessionManager.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["content"] == "Hi there!"

    @patch("streamlit.session_state", new_callable=dict)
    def test_clear_messages(self, mock_state):
        """Test clearing messages."""
        from adhd_planner.core.session_manager import SessionManager

        mock_state["messages"] = [{"role": "user", "content": "test"}]

        SessionManager.clear_messages()

        assert mock_state["messages"] == []
```

## Testing Checklist

- [ ] Run `uv run streamlit run src/adhd_planner/ui/app.py`
- [ ] Main page loads without errors
- [ ] Sidebar displays correctly
- [ ] All 4 page links are visible
- [ ] Each page loads without errors
- [ ] Session state persists across page navigations
- [ ] Run `uv run pytest tests/unit/test_session_manager.py -v`
- [ ] All tests pass

## Success Criteria

- [ ] App launches successfully with `streamlit run`
- [ ] Multi-page navigation works
- [ ] Session manager initializes state correctly
- [ ] All placeholder pages load without errors
- [ ] Tests pass

## Implementation Notes

### Streamlit Multi-Page Apps
Streamlit uses filename-based routing. Files in `pages/` directory become pages automatically. The emoji prefix and number control the order and display name.

### Session State
Streamlit's `st.session_state` persists across reruns and page navigations. We wrap it in `SessionManager` for cleaner access and to centralize initialization logic.

### MVP Approach
- Keep it simple - just navigation and placeholders
- Don't add features not needed for basic navigation
- Pages will be fully implemented in subsequent stories

## Next Story

After completing this story, proceed to:
- **ADHD-18**: Chat Page & Components - Full chat interface implementation
