"""
Integration tests for Streamlit Settings Page.
Tests settings management, persistence, and configuration.

Note: LLM settings (provider, model, API keys) are loaded from .env file
and are read-only at runtime. User preferences are stored in JSON file.
"""

import json
import tempfile
from datetime import time
from pathlib import Path

import pytest

from adhd_planner.core.settings_manager import SettingsManager


@pytest.fixture
def temp_settings_file():
    """Create a temporary settings file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{}")
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def settings_manager(temp_settings_file):
    """Create a settings manager with temporary file."""
    return SettingsManager(settings_path=Path(temp_settings_file))


class TestSettingsInitialization:
    """Test settings initialization."""

    def test_settings_manager_creation(self, settings_manager):
        """Test creating a settings manager."""
        assert settings_manager is not None

    def test_load_default_settings(self, settings_manager):
        """Test loading default settings."""
        defaults = settings_manager.get_all()
        assert defaults is not None
        assert isinstance(defaults, dict)

    def test_settings_file_creation(self, temp_settings_file):
        """Test settings manager works with temp file."""
        SettingsManager(settings_path=Path(temp_settings_file))
        assert Path(temp_settings_file).exists()


class TestSettingsLLMConfiguration:
    """Test LLM provider configuration.

    Note: LLM settings are loaded from .env and are read-only.
    The set() method will log a warning and not change the value.
    """

    def test_llm_provider_is_read_only(self, settings_manager):
        """Test that LLM provider cannot be changed at runtime."""
        original_provider = settings_manager.get("llm_provider")

        # Try to set a different provider
        settings_manager.set("llm_provider", "some_other_provider")

        # Should still have original value (from .env)
        assert settings_manager.get("llm_provider") == original_provider

    def test_llm_model_is_read_only(self, settings_manager):
        """Test that LLM model cannot be changed at runtime."""
        original_model = settings_manager.get("llm_model")

        # Try to set a different model
        settings_manager.set("llm_model", "some_other_model")

        # Should still have original value (from .env)
        assert settings_manager.get("llm_model") == original_model

    def test_api_keys_are_read_only(self, settings_manager):
        """Test that API keys cannot be changed at runtime."""
        original_gemini_key = settings_manager.get("gemini_api_key")
        original_anthropic_key = settings_manager.get("anthropic_api_key")

        # Try to set API keys
        settings_manager.set("gemini_api_key", "new-gemini-key")
        settings_manager.set("anthropic_api_key", "new-anthropic-key")

        # Should still have original values
        assert settings_manager.get("gemini_api_key") == original_gemini_key
        assert settings_manager.get("anthropic_api_key") == original_anthropic_key

    def test_llm_settings_from_env(self, settings_manager):
        """Test that LLM settings are loaded from environment."""
        # These should have values from .env (or defaults from config.py)
        provider = settings_manager.get("llm_provider")
        model = settings_manager.get("llm_model")

        assert provider is not None
        assert model is not None
        # Default provider in config.py is "ollama"
        assert provider in ["ollama", "gemini", "anthropic", "claude"]

    def test_env_settings_keys_defined(self, settings_manager):
        """Test that ENV_SETTINGS_KEYS are properly defined."""
        assert "llm_provider" in SettingsManager.ENV_SETTINGS_KEYS
        assert "llm_model" in SettingsManager.ENV_SETTINGS_KEYS
        assert "gemini_api_key" in SettingsManager.ENV_SETTINGS_KEYS
        assert "anthropic_api_key" in SettingsManager.ENV_SETTINGS_KEYS


class TestSettingsWorkingHours:
    """Test working hours configuration."""

    def test_set_working_hours_start(self, settings_manager):
        """Test setting working hours start time."""
        settings_manager.set("work_start_hour", 9)
        settings_manager.set("work_start_minute", 0)
        assert settings_manager.get("work_start_hour") == 9
        assert settings_manager.get("work_start_minute") == 0

    def test_set_working_hours_end(self, settings_manager):
        """Test setting working hours end time."""
        settings_manager.set("work_end_hour", 17)
        settings_manager.set("work_end_minute", 30)
        assert settings_manager.get("work_end_hour") == 17
        assert settings_manager.get("work_end_minute") == 30

    def test_get_work_start_time(self, settings_manager):
        """Test getting work start time as time object."""
        settings_manager.set("work_start_hour", 9)
        settings_manager.set("work_start_minute", 30)
        start = settings_manager.get_work_start()
        assert isinstance(start, time)
        assert start.hour == 9
        assert start.minute == 30

    def test_get_work_end_time(self, settings_manager):
        """Test getting work end time as time object."""
        settings_manager.set("work_end_hour", 17)
        settings_manager.set("work_end_minute", 45)
        end = settings_manager.get_work_end()
        assert isinstance(end, time)
        assert end.hour == 17
        assert end.minute == 45

    def test_set_work_days(self, settings_manager):
        """Test setting working days."""
        work_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        settings_manager.set("work_days", work_days)
        retrieved = settings_manager.get("work_days")
        assert retrieved == work_days


class TestSettingsEnergyLevels:
    """Test energy level configuration."""

    def test_set_morning_energy(self, settings_manager):
        """Test setting morning energy level."""
        energy = "high"
        settings_manager.set("morning_energy", energy)
        retrieved = settings_manager.get("morning_energy")
        assert retrieved == energy

    def test_set_afternoon_energy(self, settings_manager):
        """Test setting afternoon energy level."""
        energy = "medium"
        settings_manager.set("afternoon_energy", energy)
        retrieved = settings_manager.get("afternoon_energy")
        assert retrieved == energy

    def test_set_evening_energy(self, settings_manager):
        """Test setting evening energy level."""
        energy = "low"
        settings_manager.set("evening_energy", energy)
        retrieved = settings_manager.get("evening_energy")
        assert retrieved == energy

    def test_set_unknown_energy_level(self, settings_manager):
        """Test setting unknown energy level (no validation)."""
        # SettingsManager doesn't validate, just stores
        settings_manager.set("morning_energy", "unknown_level")
        energy = settings_manager.get("morning_energy")
        assert energy == "unknown_level"


class TestSettingsAppleSync:
    """Test Apple sync settings."""

    def test_enable_apple_sync(self, settings_manager):
        """Test enabling Apple sync."""
        settings_manager.set("sync_enabled", True)
        enabled = settings_manager.get("sync_enabled")
        assert enabled is True

    def test_disable_apple_sync(self, settings_manager):
        """Test disabling Apple sync."""
        settings_manager.set("sync_enabled", False)
        enabled = settings_manager.get("sync_enabled")
        assert enabled is False

    def test_sync_reminders(self, settings_manager):
        """Test sync reminders setting."""
        settings_manager.set("sync_reminders", True)
        sync_reminders = settings_manager.get("sync_reminders")
        assert sync_reminders is True

    def test_sync_calendar(self, settings_manager):
        """Test sync calendar setting."""
        settings_manager.set("sync_calendar", True)
        sync_calendar = settings_manager.get("sync_calendar")
        assert sync_calendar is True


class TestSettingsDisplay:
    """Test display and UI settings."""

    def test_set_theme(self, settings_manager):
        """Test setting color theme."""
        settings_manager.set("theme", "dark")
        theme = settings_manager.get("theme")
        assert theme == "dark"

    def test_set_show_energy_indicators(self, settings_manager):
        """Test show energy indicators setting."""
        settings_manager.set("show_energy_indicators", True)
        show = settings_manager.get("show_energy_indicators")
        assert show is True


class TestSettingsPersistence:
    """Test settings persistence to file."""

    def test_settings_persist_to_file(self, settings_manager):
        """Test that user settings are persisted to file."""
        # Set user preference (not LLM settings)
        settings_manager.set("theme", "dark")
        settings_manager.set("work_start_hour", 8)
        result = settings_manager.save()
        assert result is True

        # Create new manager with same file
        new_manager = SettingsManager(settings_path=settings_manager.settings_path)

        # User preferences should be persisted
        assert new_manager.get("theme") == "dark"
        assert new_manager.get("work_start_hour") == 8

    def test_settings_survive_reload(self, settings_manager):
        """Test settings survive reload from file."""
        settings_manager.set("morning_energy", "low")
        settings_manager.set("theme", "dark")
        settings_manager.save()

        # Reload settings
        settings_manager.reload()

        assert settings_manager.get("morning_energy") == "low"
        assert settings_manager.get("theme") == "dark"

    def test_save_returns_true_on_success(self, settings_manager):
        """Test save returns True on success."""
        result = settings_manager.save()
        assert result is True


class TestSettingsReset:
    """Test resetting settings."""

    def test_reset_to_defaults(self, settings_manager):
        """Test resetting all user settings to defaults."""
        # Change some user settings
        settings_manager.set("theme", "dark")
        settings_manager.set("morning_energy", "low")

        # Reset to defaults
        settings_manager.reset_to_defaults()

        # Should return default values for user settings
        assert settings_manager.get("theme") == SettingsManager.DEFAULT_USER_SETTINGS["theme"]
        assert (
            settings_manager.get("morning_energy")
            == SettingsManager.DEFAULT_USER_SETTINGS["morning_energy"]
        )

    def test_reset_single_setting(self, settings_manager):
        """Test resetting a single setting."""
        settings_manager.set("theme", "dark")
        settings_manager.reset_to_default("theme")

        # Should have default value
        theme = settings_manager.get("theme")
        assert theme == SettingsManager.DEFAULT_USER_SETTINGS["theme"]


class TestSettingsValidation:
    """Test settings validation."""

    def test_validate_always_returns_true(self, settings_manager):
        """Test that validate always returns True (no validation rules)."""
        # Current implementation always returns True
        valid = settings_manager.validate()
        assert valid is True


class TestSettingsBulkUpdate:
    """Test bulk settings updates."""

    def test_update_multiple_settings(self, settings_manager):
        """Test updating multiple user settings at once."""
        updates = {
            "theme": "dark",
            "work_start_hour": 8,
            "morning_energy": "low",
        }

        settings_manager.update(updates)

        assert settings_manager.get("theme") == "dark"
        assert settings_manager.get("work_start_hour") == 8
        assert settings_manager.get("morning_energy") == "low"

    def test_bulk_update_preserves_other_settings(self, settings_manager):
        """Test bulk update preserves other settings."""
        settings_manager.set("work_end_hour", 18)

        updates = {
            "theme": "dark",
        }

        settings_manager.update(updates)

        # Original setting should still be there
        assert settings_manager.get("work_end_hour") == 18
        assert settings_manager.get("theme") == "dark"

    def test_bulk_update_ignores_llm_settings(self, settings_manager):
        """Test that bulk update ignores LLM settings."""
        original_provider = settings_manager.get("llm_provider")

        updates = {
            "llm_provider": "some_other_provider",
            "theme": "dark",
        }

        settings_manager.update(updates)

        # LLM provider should not change
        assert settings_manager.get("llm_provider") == original_provider
        # User setting should change
        assert settings_manager.get("theme") == "dark"


class TestSettingsImportExport:
    """Test importing and exporting settings."""

    def test_export_settings(self, settings_manager):
        """Test exporting user settings to dict."""
        settings_manager.set("theme", "dark")
        settings_manager.set("morning_energy", "high")

        exported = settings_manager.export_settings()
        assert "theme" in exported
        assert "morning_energy" in exported
        assert exported["theme"] == "dark"
        assert exported["morning_energy"] == "high"

    def test_import_settings(self, settings_manager):
        """Test importing user settings from dict."""
        import_data = {
            "theme": "light",
            "work_start_hour": 7,
        }

        settings_manager.import_settings(import_data)

        assert settings_manager.get("theme") == "light"
        assert settings_manager.get("work_start_hour") == 7

    def test_import_ignores_llm_settings(self, settings_manager):
        """Test that import ignores LLM settings."""
        original_provider = settings_manager.get("llm_provider")

        import_data = {
            "llm_provider": "some_other_provider",
            "theme": "dark",
        }

        settings_manager.import_settings(import_data)

        # LLM provider should not change
        assert settings_manager.get("llm_provider") == original_provider
        # User setting should change
        assert settings_manager.get("theme") == "dark"

    def test_export_import_roundtrip(self, settings_manager):
        """Test export and reimport roundtrip for user settings."""
        settings_manager.set("theme", "dark")
        settings_manager.set("morning_energy", "high")

        exported = settings_manager.export_settings()

        # Reset
        settings_manager.reset_to_defaults()

        # Re-import
        settings_manager.import_settings(exported)

        assert settings_manager.get("theme") == "dark"
        assert settings_manager.get("morning_energy") == "high"


class TestSettingsIntegration:
    """Integration tests for settings workflows."""

    def test_complete_settings_configuration(self, settings_manager):
        """Test complete user settings configuration workflow."""
        # Configure working hours
        settings_manager.set("work_start_hour", 9)
        settings_manager.set("work_end_hour", 17)

        # Configure energy levels
        settings_manager.set("morning_energy", "high")
        settings_manager.set("afternoon_energy", "medium")

        # Configure display
        settings_manager.set("theme", "dark")

        # Save and verify
        result = settings_manager.save()
        assert result is True

        all_settings = settings_manager.get_all_settings()
        assert all_settings is not None

    def test_settings_file_merge_with_defaults(self, temp_settings_file):
        """Test that loaded settings merge with defaults."""
        # Write partial settings (user preferences only)
        partial_data = {
            "theme": "dark",
            "morning_energy": "low",
        }

        with open(temp_settings_file, "w") as f:
            json.dump(partial_data, f)

        # Load with new manager
        manager = SettingsManager(settings_path=Path(temp_settings_file))

        # Should have both custom and default values
        assert manager.get("theme") == "dark"
        assert manager.get("morning_energy") == "low"
        # Should have defaults for unspecified keys
        assert (
            manager.get("afternoon_energy")
            == SettingsManager.DEFAULT_USER_SETTINGS["afternoon_energy"]
        )

    def test_user_presets(self, settings_manager):
        """Test saving and loading user presets."""
        # Create a preset
        preset_data = {
            "theme": "dark",
            "work_start_hour": 9,
            "morning_energy": "high",
        }

        # Save as preset
        settings_manager.save_preset("dark_mode_preset", preset_data)

        # Load preset
        loaded = settings_manager.load_preset("dark_mode_preset")
        assert loaded is not None
        assert loaded["theme"] == "dark"

    def test_preset_does_not_exist(self, settings_manager):
        """Test loading non-existent preset."""
        loaded = settings_manager.load_preset("nonexistent_preset")
        assert loaded is None


class TestSettingsErrorHandling:
    """Test error handling in settings."""

    def test_get_nonexistent_setting(self, settings_manager):
        """Test getting a setting that doesn't exist."""
        # Should return None
        value = settings_manager.get("nonexistent_setting")
        assert value is None

    def test_get_with_default_value(self, settings_manager):
        """Test get with default value."""
        value = settings_manager.get("nonexistent_setting", "default_value")
        assert value == "default_value"

    def test_set_corrupted_file(self):
        """Test handling corrupted settings file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ corrupted json }")
            temp_path = f.name

        try:
            # Should handle gracefully and use defaults
            manager = SettingsManager(settings_path=Path(temp_path))
            assert manager is not None
            # Should have defaults loaded for user settings
            assert manager.get("theme") == SettingsManager.DEFAULT_USER_SETTINGS["theme"]
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestSettingsDefaultValues:
    """Test default settings values."""

    def test_default_llm_provider_from_env(self, settings_manager):
        """Test default LLM provider comes from .env."""
        provider = settings_manager.get("llm_provider")
        # Should have a value (from .env or config.py defaults)
        assert provider is not None
        assert isinstance(provider, str)

    def test_default_working_hours(self, settings_manager):
        """Test default working hours."""
        start_hour = settings_manager.get("work_start_hour")
        end_hour = settings_manager.get("work_end_hour")
        assert start_hour == SettingsManager.DEFAULT_USER_SETTINGS["work_start_hour"]
        assert end_hour == SettingsManager.DEFAULT_USER_SETTINGS["work_end_hour"]

    def test_default_energy_levels(self, settings_manager):
        """Test default energy levels."""
        morning = settings_manager.get("morning_energy")
        afternoon = settings_manager.get("afternoon_energy")
        evening = settings_manager.get("evening_energy")
        assert morning == SettingsManager.DEFAULT_USER_SETTINGS["morning_energy"]
        assert afternoon == SettingsManager.DEFAULT_USER_SETTINGS["afternoon_energy"]
        assert evening == SettingsManager.DEFAULT_USER_SETTINGS["evening_energy"]
