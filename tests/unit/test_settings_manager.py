"""Tests for SettingsManager."""

import json
import tempfile
from pathlib import Path

import pytest

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

        manager.update(
            {
                "llm_provider": "gemini",
                "llm_model": "gemini-pro",
                "morning_energy": "low",
            }
        )

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
