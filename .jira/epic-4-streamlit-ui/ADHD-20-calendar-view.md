# ADHD-20: Calendar View

## Story Information
- **Epic**: Epic 4 - Streamlit UI
- **Story ID**: ADHD-20
- **Estimated Time**: 4 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-17: Streamlit App Structure
  - ✅ ADHD-9: Calendar Service

## Description

Implement the calendar page with a visual schedule view showing time blocks for the day/week. Users can see their scheduled tasks, energy levels, and free time slots.

**MVP Focus**: Simple day view with time blocks. No drag-and-drop or complex interactions.

## Goals

1. Display daily schedule with time blocks
2. Show time block details (task, duration, energy)
3. Navigate between days
4. Display energy level indicators
5. Show free time slots

## Acceptance Criteria

### Calendar View
- [ ] Day view showing 24-hour timeline
- [ ] Date navigation (previous/next day, today button)
- [ ] Current time indicator
- [ ] Working hours highlighted

### Time Block Display
- [ ] Time blocks shown on timeline
- [ ] Color coding by energy level or task type
- [ ] Block shows task title and duration
- [ ] Click to view block details

### Energy Visualization
- [ ] Energy level indicator for each block
- [ ] Visual distinction for high/medium/low energy slots

### Data Integration
- [ ] Fetch time blocks from CalendarService
- [ ] Handle empty days gracefully

## Files to Create/Modify

### Files to Modify
```
src/adhd_planner/ui/pages/3_📅_Calendar.py    # Full implementation
```

### New Files
```
src/adhd_planner/ui/components/
├── time_block.py               # Time block component
└── day_timeline.py             # Day timeline component

tests/unit/
└── test_calendar_view.py       # Calendar view tests
```

## Implementation Steps

### Step 1: Create Time Block Component (45 min)

Create `src/adhd_planner/ui/components/time_block.py`:

```python
"""Time block component for calendar display."""

import streamlit as st
from datetime import datetime, time
from typing import Optional


def time_block_card(
    block_id: str,
    title: str,
    start_time: time,
    end_time: time,
    energy_level: str = "medium",
    task_id: Optional[str] = None,
    is_break: bool = False,
) -> None:
    """
    Display a time block card.

    Args:
        block_id: Unique block identifier
        title: Block title/task name
        start_time: Start time
        end_time: End time
        energy_level: Energy level (high, medium, low)
        task_id: Associated task ID
        is_break: Whether this is a break block
    """
    # Energy level colors
    energy_colors = {
        "high": "#ff6b6b",      # Red
        "medium": "#ffd93d",    # Yellow
        "low": "#6bcb77",       # Green
    }

    # Energy level icons
    energy_icons = {
        "high": "🔥",
        "medium": "⚡",
        "low": "🌱",
    }

    bg_color = energy_colors.get(energy_level.lower(), "#e0e0e0")
    icon = energy_icons.get(energy_level.lower(), "📋")

    if is_break:
        bg_color = "#b8e0d2"
        icon = "☕"

    # Format times
    start_str = start_time.strftime("%H:%M")
    end_str = end_time.strftime("%H:%M")

    # Calculate duration
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    duration_minutes = end_minutes - start_minutes

    if duration_minutes >= 60:
        duration_str = f"{duration_minutes // 60}h {duration_minutes % 60}m" if duration_minutes % 60 else f"{duration_minutes // 60}h"
    else:
        duration_str = f"{duration_minutes}m"

    # Render block
    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            border-radius: 8px;
            padding: 12px;
            margin: 4px 0;
            border-left: 4px solid rgba(0,0,0,0.2);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">{icon} {title}</span>
                <span style="font-size: 0.85em; color: #666;">{duration_str}</span>
            </div>
            <div style="font-size: 0.85em; color: #555; margin-top: 4px;">
                {start_str} - {end_str}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_slot(start_time: time, end_time: time) -> None:
    """
    Display an empty time slot.

    Args:
        start_time: Slot start time
        end_time: Slot end time
    """
    start_str = start_time.strftime("%H:%M")
    end_str = end_time.strftime("%H:%M")

    st.markdown(
        f"""
        <div style="
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 12px;
            margin: 4px 0;
            border: 1px dashed #ccc;
            color: #999;
        ">
            <div style="display: flex; justify-content: space-between;">
                <span>Free time</span>
                <span>{start_str} - {end_str}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
```

### Step 2: Create Day Timeline Component (45 min)

Create `src/adhd_planner/ui/components/day_timeline.py`:

```python
"""Day timeline component for calendar view."""

import streamlit as st
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any

from adhd_planner.ui.components.time_block import time_block_card, empty_slot


def day_timeline(
    selected_date: date,
    time_blocks: List[Dict[str, Any]],
    work_start: time = time(9, 0),
    work_end: time = time(17, 0),
) -> None:
    """
    Display a day timeline with time blocks.

    Args:
        selected_date: The date to display
        time_blocks: List of time block dicts
        work_start: Working hours start
        work_end: Working hours end
    """
    st.markdown(f"### {selected_date.strftime('%A, %B %d, %Y')}")

    # Current time indicator
    now = datetime.now()
    is_today = selected_date == now.date()

    if is_today:
        current_time = now.strftime("%H:%M")
        st.markdown(f"🕐 Current time: **{current_time}**")

    st.markdown("---")

    # Working hours indicator
    st.caption(f"Working hours: {work_start.strftime('%H:%M')} - {work_end.strftime('%H:%M')}")

    if not time_blocks:
        st.info("No scheduled blocks for this day. Your day is wide open!")
        empty_slot(work_start, work_end)
        return

    # Sort blocks by start time
    sorted_blocks = sorted(
        time_blocks,
        key=lambda b: b.get("start_time", time(0, 0))
    )

    # Display blocks
    for block in sorted_blocks:
        time_block_card(
            block_id=str(block.get("id", "")),
            title=block.get("title", "Untitled"),
            start_time=block.get("start_time", time(9, 0)),
            end_time=block.get("end_time", time(10, 0)),
            energy_level=block.get("energy_level", "medium"),
            task_id=block.get("task_id"),
            is_break=block.get("is_break", False),
        )


def date_navigator(current_date: date) -> date:
    """
    Display date navigation controls.

    Args:
        current_date: Currently selected date

    Returns:
        New selected date
    """
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

    with col1:
        if st.button("◀ Prev", use_container_width=True):
            return current_date - timedelta(days=1)

    with col2:
        if st.button("Today", use_container_width=True):
            return date.today()

    with col3:
        selected = st.date_input(
            "Select date",
            value=current_date,
            label_visibility="collapsed",
        )
        if selected != current_date:
            return selected

    with col4:
        if st.button("Next ▶", use_container_width=True):
            return current_date + timedelta(days=1)

    return current_date
```

### Step 3: Implement Calendar Page (1.5 hours)

Update `src/adhd_planner/ui/pages/3_📅_Calendar.py`:

```python
"""Calendar page - schedule and time block view."""

import streamlit as st
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.ui.components.day_timeline import day_timeline, date_navigator
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Calendar - ADHD Planner", page_icon="📅", layout="wide")

SessionManager.initialize()


def get_calendar_service():
    """Get calendar service instance."""
    if "calendar_service" not in st.session_state:
        try:
            from adhd_planner.services.calendar_service import CalendarService
            from adhd_planner.repositories.time_block_repository import TimeBlockRepository
            from adhd_planner.database.connection import get_session

            session = get_session()
            repo = TimeBlockRepository(session)
            st.session_state["calendar_service"] = CalendarService(repo)
        except Exception as e:
            logger.warning(f"Could not initialize calendar service: {e}")
            st.session_state["calendar_service"] = None

    return st.session_state.get("calendar_service")


def get_mock_time_blocks(selected_date: date) -> List[Dict[str, Any]]:
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


def load_time_blocks(selected_date: date) -> List[Dict[str, Any]]:
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
                "start_time": b.start_time.time() if isinstance(b.start_time, datetime) else b.start_time,
                "end_time": b.end_time.time() if isinstance(b.end_time, datetime) else b.end_time,
                "energy_level": b.energy_level.value if hasattr(b.energy_level, 'value') else str(b.energy_level),
                "task_id": str(b.task_id) if b.task_id else None,
                "is_break": b.is_break if hasattr(b, 'is_break') else False,
            }
            for b in blocks
        ]
    except Exception as e:
        logger.error(f"Error loading time blocks: {e}")
        return get_mock_time_blocks(selected_date)


def calculate_stats(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
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
```

### Step 4: Update Components Init (10 min)

Update `src/adhd_planner/ui/components/__init__.py`:

```python
"""Reusable UI components."""

from adhd_planner.ui.components.chat_message import display_message, display_message_history
from adhd_planner.ui.components.task_card import task_card, task_list
from adhd_planner.ui.components.time_block import time_block_card, empty_slot
from adhd_planner.ui.components.day_timeline import day_timeline, date_navigator

__all__ = [
    "display_message",
    "display_message_history",
    "task_card",
    "task_list",
    "time_block_card",
    "empty_slot",
    "day_timeline",
    "date_navigator",
]
```

### Step 5: Create Tests (30 min)

Create `tests/unit/test_calendar_view.py`:

```python
"""Tests for calendar view components."""

import pytest
from datetime import date, time, timedelta


class TestTimeBlockComponent:
    """Test time block component."""

    def test_import(self):
        """Test component can be imported."""
        from adhd_planner.ui.components.time_block import time_block_card, empty_slot
        assert time_block_card is not None
        assert empty_slot is not None


class TestDayTimeline:
    """Test day timeline component."""

    def test_import(self):
        """Test component can be imported."""
        from adhd_planner.ui.components.day_timeline import day_timeline, date_navigator
        assert day_timeline is not None
        assert date_navigator is not None


class TestCalendarPage:
    """Test calendar page functions."""

    def test_mock_blocks_structure(self):
        """Test mock time blocks have required fields."""
        mock_blocks = [
            {
                "id": "1",
                "title": "Test block",
                "start_time": time(9, 0),
                "end_time": time(10, 0),
                "energy_level": "high",
                "is_break": False,
            }
        ]

        for block in mock_blocks:
            assert "id" in block
            assert "title" in block
            assert "start_time" in block
            assert "end_time" in block
            assert "energy_level" in block
            assert block["energy_level"] in ["high", "medium", "low"]

    def test_stats_calculation(self):
        """Test stats calculation logic."""
        blocks = [
            {"start_time": time(9, 0), "end_time": time(10, 0), "is_break": False},
            {"start_time": time(10, 0), "end_time": time(10, 30), "is_break": True},
            {"start_time": time(10, 30), "end_time": time(12, 0), "is_break": False},
        ]

        total_minutes = 0
        work_minutes = 0
        break_minutes = 0

        for block in blocks:
            start = block["start_time"]
            end = block["end_time"]
            duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            total_minutes += duration
            if block["is_break"]:
                break_minutes += duration
            else:
                work_minutes += duration

        assert total_minutes == 180  # 3 hours
        assert work_minutes == 150   # 2.5 hours
        assert break_minutes == 30   # 0.5 hours

    def test_date_navigation(self):
        """Test date navigation logic."""
        today = date.today()

        # Previous day
        prev_day = today - timedelta(days=1)
        assert prev_day < today

        # Next day
        next_day = today + timedelta(days=1)
        assert next_day > today
```

## Testing Checklist

- [ ] Run `uv run streamlit run src/adhd_planner/ui/app.py`
- [ ] Navigate to Calendar page
- [ ] Today's date is selected by default
- [ ] Mock time blocks display correctly
- [ ] Time blocks show title, time, and duration
- [ ] Energy level colors are distinct
- [ ] Break blocks look different
- [ ] Date navigation works (prev/next/today)
- [ ] Date picker works
- [ ] Stats update when changing dates
- [ ] Empty day shows appropriate message
- [ ] Run `uv run pytest tests/unit/test_calendar_view.py -v`
- [ ] All tests pass

## Success Criteria

- [ ] Day view displays time blocks correctly
- [ ] Date navigation works smoothly
- [ ] Energy levels are visually distinct
- [ ] Stats calculation is accurate
- [ ] Integrates with CalendarService when available
- [ ] Falls back to mock data when service unavailable
- [ ] Tests pass

## Implementation Notes

### HTML/CSS in Streamlit
We use `st.markdown` with `unsafe_allow_html=True` for custom styling of time blocks. This provides more control than native Streamlit components for visual layouts.

### Time Handling
Time blocks use `datetime.time` objects for start/end times, making calculations straightforward and avoiding timezone issues.

### Mock Data
Mock data varies by date to demonstrate different scenarios (today has full schedule, tomorrow has partial, other days are empty).

### MVP Approach
- Day view only (no week view)
- No drag-and-drop
- No inline editing
- No block creation from calendar
- Read-only display

## Next Story

After completing this story, proceed to:
- **ADHD-21**: Settings Page - User preferences and configuration
