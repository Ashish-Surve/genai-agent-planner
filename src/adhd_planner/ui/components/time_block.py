"""Time block component for calendar display."""

from datetime import time

import streamlit as st

# ADHD-friendly energy level colors (softer, easier on the eyes)
# Light mode colors
ENERGY_COLORS_LIGHT = {
    "high": "#F8D7DA",  # Soft pink/coral background
    "medium": "#FFF3CD",  # Soft warm yellow background
    "low": "#D4EDDA",  # Soft sage green background
}

# Dark mode colors (darker, muted versions)
ENERGY_COLORS_DARK = {
    "high": "#3D2A2E",  # Dark coral background
    "medium": "#3D3525",  # Dark warm yellow background
    "low": "#2A3D30",  # Dark sage green background
}

# Border colors for energy levels (slightly more saturated for visual distinction)
ENERGY_BORDER_COLORS = {
    "high": "#E07A5F",  # Coral
    "medium": "#F4A261",  # Soft orange
    "low": "#81B29A",  # Sage green
}

# Brighter border colors for dark mode
ENERGY_BORDER_COLORS_DARK = {
    "high": "#F28B7D",  # Lighter coral
    "medium": "#F7B87A",  # Lighter orange
    "low": "#8FD4A8",  # Lighter sage
}

ENERGY_ICONS = {
    "high": "🔥",
    "medium": "⚡",
    "low": "🌱",
}


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
    energy_lower = energy_level.lower()

    # Get colors for both modes
    bg_color_light = ENERGY_COLORS_LIGHT.get(energy_lower, "#F5F0E8")
    bg_color_dark = ENERGY_COLORS_DARK.get(energy_lower, "#2A2A3C")
    border_color_light = ENERGY_BORDER_COLORS.get(energy_lower, "#C5BEB3")
    border_color_dark = ENERGY_BORDER_COLORS_DARK.get(energy_lower, "#7A7A8C")
    icon = ENERGY_ICONS.get(energy_lower, "📋")

    if is_break:
        bg_color_light = "#E8F5E9"  # Soft mint green for breaks
        bg_color_dark = "#1E3D2E"  # Dark mint for breaks
        border_color_light = "#81B29A"
        border_color_dark = "#8FD4A8"
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
            # Render block content with ADHD-friendly styling and dark mode support
            st.markdown(
                f"""
                <style>
                    .time-block-{block_id} {{
                        background-color: {bg_color_light};
                        border-radius: 12px;
                        padding: 14px 16px;
                        margin: 6px 0;
                        border-left: 4px solid {border_color_light};
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        transition: all 0.2s ease;
                    }}
                    .time-block-{block_id} .block-title {{
                        font-weight: 600;
                        color: #2C3E50;
                    }}
                    .time-block-{block_id} .block-meta {{
                        font-size: 0.85em;
                        color: #5D6D7E;
                        font-weight: 500;
                    }}
                    .time-block-{block_id} .block-time {{
                        font-size: 0.85em;
                        color: #5D6D7E;
                        margin-top: 6px;
                    }}

                    @media (prefers-color-scheme: dark) {{
                        .time-block-{block_id} {{
                            background-color: {bg_color_dark} !important;
                            border-left-color: {border_color_dark} !important;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
                        }}
                        .time-block-{block_id} .block-title {{
                            color: #E8E8EC !important;
                        }}
                        .time-block-{block_id} .block-meta {{
                            color: #B8B8C4 !important;
                        }}
                        .time-block-{block_id} .block-time {{
                            color: #B8B8C4 !important;
                        }}
                    }}
                </style>
                <div class="time-block-{block_id}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="block-title">{icon} {title}</span>
                        <span class="block-meta">{duration_str}</span>
                    </div>
                    <div class="block-time">
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
            background-color: #FAF7F2;
            border-radius: 12px;
            padding: 14px 16px;
            margin: 6px 0;
            border: 2px dashed #E5E0D8;
            color: #95A5A6;
        ">
            <div style="display: flex; justify-content: space-between;">
                <span>✨ Free time - schedule something!</span>
                <span>{start_str} - {end_str}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
