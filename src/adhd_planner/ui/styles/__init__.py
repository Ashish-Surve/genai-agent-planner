"""ADHD-friendly styling and theming for the UI.

Research-based color choices for ADHD users:
- Softer, muted colors reduce visual overwhelm
- Warm tones (soft orange, peach) are calming yet energizing
- Cool blues/teals help with focus without being jarring
- High contrast for readability but not harsh backgrounds
- Consistent visual hierarchy reduces cognitive load
- Dark mode support for reduced eye strain
"""

import streamlit as st

# ADHD-friendly color palette - Light mode
COLORS_LIGHT = {
    # Primary colors - calming but engaging
    "primary": "#5B8FB9",  # Soft blue - focus and calm
    "primary_light": "#8FB8DE",
    "primary_dark": "#3D6B8C",
    # Secondary accent - warm and motivating
    "accent": "#F4A261",  # Soft orange - energy without anxiety
    "accent_light": "#F7C59F",
    "accent_dark": "#E76F51",
    # Backgrounds - warm neutrals, easier on eyes than pure white
    "bg_main": "#FAF7F2",  # Warm cream
    "bg_card": "#FFFFFF",
    "bg_sidebar": "#F5F0E8",
    # Text - softer than pure black
    "text_primary": "#2C3E50",
    "text_secondary": "#5D6D7E",
    "text_muted": "#95A5A6",
    # Priority colors - distinguishable but not harsh
    "priority_urgent": "#E07A5F",  # Coral red
    "priority_high": "#F4A261",  # Soft orange
    "priority_medium": "#F2CC8F",  # Soft yellow
    "priority_low": "#81B29A",  # Sage green
}

# ADHD-friendly color palette - Dark mode
COLORS_DARK = {
    # Primary colors - calming but visible on dark
    "primary": "#7FB3D5",  # Lighter soft blue
    "primary_light": "#A8CCE5",
    "primary_dark": "#5B8FB9",
    # Secondary accent - warm and motivating
    "accent": "#F4A261",  # Soft orange works in both modes
    "accent_light": "#F7C59F",
    "accent_dark": "#E76F51",
    # Backgrounds - dark but not pure black (easier on eyes)
    "bg_main": "#1E1E2E",  # Soft dark blue-gray
    "bg_card": "#2A2A3C",  # Slightly lighter for cards
    "bg_sidebar": "#252536",
    # Text - softer than pure white
    "text_primary": "#E8E8EC",
    "text_secondary": "#B8B8C4",
    "text_muted": "#7A7A8C",
    # Priority colors - slightly brighter for dark mode visibility
    "priority_urgent": "#F28B7D",  # Lighter coral
    "priority_high": "#F7B87A",  # Lighter orange
    "priority_medium": "#F5D89A",  # Lighter yellow
    "priority_low": "#8FD4A8",  # Lighter sage
}

# Default to light mode colors for backwards compatibility
COLORS = COLORS_LIGHT

# CSS for ADHD-friendly styling with dark mode support
ADHD_CSS = """
<style>
    /* ============================================
       LIGHT MODE (default)
       ============================================ */

    /* Main background - warm cream instead of stark white */
    .stApp {
        background-color: #FAF7F2;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F5F0E8;
    }

    /* Headers - softer color */
    h1, h2, h3 {
        color: #2C3E50 !important;
    }

    /* Reduce visual noise from borders */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E5E0D8;
    }

    /* Focus states - clear but not jarring */
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: #5B8FB9;
        box-shadow: 0 0 0 2px rgba(91, 143, 185, 0.2);
    }

    /* Button styling - larger click targets */
    .stButton > button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #5B8FB9;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #4A7A9E;
    }

    /* Cards and containers - subtle shadows */
    .element-container {
        border-radius: 8px;
    }

    /* Metrics - cleaner look */
    [data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Checkboxes - larger for easier clicking */
    .stCheckbox > label {
        font-size: 1rem;
    }

    /* Form styling */
    .stForm {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* Success/Error messages - softer colors */
    .stSuccess {
        background-color: rgba(82, 183, 136, 0.1);
        border-left: 4px solid #52B788;
    }

    .stError {
        background-color: rgba(224, 122, 95, 0.1);
        border-left: 4px solid #E07A5F;
    }

    .stWarning {
        background-color: rgba(244, 162, 97, 0.1);
        border-left: 4px solid #F4A261;
    }

    .stInfo {
        background-color: rgba(127, 179, 213, 0.1);
        border-left: 4px solid #7FB3D5;
    }

    /* Dividers - subtle */
    hr {
        border: none;
        border-top: 1px solid #E5E0D8;
        margin: 1.5rem 0;
    }

    /* Scrollbar styling - less distracting */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F5F0E8;
    }

    ::-webkit-scrollbar-thumb {
        background: #C5BEB3;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #A59E93;
    }

    /* Task card styling */
    .task-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid transparent;
        transition: all 0.2s ease;
    }

    .task-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }

    .task-card.priority-urgent {
        border-left-color: #E07A5F;
    }

    .task-card.priority-high {
        border-left-color: #F4A261;
    }

    .task-card.priority-medium {
        border-left-color: #F2CC8F;
    }

    .task-card.priority-low {
        border-left-color: #81B29A;
    }

    /* Dialog/Modal styling */
    [data-testid="stModal"] {
        background-color: white;
        border-radius: 16px;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F5F0E8;
        border-radius: 8px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }

    /* Caption text - better readability */
    .stCaption {
        color: #5D6D7E;
    }

    /* ============================================
       DARK MODE - Uses system preference
       ============================================ */
    @media (prefers-color-scheme: dark) {
        /* Main background - soft dark, not pure black */
        .stApp {
            background-color: #1E1E2E !important;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #252536 !important;
        }

        section[data-testid="stSidebar"] > div {
            background-color: #252536 !important;
        }

        /* Headers - light color for dark bg */
        h1, h2, h3 {
            color: #E8E8EC !important;
        }

        /* Regular text */
        p, span, label, .stMarkdown {
            color: #E8E8EC !important;
        }

        /* Muted/secondary text */
        .stCaption, small {
            color: #B8B8C4 !important;
        }

        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #2A2A3C !important;
            border: 1px solid #3D3D52 !important;
            color: #E8E8EC !important;
            border-radius: 8px;
        }

        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: #7A7A8C !important;
        }

        /* Focus states */
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within,
        .stTextArea > div > div > textarea:focus {
            border-color: #7FB3D5 !important;
            box-shadow: 0 0 0 2px rgba(127, 179, 213, 0.3) !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #3D3D52 !important;
            color: #E8E8EC !important;
            border: 1px solid #4D4D66 !important;
        }

        .stButton > button:hover {
            background-color: #4D4D66 !important;
            border-color: #5D5D76 !important;
        }

        .stButton > button[kind="primary"] {
            background-color: #5B8FB9 !important;
            border: none !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #4A7A9E !important;
        }

        /* Metrics */
        [data-testid="metric-container"] {
            background-color: #2A2A3C !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        [data-testid="metric-container"] label {
            color: #B8B8C4 !important;
        }

        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #E8E8EC !important;
        }

        /* Form styling */
        .stForm {
            background-color: #2A2A3C !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        }

        /* Success/Error messages */
        .stSuccess {
            background-color: rgba(82, 183, 136, 0.15) !important;
        }

        .stError {
            background-color: rgba(224, 122, 95, 0.15) !important;
        }

        .stWarning {
            background-color: rgba(244, 162, 97, 0.15) !important;
        }

        .stInfo {
            background-color: rgba(127, 179, 213, 0.15) !important;
        }

        /* Dividers */
        hr {
            border-top: 1px solid #3D3D52 !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar-track {
            background: #252536 !important;
        }

        ::-webkit-scrollbar-thumb {
            background: #4D4D66 !important;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #5D5D76 !important;
        }

        /* Task cards */
        .task-card {
            background: #2A2A3C !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        .task-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        }

        /* Brighter priority colors for dark mode */
        .task-card.priority-urgent {
            border-left-color: #F28B7D !important;
        }

        .task-card.priority-high {
            border-left-color: #F7B87A !important;
        }

        .task-card.priority-medium {
            border-left-color: #F5D89A !important;
        }

        .task-card.priority-low {
            border-left-color: #8FD4A8 !important;
        }

        /* Dialog/Modal */
        [data-testid="stModal"] {
            background-color: #2A2A3C !important;
        }

        [data-testid="stModal"] > div {
            background-color: #2A2A3C !important;
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: #2A2A3C !important;
            color: #E8E8EC !important;
        }

        /* Selectbox dropdown */
        [data-baseweb="select"] > div {
            background-color: #2A2A3C !important;
        }

        [data-baseweb="menu"] {
            background-color: #2A2A3C !important;
        }

        [data-baseweb="menu"] li {
            color: #E8E8EC !important;
        }

        [data-baseweb="menu"] li:hover {
            background-color: #3D3D52 !important;
        }

        /* Checkbox */
        .stCheckbox label span {
            color: #E8E8EC !important;
        }

        /* Date input */
        [data-testid="stDateInput"] > div > div > input {
            background-color: #2A2A3C !important;
            color: #E8E8EC !important;
            border: 1px solid #3D3D52 !important;
        }

        /* Number input */
        [data-testid="stNumberInput"] button {
            background-color: #3D3D52 !important;
            color: #E8E8EC !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #B8B8C4 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #3D3D52 !important;
            color: #E8E8EC !important;
        }

        /* Chat input */
        [data-testid="stChatInput"] > div {
            background-color: #2A2A3C !important;
            border-color: #3D3D52 !important;
        }

        [data-testid="stChatInput"] textarea {
            color: #E8E8EC !important;
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background-color: #2A2A3C !important;
        }

        /* Info box */
        .stAlert {
            background-color: #2A2A3C !important;
        }
    }
</style>
"""


def apply_adhd_theme():
    """Apply ADHD-friendly theme to the Streamlit app."""
    st.markdown(ADHD_CSS, unsafe_allow_html=True)


def get_priority_color(priority: str) -> str:
    """Get ADHD-friendly color for a priority level."""
    priority_map = {
        "urgent": COLORS["priority_urgent"],
        "high": COLORS["priority_high"],
        "medium": COLORS["priority_medium"],
        "low": COLORS["priority_low"],
    }
    return priority_map.get(priority.lower(), COLORS["priority_medium"])


def get_energy_color(energy: str) -> str:
    """Get ADHD-friendly color for an energy level."""
    energy_map = {
        "high": COLORS["energy_high"],
        "medium": COLORS["energy_medium"],
        "low": COLORS["energy_low"],
    }
    return energy_map.get(energy.lower(), COLORS["energy_medium"])


def get_status_color(status: str) -> str:
    """Get ADHD-friendly color for a task status."""
    status_map = {
        "not_started": COLORS["status_not_started"],
        "in_progress": COLORS["status_in_progress"],
        "completed": COLORS["status_completed"],
        "blocked": COLORS["status_blocked"],
    }
    return status_map.get(status.lower(), COLORS["status_not_started"])


def priority_badge(priority: str) -> str:
    """Return HTML for a styled priority badge."""
    color = get_priority_color(priority)
    return f"""
    <span style="
        background-color: {color}20;
        color: {color};
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    ">{priority.upper()}</span>
    """


def status_badge(status: str) -> str:
    """Return HTML for a styled status badge."""
    color = get_status_color(status)
    display_status = status.replace("_", " ").title()
    return f"""
    <span style="
        background-color: {color}20;
        color: {color};
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    ">{display_status}</span>
    """
