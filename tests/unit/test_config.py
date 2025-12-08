"""Test configuration management."""

from adhd_planner.utils.config import Settings, get_settings


def test_settings_load_from_env(mock_settings):
    """Test that settings load from environment."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.database_path.endswith("test.db")


def test_settings_defaults():
    """Test default values."""
    settings = Settings()
    assert settings.llm_provider == "ollama"
    assert settings.max_focus_duration == 45
    assert settings.sync_enabled is True


def test_logger_setup():
    """Test logger configuration."""
    from adhd_planner.utils.logger import get_logger, setup_logging

    logger = setup_logging("test")
    assert logger.name == "test"

    module_logger = get_logger("test_module")
    assert "adhd_planner.test_module" in module_logger.name
