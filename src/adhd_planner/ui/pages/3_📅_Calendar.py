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


def get_calendar_service():
    """Get calendar service instance."""
    if "calendar_service" not in st.session_state:
        try:
            from adhd_planner.database.connection import get_session
            from adhd_planner.repositories.time_block_repository import TimeBlockRepository
            from adhd_planner.services.calendar_service import CalendarService

            session = get_session()
            repo = TimeBlockRepository(session)
            st.session_state["calendar_service"] = CalendarService(repo)
        except Exception as e:
            logger.warning(f"Could not initialize calendar service: {e}")
            st.session_state["calendar_service"] = None

    return st.session_state.get("calendar_service")


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


def load_time_blocks(selected_date: date) -> list[dict[str, Any]]:
    """Load time blocks for a given date."""
    service = get_calendar_service()

    if service is None:
        return get_mock_time_blocks(selected_date)

    try:
        blocks = service.get_time_blocks_for_date(selected_date)
        return [
            {
                "id": str(b.id),
                "title": b.title,
                "start_time": b.start_time.time()
                if isinstance(b.start_time, datetime)
                else b.start_time,
                "end_time": b.end_time.time() if isinstance(b.end_time, datetime) else b.end_time,
                "energy_level": b.energy_level.value
                if hasattr(b.energy_level, "value")
                else str(b.energy_level),
                "task_id": str(b.task_id) if b.task_id else None,
                "is_break": b.is_break if hasattr(b, "is_break") else False,
            }
            for b in blocks
        ]
    except Exception as e:
        logger.error(f"Error loading time blocks: {e}")
        return get_mock_time_blocks(selected_date)


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
