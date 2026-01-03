"""Day timeline component for calendar view."""

from datetime import date, datetime, time, timedelta
from typing import Any

import streamlit as st

from adhd_planner.ui.components.time_block import empty_slot, time_block_card


def day_timeline(
    selected_date: date,
    time_blocks: list[dict[str, Any]],
    work_start: time = time(9, 0),
    work_end: time = time(17, 0),
    on_block_click: callable | None = None,
) -> None:
    """
    Display a day timeline with time blocks.

    Args:
        selected_date: The date to display
        time_blocks: List of time block dicts
        work_start: Working hours start
        work_end: Working hours end
        on_block_click: Callback when a time block is clicked (receives block_id)
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
    sorted_blocks = sorted(time_blocks, key=lambda b: b.get("start_time", time(0, 0)))

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
            on_click=on_block_click,
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
