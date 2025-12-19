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
