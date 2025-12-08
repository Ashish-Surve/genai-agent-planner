"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # LLM Configuration
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-pro"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Database Configuration
    database_path: str = "data/database/adhd_planner.db"

    # Sync Configuration
    sync_enabled: bool = True
    sync_interval_minutes: int = 5
    default_sync_to_reminders: bool = True
    default_sync_to_calendar: bool = True

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "data/logs/app.log"

    # Streamlit Configuration
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "localhost"
    streamlit_theme_base: str = "light"

    # ADHD Settings
    max_focus_duration: int = 45
    buffer_time_between_tasks: int = 10
    context_switch_penalty: int = 5
    work_start_time: str = "09:00"
    work_end_time: str = "17:00"
    default_break_duration: int = 15

    # Development
    environment: str = "development"
    debug: bool = False


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
