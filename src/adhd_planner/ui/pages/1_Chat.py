"""Chat page - conversational interface with AI assistant."""

import streamlit as st

from adhd_planner.core.chat_handler import ChatHandler
from adhd_planner.core.session_manager import SessionManager
from adhd_planner.ui.components.chat_message import display_message, display_message_history

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
            # Also clear handler context for fresh conversation
            handler = get_chat_handler()
            handler.clear_context()
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
