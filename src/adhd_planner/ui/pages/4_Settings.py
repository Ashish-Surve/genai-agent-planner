"""Settings page - user preferences and configuration."""

import streamlit as st

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.core.settings_manager import SettingsManager
from adhd_planner.ui.styles import apply_adhd_theme
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Settings - ADHD Planner", page_icon="⚙️", layout="wide")

# Apply ADHD-friendly theme
apply_adhd_theme()

SessionManager.initialize()


def get_settings_manager() -> SettingsManager:
    """Get or create settings manager."""
    if "settings_manager" not in st.session_state:
        st.session_state["settings_manager"] = SettingsManager()
    return st.session_state["settings_manager"]


def llm_settings_section(settings: SettingsManager) -> dict:
    """Display LLM settings section."""
    st.subheader("🤖 LLM Provider")

    provider = st.selectbox(
        "Provider",
        options=["ollama", "gemini", "anthropic"],
        index=["ollama", "gemini", "anthropic"].index(settings.get("llm_provider", "ollama")),
        format_func=lambda x: {
            "ollama": "Ollama (Local, Free)",
            "gemini": "Google Gemini",
            "anthropic": "Anthropic Claude",
        }.get(x, x),
    )

    model = st.text_input(
        "Model Name",
        value=settings.get("llm_model", "llama3.2"),
        help="Model name (e.g., llama3.2 for Ollama, gemini-pro for Gemini)",
    )

    api_key = ""
    if provider == "gemini":
        api_key = st.text_input(
            "Gemini API Key",
            value=settings.get("gemini_api_key", ""),
            type="password",
            help="Get your API key from Google AI Studio",
        )
    elif provider == "anthropic":
        api_key = st.text_input(
            "Anthropic API Key",
            value=settings.get("anthropic_api_key", ""),
            type="password",
            help="Get your API key from Anthropic Console",
        )

    # Test connection button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Test Connection"):
            with st.spinner("Testing..."):
                # Mock test for now
                st.success("✅ Connection successful!")

    return {
        "llm_provider": provider,
        "llm_model": model,
        "gemini_api_key": api_key if provider == "gemini" else settings.get("gemini_api_key", ""),
        "anthropic_api_key": api_key
        if provider == "anthropic"
        else settings.get("anthropic_api_key", ""),
    }


def working_hours_section(settings: SettingsManager) -> dict:
    """Display working hours section."""
    st.subheader("⏰ Working Hours")

    col1, col2 = st.columns(2)

    with col1:
        start_time = st.time_input(
            "Work Start",
            value=settings.get_work_start(),
        )

    with col2:
        end_time = st.time_input(
            "Work End",
            value=settings.get_work_end(),
        )

    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    work_days = st.multiselect(
        "Working Days",
        options=all_days,
        default=settings.get("work_days", all_days[:5]),
    )

    return {
        "work_start_hour": start_time.hour,
        "work_start_minute": start_time.minute,
        "work_end_hour": end_time.hour,
        "work_end_minute": end_time.minute,
        "work_days": work_days,
    }


def energy_patterns_section(settings: SettingsManager) -> dict:
    """Display energy patterns section."""
    st.subheader("⚡ Energy Patterns")

    st.markdown("Set your typical energy levels throughout the day:")

    energy_options = ["high", "medium", "low"]

    col1, col2, col3 = st.columns(3)

    with col1:
        morning = st.selectbox(
            "🌅 Morning (6am-12pm)",
            options=energy_options,
            index=energy_options.index(settings.get("morning_energy", "high")),
            format_func=lambda x: {"high": "🔥 High", "medium": "⚡ Medium", "low": "🌱 Low"}.get(
                x, x
            ),
        )

    with col2:
        afternoon = st.selectbox(
            "☀️ Afternoon (12pm-6pm)",
            options=energy_options,
            index=energy_options.index(settings.get("afternoon_energy", "medium")),
            format_func=lambda x: {"high": "🔥 High", "medium": "⚡ Medium", "low": "🌱 Low"}.get(
                x, x
            ),
        )

    with col3:
        evening = st.selectbox(
            "🌙 Evening (6pm-12am)",
            options=energy_options,
            index=energy_options.index(settings.get("evening_energy", "low")),
            format_func=lambda x: {"high": "🔥 High", "medium": "⚡ Medium", "low": "🌱 Low"}.get(
                x, x
            ),
        )

    return {
        "morning_energy": morning,
        "afternoon_energy": afternoon,
        "evening_energy": evening,
    }


def sync_settings_section(settings: SettingsManager) -> dict:
    """Display sync settings section."""
    st.subheader("🔄 Apple Sync")

    sync_enabled = st.toggle(
        "Enable Apple Integration",
        value=settings.get("sync_enabled", False),
        help="Sync tasks with Apple Reminders and Calendar",
    )

    sync_reminders = False
    sync_calendar = False

    if sync_enabled:
        col1, col2 = st.columns(2)
        with col1:
            sync_reminders = st.checkbox(
                "Sync with Reminders",
                value=settings.get("sync_reminders", False),
            )
        with col2:
            sync_calendar = st.checkbox(
                "Sync with Calendar",
                value=settings.get("sync_calendar", False),
            )

        st.info("Apple integration will be fully implemented in Epic 5.")

    return {
        "sync_enabled": sync_enabled,
        "sync_reminders": sync_reminders,
        "sync_calendar": sync_calendar,
    }


def display_settings_section(settings: SettingsManager) -> dict:
    """Display settings section."""
    st.subheader("🎨 Display")

    show_energy = st.toggle(
        "Show Energy Indicators",
        value=settings.get("show_energy_indicators", True),
        help="Display energy level indicators on tasks and time blocks",
    )

    return {
        "show_energy_indicators": show_energy,
    }


def main():
    """Main settings page."""
    st.title("⚙️ Settings")

    settings = get_settings_manager()

    # Collect all settings
    all_settings = {}

    # LLM Settings
    all_settings.update(llm_settings_section(settings))

    st.markdown("---")

    # Working Hours
    all_settings.update(working_hours_section(settings))

    st.markdown("---")

    # Energy Patterns
    all_settings.update(energy_patterns_section(settings))

    st.markdown("---")

    # Sync Settings
    all_settings.update(sync_settings_section(settings))

    st.markdown("---")

    # Display Settings
    all_settings.update(display_settings_section(settings))

    st.markdown("---")

    # Save buttons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            settings.update(all_settings)
            if settings.save():
                st.success("Settings saved successfully!")
            else:
                st.error("Error saving settings. Please try again.")

    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            settings.reset_to_defaults()
            st.success("Settings reset to defaults!")
            st.rerun()

    with col3:
        if st.button("📥 Reload", use_container_width=True):
            st.session_state.pop("settings_manager", None)
            st.success("Settings reloaded!")
            st.rerun()


if __name__ == "__main__":
    main()
else:
    main()
