"""Task card component for displaying individual tasks."""

from collections.abc import Callable
from datetime import datetime

import streamlit as st


def task_card(
    task_id: str,
    title: str,
    priority: str,
    status: str,
    estimated_minutes: int | None = None,
    due_date: datetime | None = None,
    on_complete: Callable[[str], None] | None = None,
    on_delete: Callable[[str], None] | None = None,
) -> None:
    """
    Display a task card.

    Args:
        task_id: Unique task identifier
        title: Task title
        priority: Priority level (high, medium, low)
        status: Task status (pending, in_progress, completed)
        estimated_minutes: Estimated duration in minutes
        due_date: Optional due date
        on_complete: Callback when task is completed
        on_delete: Callback when task is deleted
    """
    # Priority colors (case-insensitive)
    priority_colors = {
        "urgent": "🔴",
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }

    # Status indicators (handle both uppercase and lowercase)
    is_completed = status.upper() == "COMPLETED"

    with st.container():
        col1, col2, col3 = st.columns([0.5, 8, 1.5])

        with col1:
            # Checkbox for completion
            def on_checkbox_change(task_id=task_id, on_complete=on_complete):
                if on_complete:
                    on_complete(task_id)

            st.checkbox(
                "Complete",
                value=is_completed,
                key=f"task_check_{task_id}",
                label_visibility="collapsed",
                on_change=on_checkbox_change,
            )

        with col2:
            # Task title with strikethrough if completed
            title_display = f"~~{title}~~" if is_completed else f"**{title}**"
            priority_icon = priority_colors.get(priority.lower(), "⚪")

            st.markdown(f"{priority_icon} {title_display}")

            # Details line
            details = []
            if estimated_minutes:
                hours = estimated_minutes // 60
                mins = estimated_minutes % 60
                if hours > 0:
                    details.append(f"⏱️ {hours}h {mins}m" if mins else f"⏱️ {hours}h")
                else:
                    details.append(f"⏱️ {mins}m")

            if due_date:
                details.append(f"📅 {due_date.strftime('%b %d')}")

            if details:
                st.caption(" • ".join(details))

        with col3:
            if st.button("🗑️", key=f"task_del_{task_id}", help="Delete task"):
                if on_delete:
                    on_delete(task_id)

        st.markdown("---")


def task_list(
    tasks: list,
    on_complete: Callable[[str], None] | None = None,
    on_delete: Callable[[str], None] | None = None,
) -> None:
    """
    Display a list of task cards.

    Args:
        tasks: List of task dicts/objects
        on_complete: Callback when a task is completed
        on_delete: Callback when a task is deleted
    """
    if not tasks:
        st.info("No tasks to display. Add your first task!")
        return

    for task in tasks:
        # Handle both dict and object access
        if isinstance(task, dict):
            task_card(
                task_id=str(task.get("id", "")),
                title=task.get("title", "Untitled"),
                priority=task.get("priority", "medium"),
                status=task.get("status", "pending"),
                estimated_minutes=task.get("estimated_minutes"),
                due_date=task.get("due_date"),
                on_complete=on_complete,
                on_delete=on_delete,
            )
        else:
            # Handle TaskModel objects with correct attribute names
            # TaskModel stores priority and status as strings, not enums
            task_card(
                task_id=str(task.id),
                title=task.title,
                priority=str(task.priority),
                status=str(task.status),
                estimated_minutes=getattr(task, "estimated_duration_minutes", None),
                due_date=getattr(task, "deadline", None),
                on_complete=on_complete,
                on_delete=on_delete,
            )
