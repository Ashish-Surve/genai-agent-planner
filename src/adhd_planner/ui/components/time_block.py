"""Time block component for calendar display."""

from datetime import time

import streamlit as st


def time_block_card(
    block_id: str,
    title: str,
    start_time: time,
    end_time: time,
    energy_level: str = "medium",
    task_id: str | None = None,
    is_break: bool = False,
    on_click: callable | None = None,
) -> bool:
    """
    Display a time block card with optional click handling.

    Args:
        block_id: Unique block identifier
        title: Block title/task name
        start_time: Start time
        end_time: End time
        energy_level: Energy level (high, medium, low)
        task_id: Associated task ID (unused, kept for compatibility)
        is_break: Whether this is a break block
        on_click: Callback when block is clicked (receives block_id)

    Returns:
        True if the block was clicked, False otherwise
    """
    # Energy level colors
    energy_colors = {
        "high": "#ff6b6b",  # Red
        "medium": "#ffd93d",  # Yellow
        "low": "#6bcb77",  # Green
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
        duration_str = (
            f"{duration_minutes // 60}h {duration_minutes % 60}m"
            if duration_minutes % 60
            else f"{duration_minutes // 60}h"
        )
    else:
        duration_str = f"{duration_minutes}m"

    # Create a container for the block with edit button
    clicked = False
    with st.container():
        col1, col2 = st.columns([9, 1])

        with col1:
            # Render block content
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

        with col2:
            # Show edit button for all blocks (not just those with tasks)
            if on_click and block_id:
                if st.button("✏️", key=f"edit_block_{block_id}", help="Edit time block"):
                    on_click(block_id)
                    clicked = True

    return clicked


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
