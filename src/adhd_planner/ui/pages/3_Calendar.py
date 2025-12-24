"""Calendar page - schedule and time block view."""

from datetime import date, datetime, time, timedelta
from typing import Any

import streamlit as st

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.ui.components.day_timeline import date_navigator, day_timeline
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Calendar - ADHD Planner", page_icon="📅", layout="wide")

SessionManager.initialize()


def get_task_service():
    """
    Get task service instance with fresh session.

    Note: We create a fresh session each time to ensure data synchronization
    between pages (Calendar, Chat, Tasks).
    """
    try:
        from adhd_planner.database.connection import get_db
        from adhd_planner.services.task_service import TaskService

        db = get_db()
        session = db.session_factory()
        return TaskService(session)
    except Exception as e:
        logger.warning(f"Could not initialize task service: {e}")
        return None


def get_calendar_service():
    """
    Get calendar service instance with fresh session.

    Note: We create a fresh session each time to ensure data synchronization
    between pages (Calendar, Chat, Tasks).
    """
    try:
        from adhd_planner.database.connection import get_db
        from adhd_planner.services.calendar_service import CalendarService

        db = get_db()
        session = db.session_factory()
        return CalendarService(session)
    except Exception as e:
        logger.warning(f"Could not initialize calendar service: {e}")
        return None


def _get_block_title(block) -> str:
    """
    Get display title for a time block.

    Args:
        block: TimeBlock instance

    Returns:
        Human-readable title for the block
    """
    # If block has notes, use them as title
    if hasattr(block, "notes") and block.notes:
        return block.notes

    # If block is linked to a task, try to get task title
    if hasattr(block, "task") and block.task:
        return block.task.title

    # Otherwise, use block type as title
    block_type = (
        block.block_type.value if hasattr(block.block_type, "value") else str(block.block_type)
    )
    return f"{block_type.title()} Block"


def get_mock_time_blocks(selected_date: date) -> list[dict[str, Any]]:
    """Return mock time blocks for development."""
    if selected_date == date.today():
        return [
            {
                "id": "1",
                "title": "Morning planning",
                "start_time": time(9, 0),
                "end_time": time(9, 30),
                "energy_level": "high",
                "is_break": False,
            },
            {
                "id": "2",
                "title": "Deep work: Write documentation",
                "start_time": time(9, 30),
                "end_time": time(11, 30),
                "energy_level": "high",
                "task_id": "task_1",
                "is_break": False,
            },
            {
                "id": "3",
                "title": "Coffee break",
                "start_time": time(11, 30),
                "end_time": time(11, 45),
                "energy_level": "low",
                "is_break": True,
            },
            {
                "id": "4",
                "title": "Email and admin",
                "start_time": time(11, 45),
                "end_time": time(12, 30),
                "energy_level": "medium",
                "is_break": False,
            },
            {
                "id": "5",
                "title": "Lunch break",
                "start_time": time(12, 30),
                "end_time": time(13, 30),
                "energy_level": "low",
                "is_break": True,
            },
            {
                "id": "6",
                "title": "Review pull requests",
                "start_time": time(13, 30),
                "end_time": time(15, 0),
                "energy_level": "medium",
                "task_id": "task_2",
                "is_break": False,
            },
            {
                "id": "7",
                "title": "Wrap-up and planning for tomorrow",
                "start_time": time(16, 30),
                "end_time": time(17, 0),
                "energy_level": "low",
                "is_break": False,
            },
        ]
    elif selected_date == date.today() + timedelta(days=1):
        return [
            {
                "id": "10",
                "title": "Team standup",
                "start_time": time(9, 0),
                "end_time": time(9, 30),
                "energy_level": "medium",
                "is_break": False,
            },
            {
                "id": "11",
                "title": "Project work",
                "start_time": time(10, 0),
                "end_time": time(12, 0),
                "energy_level": "high",
                "is_break": False,
            },
        ]
    else:
        return []


def load_tasks_for_date(selected_date: date) -> list[dict[str, Any]]:
    """
    Load tasks with deadlines on the selected date.

    Returns tasks as calendar items that don't have time blocks yet.
    """
    task_service = get_task_service()

    if task_service is None:
        return []

    try:
        # Get all tasks
        all_tasks = task_service.list_tasks()

        # Filter tasks with deadline on selected date
        tasks_for_date = []
        for task in all_tasks:
            if hasattr(task, "deadline") and task.deadline:
                # Check if deadline is on selected date
                task_date = (
                    task.deadline.date() if isinstance(task.deadline, datetime) else task.deadline
                )
                if task_date == selected_date:
                    # Convert task to calendar item format
                    # Tasks without time blocks show as all-day events

                    # Get energy level - handle both enum and string
                    energy = "medium"
                    if hasattr(task, "estimated_energy_level") and task.estimated_energy_level:
                        if hasattr(task.estimated_energy_level, "value"):
                            energy = task.estimated_energy_level.value.lower()
                        else:
                            energy = str(task.estimated_energy_level).lower()

                    # Get priority - handle both enum and string
                    priority = "MEDIUM"
                    if hasattr(task, "priority") and task.priority:
                        if hasattr(task.priority, "value"):
                            priority = task.priority.value
                        else:
                            priority = str(task.priority)

                    # Get status - handle both enum and string
                    status = "NOT_STARTED"
                    if hasattr(task, "status") and task.status:
                        if hasattr(task.status, "value"):
                            status = task.status.value
                        else:
                            status = str(task.status)

                    tasks_for_date.append(
                        {
                            "id": f"task_{task.id}",
                            "title": f"📌 {task.title}",  # Prefix to indicate it's a task
                            "start_time": time(0, 0),  # All-day event
                            "end_time": time(23, 59),
                            "energy_level": energy,
                            "task_id": str(task.id),
                            "is_break": False,
                            "is_task_deadline": True,  # Flag to identify task deadlines
                            "priority": priority,
                            "status": status,
                        }
                    )

        return tasks_for_date

    except Exception as e:
        logger.error(f"Error loading tasks for date: {e}")
        return []


def load_time_blocks(selected_date: date) -> list[dict[str, Any]]:
    """
    Load time blocks and tasks for a given date.

    Combines:
    1. Scheduled time blocks
    2. Tasks with deadlines (that don't have time blocks yet)
    """
    calendar_service = get_calendar_service()

    # Start with scheduled time blocks
    time_blocks = []

    if calendar_service is not None:
        try:
            blocks = calendar_service.get_blocks_for_date(selected_date)
            time_blocks = [
                {
                    "id": str(b.id),
                    "title": _get_block_title(b),
                    "start_time": b.start_time.time()
                    if isinstance(b.start_time, datetime)
                    else b.start_time,
                    "end_time": b.end_time.time()
                    if isinstance(b.end_time, datetime)
                    else b.end_time,
                    "energy_level": (
                        b.energy_level_required.value
                        if hasattr(b, "energy_level_required") and b.energy_level_required
                        else "medium"
                    ),
                    "task_id": str(b.task_id) if b.task_id else None,
                    "is_break": b.block_type.value == "BREAK"
                    if hasattr(b.block_type, "value")
                    else b.block_type == "BREAK",
                    "is_task_deadline": False,
                }
                for b in blocks
            ]
        except Exception as e:
            logger.error(f"Error loading time blocks: {e}")

    # Add tasks with deadlines (if they don't already have time blocks)
    task_deadlines = load_tasks_for_date(selected_date)

    # Get task IDs that already have time blocks
    scheduled_task_ids = {str(b.get("task_id")) for b in time_blocks if b.get("task_id")}

    # Only add tasks that don't have time blocks yet
    for task_item in task_deadlines:
        task_id = task_item.get("task_id")
        if task_id not in scheduled_task_ids:
            time_blocks.append(task_item)

    # If no data available, use mock data
    if not time_blocks and calendar_service is None:
        return get_mock_time_blocks(selected_date)

    return time_blocks


def calculate_stats(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate daily statistics."""
    total_minutes = 0
    work_minutes = 0
    break_minutes = 0

    for block in blocks:
        start = block.get("start_time", time(0, 0))
        end = block.get("end_time", time(0, 0))

        start_mins = start.hour * 60 + start.minute
        end_mins = end.hour * 60 + end.minute
        duration = end_mins - start_mins

        total_minutes += duration
        if block.get("is_break"):
            break_minutes += duration
        else:
            work_minutes += duration

    return {
        "total_hours": total_minutes / 60,
        "work_hours": work_minutes / 60,
        "break_hours": break_minutes / 60,
        "block_count": len(blocks),
    }


def main():
    """Main calendar page."""
    st.title("📅 Calendar")

    # Initialize selected date in session state
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = date.today()

    # Sidebar with legend and quick actions
    with st.sidebar:
        st.markdown("### Energy Levels")
        st.markdown("🔥 **High** - Peak focus time")
        st.markdown("⚡ **Medium** - Regular work")
        st.markdown("🌱 **Low** - Light tasks")
        st.markdown("☕ **Break** - Rest time")

        st.markdown("---")

        st.markdown("### Tips")
        st.markdown("""
        - Schedule demanding tasks during high energy
        - Include buffer time between blocks
        - Don't forget breaks!
        """)

    # Date navigation
    new_date = date_navigator(st.session_state["selected_date"])
    if new_date != st.session_state["selected_date"]:
        st.session_state["selected_date"] = new_date
        st.rerun()

    st.markdown("---")

    # Load and display time blocks
    blocks = load_time_blocks(st.session_state["selected_date"])

    # Daily stats
    stats = calculate_stats(blocks)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Blocks", stats["block_count"])
    col2.metric("Total", f"{stats['total_hours']:.1f}h")
    col3.metric("Work", f"{stats['work_hours']:.1f}h")
    col4.metric("Breaks", f"{stats['break_hours']:.1f}h")

    st.markdown("---")

    # Timeline
    day_timeline(
        selected_date=st.session_state["selected_date"],
        time_blocks=blocks,
    )


if __name__ == "__main__":
    main()
else:
    main()
