# ADHD-21: Settings Page

## Story Information
- **Epic**: Epic 4 - Streamlit UI
- **Story ID**: ADHD-21
- **Estimated Time**: 2 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-17: Streamlit App Structure
  - ✅ ADHD-6: Configuration & Logging

## Description

Implement the settings page where users can configure their preferences including LLM provider selection, working hours, energy patterns, and sync options.

**MVP Focus**: Basic settings form with essential options. No complex validation or real-time updates.

## Goals

1. Create settings form for user preferences
2. LLM provider selection and configuration
3. Working hours configuration
4. Basic energy pattern settings
5. Save/load settings from configuration

## Acceptance Criteria

### LLM Settings
- [ ] Provider selection (Ollama, Gemini, Claude)
- [ ] Model name input
- [ ] API key input (masked) for cloud providers
- [ ] Test connection button

### Working Hours
- [ ] Work start time picker
- [ ] Work end time picker
- [ ] Working days selection

### Energy Patterns
- [ ] Morning energy level selector
- [ ] Afternoon energy level selector
- [ ] Evening energy level selector

### Persistence
- [ ] Settings saved to configuration
- [ ] Settings loaded on page load
- [ ] Success/error feedback on save

## Files to Create/Modify

### Files to Modify
```
src/adhd_planner/ui/pages/4_⚙️_Settings.py    # Full implementation
```

### New Files
```
src/adhd_planner/core/
└── settings_manager.py         # Settings persistence

tests/unit/
└── test_settings_manager.py    # Settings tests
```

## Implementation Steps

### Step 1: Create Settings Manager (30 min)

Create `src/adhd_planner/core/settings_manager.py`:

```python
"""Settings management for user preferences."""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import time

from adhd_planner.utils.logger import get_logger
from adhd_planner.utils.config import get_settings

logger = get_logger(__name__)


class SettingsManager:
    """
    Manages user settings persistence.

    Settings are stored in a JSON file in the data directory.
    """

    DEFAULT_SETTINGS = {
        # LLM Settings
        "llm_provider": "ollama",
        "llm_model": "llama3.2",
        "gemini_api_key": "",
        "anthropic_api_key": "",

        # Working Hours
        "work_start_hour": 9,
        "work_start_minute": 0,
        "work_end_hour": 17,
        "work_end_minute": 0,
        "work_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],

        # Energy Patterns
        "morning_energy": "high",
        "afternoon_energy": "medium",
        "evening_energy": "low",

        # Sync Settings
        "sync_enabled": False,
        "sync_reminders": False,
        "sync_calendar": False,

        # Display Settings
        "theme": "light",
        "show_energy_indicators": True,
    }

    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialize settings manager.

        Args:
            settings_path: Optional path to settings file. Defaults to data/config/user_settings.json
        """
        if settings_path is None:
            app_settings = get_settings()
            settings_path = Path(app_settings.data_dir) / "config" / "user_settings.json"

        self.settings_path = settings_path
        self._settings: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load settings from file."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r") as f:
                    saved = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self._settings = {**self.DEFAULT_SETTINGS, **saved}
                    logger.info("Settings loaded successfully")
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
                self._settings = self.DEFAULT_SETTINGS.copy()
        else:
            self._settings = self.DEFAULT_SETTINGS.copy()
            logger.info("Using default settings")

    def save(self) -> bool:
        """
        Save settings to file.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, "w") as f:
                json.dump(self._settings, f, indent=2)
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()

    def update(self, settings: Dict[str, Any]) -> None:
        """Update multiple settings at once."""
        self._settings.update(settings)

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self.DEFAULT_SETTINGS.copy()

    def get_work_start(self) -> time:
        """Get work start time."""
        return time(
            self.get("work_start_hour", 9),
            self.get("work_start_minute", 0)
        )

    def get_work_end(self) -> time:
        """Get work end time."""
        return time(
            self.get("work_end_hour", 17),
            self.get("work_end_minute", 0)
        )
```

### Step 2: Implement Settings Page (1 hour)

Update `src/adhd_planner/ui/pages/4_⚙️_Settings.py`:

```python
"""Settings page - user preferences and configuration."""

import streamlit as st
from datetime import time

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.core.settings_manager import SettingsManager
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Settings - ADHD Planner", page_icon="⚙️", layout="wide")

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
            "anthropic": "Anthropic Claude"
        }.get(x, x)
    )

    model = st.text_input(
        "Model Name",
        value=settings.get("llm_model", "llama3.2"),
        help="Model name (e.g., llama3.2 for Ollama, gemini-pro for Gemini)"
    )

    api_key = ""
    if provider == "gemini":
        api_key = st.text_input(
            "Gemini API Key",
            value=settings.get("gemini_api_key", ""),
            type="password",
            help="Get your API key from Google AI Studio"
        )
    elif provider == "anthropic":
        api_key = st.text_input(
            "Anthropic API Key",
            value=settings.get("anthropic_api_key", ""),
            type="password",
            help="Get your API key from Anthropic Console"
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
        "anthropic_api_key": api_key if provider == "anthropic" else settings.get("anthropic_api_key", ""),
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
            format_func=lambda x: {"high": "🔥 High", "medium": "⚡ Medium", "low": "🌱 Low"}.get(x, x)
        )

    with col2:
        afternoon = st.selectbox(
            "☀️ Afternoon (12pm-6pm)",
            options=energy_options,
            index=energy_options.index(settings.get("afternoon_energy", "medium")),
            format_func=lambda x: {"high": "🔥 High", "medium": "⚡ Medium", "low": "🌱 Low"}.get(x, x)
        )

    with col3:
        evening = st.selectbox(
            "🌙 Evening (6pm-12am)",
            options=energy_options,
            index=energy_options.index(settings.get("evening_energy", "low")),
            format_func=lambda x: {"high": "🔥 High", "medium": "⚡ Medium", "low": "🌱 Low"}.get(x, x)
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
        help="Sync tasks with Apple Reminders and Calendar"
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
        help="Display energy level indicators on tasks and time blocks"
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
```

### Step 3: Update Core Init (5 min)

Update `src/adhd_planner/core/__init__.py`:

```python
"""Core business logic and session management."""

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.core.settings_manager import SettingsManager

__all__ = ["SessionManager", "SettingsManager"]
```

### Step 4: Create Tests (25 min)

Create `tests/unit/test_settings_manager.py`:

```python
"""Tests for SettingsManager."""

import pytest
import tempfile
from pathlib import Path
import json

from adhd_planner.core.settings_manager import SettingsManager


class TestSettingsManager:
    """Test SettingsManager functionality."""

    @pytest.fixture
    def temp_settings_path(self):
        """Create temporary settings file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "settings.json"

    def test_default_settings(self, temp_settings_path):
        """Test default settings are loaded when no file exists."""
        manager = SettingsManager(temp_settings_path)

        assert manager.get("llm_provider") == "ollama"
        assert manager.get("work_start_hour") == 9
        assert manager.get("morning_energy") == "high"

    def test_get_and_set(self, temp_settings_path):
        """Test getting and setting values."""
        manager = SettingsManager(temp_settings_path)

        manager.set("llm_provider", "gemini")
        assert manager.get("llm_provider") == "gemini"

        assert manager.get("nonexistent", "default") == "default"

    def test_save_and_load(self, temp_settings_path):
        """Test saving and loading settings."""
        manager = SettingsManager(temp_settings_path)

        manager.set("llm_provider", "anthropic")
        manager.set("work_start_hour", 10)
        manager.save()

        # Create new manager to load from file
        manager2 = SettingsManager(temp_settings_path)

        assert manager2.get("llm_provider") == "anthropic"
        assert manager2.get("work_start_hour") == 10

    def test_update_multiple(self, temp_settings_path):
        """Test updating multiple settings at once."""
        manager = SettingsManager(temp_settings_path)

        manager.update({
            "llm_provider": "gemini",
            "llm_model": "gemini-pro",
            "morning_energy": "low",
        })

        assert manager.get("llm_provider") == "gemini"
        assert manager.get("llm_model") == "gemini-pro"
        assert manager.get("morning_energy") == "low"

    def test_reset_to_defaults(self, temp_settings_path):
        """Test resetting to defaults."""
        manager = SettingsManager(temp_settings_path)

        manager.set("llm_provider", "anthropic")
        manager.reset_to_defaults()

        assert manager.get("llm_provider") == "ollama"

    def test_get_all(self, temp_settings_path):
        """Test getting all settings."""
        manager = SettingsManager(temp_settings_path)

        all_settings = manager.get_all()

        assert "llm_provider" in all_settings
        assert "work_start_hour" in all_settings
        assert "morning_energy" in all_settings

    def test_work_time_helpers(self, temp_settings_path):
        """Test work time helper methods."""
        manager = SettingsManager(temp_settings_path)

        manager.set("work_start_hour", 8)
        manager.set("work_start_minute", 30)
        manager.set("work_end_hour", 18)
        manager.set("work_end_minute", 0)

        start = manager.get_work_start()
        end = manager.get_work_end()

        assert start.hour == 8
        assert start.minute == 30
        assert end.hour == 18
        assert end.minute == 0

    def test_load_merges_with_defaults(self, temp_settings_path):
        """Test that loading merges with defaults for missing keys."""
        # Create file with partial settings
        temp_settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_settings_path, "w") as f:
            json.dump({"llm_provider": "gemini"}, f)

        manager = SettingsManager(temp_settings_path)

        # Should have saved value
        assert manager.get("llm_provider") == "gemini"
        # Should have default for missing keys
        assert manager.get("work_start_hour") == 9
```

## Testing Checklist

- [ ] Run `uv run streamlit run src/adhd_planner/ui/app.py`
- [ ] Navigate to Settings page
- [ ] All sections display correctly
- [ ] LLM provider dropdown works
- [ ] API key fields are masked
- [ ] Time pickers work
- [ ] Working days multi-select works
- [ ] Energy level selectors work
- [ ] Sync toggles work
- [ ] Save button shows success message
- [ ] Reset button resets all values
- [ ] Settings persist after page refresh
- [ ] Run `uv run pytest tests/unit/test_settings_manager.py -v`
- [ ] All tests pass

## Success Criteria

- [ ] Settings form displays all options
- [ ] Form values reflect saved settings
- [ ] Save persists settings to file
- [ ] Reset restores defaults
- [ ] API keys are properly masked
- [ ] Time inputs work correctly
- [ ] Tests pass

## Implementation Notes

### Settings Storage
Settings are stored as JSON in `data/config/user_settings.json`. This keeps them separate from environment variables which are for secrets/deployment config.

### API Key Handling
API keys use `type="password"` in Streamlit to mask input. They're stored in the settings file. For production, consider more secure storage.

### Settings Manager Pattern
The `SettingsManager` provides a single source of truth for user preferences that can be accessed from any part of the application.

### MVP Approach
- Basic form with essential settings
- No validation beyond required fields
- No real-time LLM connection testing (just mock success)
- No advanced themes or customization

## Next Story

After completing this story, you have completed Epic 4! Proceed to:
- **ADHD-22**: Apple Permissions & Setup - Begin Epic 5 (Apple Integration)
