"""Tasks page - task management interface."""

from datetime import datetime

import streamlit as st

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.ui.components.task_card import task_list
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Tasks - ADHD Planner", page_icon="📋", layout="wide")

SessionManager.initialize()


def get_task_service():
    """Get task service instance."""
    if "task_service" not in st.session_state:
        try:
            from adhd_planner.database.connection import get_session
            from adhd_planner.repositories.task_repository import TaskRepository
            from adhd_planner.services.task_service import TaskService

            session = get_session()
            repo = TaskRepository(session)
            st.session_state["task_service"] = TaskService(repo)
        except Exception as e:
            logger.warning(f"Could not initialize task service: {e}")
            st.session_state["task_service"] = None

    return st.session_state.get("task_service")


def get_mock_tasks():
    """Return mock tasks for development."""
    return [
        {
            "id": "1",
            "title": "Write project documentation",
            "priority": "high",
            "status": "pending",
            "estimated_minutes": 120,
            "due_date": datetime(2024, 12, 15),
        },
        {
            "id": "2",
            "title": "Review pull requests",
            "priority": "medium",
            "status": "in_progress",
            "estimated_minutes": 60,
            "due_date": None,
        },
        {
            "id": "3",
            "title": "Send weekly update email",
            "priority": "low",
            "status": "completed",
            "estimated_minutes": 15,
            "due_date": datetime(2024, 12, 10),
        },
    ]


def load_tasks(status_filter: str = "all", priority_filter: str = "all", sort_by: str = "created"):
    """Load tasks with filters applied."""
    service = get_task_service()

    if service is None:
        # Use mock data for development
        tasks = get_mock_tasks()
    else:
        try:
            tasks = service.get_all_tasks()
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            tasks = get_mock_tasks()

    # Apply status filter
    if status_filter != "all":
        tasks = [
            t
            for t in tasks
            if (t.get("status") if isinstance(t, dict) else t.status.value) == status_filter
        ]

    # Apply priority filter
    if priority_filter != "all":
        tasks = [
            t
            for t in tasks
            if (t.get("priority") if isinstance(t, dict) else t.priority.value) == priority_filter
        ]

    return tasks


def handle_complete_task(task_id: str):
    """Handle task completion."""
    logger.info(f"Completing task: {task_id}")
    service = get_task_service()

    if service:
        try:
            service.complete_task(task_id)
        except Exception as e:
            st.error(f"Error completing task: {e}")

    st.rerun()


def handle_delete_task(task_id: str):
    """Handle task deletion."""
    logger.info(f"Deleting task: {task_id}")
    service = get_task_service()

    if service:
        try:
            service.delete_task(task_id)
        except Exception as e:
            st.error(f"Error deleting task: {e}")

    st.rerun()


def add_task_form():
    """Display add task form in sidebar."""
    with st.form("add_task_form"):
        st.subheader("➕ Add New Task")

        title = st.text_input("Task Title *", placeholder="What needs to be done?")

        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        with col2:
            hours = st.number_input("Hours", min_value=0, max_value=8, value=1)
            minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0, step=15)

        due_date = st.date_input("Due Date (optional)", value=None)

        submitted = st.form_submit_button("Add Task", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Please enter a task title")
                return

            estimated_minutes = (hours * 60) + minutes

            service = get_task_service()
            if service:
                try:
                    service.create_task(
                        title=title,
                        priority=priority,
                        estimated_minutes=estimated_minutes,
                        due_date=datetime.combine(due_date, datetime.min.time())
                        if due_date
                        else None,
                    )
                    st.success("Task added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {e}")
            else:
                st.success("Task added! (mock mode)")
                st.rerun()


def main():
    """Main tasks page."""
    st.title("📋 Tasks")

    # Sidebar with add task form
    with st.sidebar:
        add_task_form()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["all", "pending", "in_progress", "completed"],
            format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All",
        )

    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["all", "high", "medium", "low"],
            format_func=lambda x: x.title() if x != "all" else "All",
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["created", "due_date", "priority"],
            format_func=lambda x: x.replace("_", " ").title(),
        )

    st.markdown("---")

    # Load and display tasks
    tasks = load_tasks(status_filter, priority_filter, sort_by)

    # Summary
    total = len(tasks)
    completed = len(
        [
            t
            for t in tasks
            if (t.get("status") if isinstance(t, dict) else t.status.value) == "completed"
        ]
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Remaining", total - completed)

    st.markdown("---")

    # Task list
    task_list(
        tasks=tasks,
        on_complete=handle_complete_task,
        on_delete=handle_delete_task,
    )


if __name__ == "__main__":
    main()
else:
    main()
