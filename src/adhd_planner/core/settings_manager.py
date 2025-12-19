"""Settings management for user preferences."""

import json
from datetime import time
from pathlib import Path
from typing import Any

from adhd_planner.utils.config import get_settings
from adhd_planner.utils.logger import get_logger

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

    # Settings that are read-only (loaded from environment variables)
    READ_ONLY_SETTINGS = {"llm_provider", "llm_model", "gemini_api_key", "anthropic_api_key"}

    def __init__(self, settings_path: Path | None = None):
        """
        Initialize settings manager.

        Args:
            settings_path: Optional path to settings file. Defaults to data/config/user_settings.json
        """
        if settings_path is None:
            app_settings = get_settings()
            settings_path = Path(app_settings.data_dir) / "config" / "user_settings.json"

        self.settings_path = settings_path
        self._settings: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load settings from file."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path) as f:
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
        """
        Set a setting value.

        Read-only settings cannot be changed.
        """
        if key in self.READ_ONLY_SETTINGS:
            logger.warning(f"Cannot set read-only setting: {key}")
            return
        self._settings[key] = value

    def get_all(self) -> dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()

    def update(self, settings: dict[str, Any]) -> None:
        """
        Update multiple settings at once.

        Read-only settings are ignored during update.
        """
        filtered_settings = {k: v for k, v in settings.items() if k not in self.READ_ONLY_SETTINGS}
        self._settings.update(filtered_settings)

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self.DEFAULT_SETTINGS.copy()

    def get_work_start(self) -> time:
        """Get work start time."""
        return time(self.get("work_start_hour", 9), self.get("work_start_minute", 0))

    def get_work_end(self) -> time:
        """Get work end time."""
        return time(self.get("work_end_hour", 17), self.get("work_end_minute", 0))
