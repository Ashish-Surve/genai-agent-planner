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
        st.session_state[cls.MESSAGES].append({"role": role, "content": content})

    @classmethod
    def clear_messages(cls) -> None:
        """Clear chat message history."""
        st.session_state[cls.MESSAGES] = []

    @classmethod
    def get_user_id(cls) -> str:
        """Get current user ID."""
        return st.session_state.get(cls.USER_ID, "default_user")
