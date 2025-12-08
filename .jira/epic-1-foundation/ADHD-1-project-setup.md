# ADHD-1: Project Setup & Configuration

## Story Information

- **Epic**: Foundation
- **Story Points**: 2
- **Estimated Time**: 2 hours
- **Prerequisites**: None (first story!)
- **Status**: 📋 Not Started

## Description

Set up the basic project structure, create essential configuration files, and ensure the development environment is ready. This is the foundation that all other stories will build upon.

## Goals

1. Create the complete directory structure
2. Set up configuration management
3. Create environment file templates
4. Set up logging infrastructure
5. Create initial test structure

## Acceptance Criteria

- [ ] All source directories exist as per architecture
- [ ] Configuration can be loaded from `.env` file
- [ ] Logging is configured and working
- [ ] Can import from `src` package
- [ ] Basic test infrastructure is set up
- [ ] Development dependencies installed with `uv sync --extra dev`

## Files to Create

### Configuration Files
```
src/utils/config.py          # Configuration management
src/utils/logger.py           # Logging setup
```

### Core Structure
```
src/__init__.py
src/agents/__init__.py
src/graph/__init__.py
src/models/__init__.py
src/services/__init__.py
src/repositories/__init__.py
src/integrations/__init__.py
src/integrations/apple/__init__.py
src/integrations/llm/__init__.py
src/ui/__init__.py
src/ui/pages/__init__.py
src/ui/components/__init__.py
src/database/__init__.py
src/utils/__init__.py
src/core/__init__.py
```

### Test Structure
```
tests/__init__.py
tests/conftest.py
tests/unit/__init__.py
tests/integration/__init__.py
```

### Data Directories
```
data/database/.gitkeep
data/config/.gitkeep
data/logs/.gitkeep
scripts/.gitkeep
```

## Implementation Steps

### Step 1: Create Directory Structure (15 min)

```bash
# Create all source directories
mkdir -p src/{agents,graph,models,services,repositories,integrations/{apple,llm},ui/{pages,components,styles},database,utils,core}

# Create test directories
mkdir -p tests/{unit,integration,fixtures}

# Create data directories
mkdir -p data/{database,config,logs}

# Create scripts directory
mkdir -p scripts
```

### Step 2: Create __init__.py Files (10 min)

Create empty `__init__.py` files in all directories to make them Python packages.

```bash
# Use find and touch to create all __init__.py files
find src tests -type d -exec touch {}/__init__.py \;
```

### Step 3: Implement Configuration Manager (30 min)

**File**: `src/utils/config.py`

```python
"""Configuration management using pydantic-settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Configuration
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"
    anthropic_api_key: Optional[str] = None
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
_settings: Optional[Settings] = None


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
```

### Step 4: Implement Logging (30 min)

**File**: `src/utils/logger.py`

```python
"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path
from typing import Optional

from src.utils.config import get_settings


def setup_logging(
    name: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging with file and console handlers.

    Args:
        name: Logger name (defaults to root logger)
        level: Log level (defaults to config value)

    Returns:
        Configured logger instance
    """
    settings = get_settings()

    # Get or create logger
    logger = logging.getLogger(name)

    # Set level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter(
        fmt="%(levelname)s: %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if settings.log_file:
        log_file = Path(settings.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger
logger = setup_logging("adhd_planner")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"adhd_planner.{name}")
```

### Step 5: Create pytest Configuration (20 min)

**File**: `tests/conftest.py`

```python
"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def test_data_dir(tmp_path):
    """Create temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "database").mkdir()
    (data_dir / "config").mkdir()
    (data_dir / "logs").mkdir()
    return data_dir


@pytest.fixture
def mock_settings(monkeypatch, test_data_dir):
    """Mock settings for testing."""
    monkeypatch.setenv("DATABASE_PATH", str(test_data_dir / "database" / "test.db"))
    monkeypatch.setenv("LOG_FILE", str(test_data_dir / "logs" / "test.log"))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    from src.utils.config import reload_settings
    return reload_settings()
```

### Step 6: Create .gitkeep Files (5 min)

```bash
# Create .gitkeep files to preserve empty directories
touch data/database/.gitkeep
touch data/config/.gitkeep
touch data/logs/.gitkeep
touch scripts/.gitkeep
```

### Step 7: Verify Setup (10 min)

**File**: `tests/unit/test_config.py`

```python
"""Test configuration management."""

import pytest
from src.utils.config import get_settings, Settings


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
    from src.utils.logger import setup_logging, get_logger

    logger = setup_logging("test")
    assert logger.name == "test"

    module_logger = get_logger("test_module")
    assert "adhd_planner.test_module" in module_logger.name
```

## Testing Checklist

Run these commands to verify everything works:

```bash
# 1. Install dependencies
uv sync --extra dev

# 2. Verify directory structure
ls -R src/

# 3. Verify imports work
uv run python -c "from src.utils.config import get_settings; print(get_settings())"

# 4. Verify logging works
uv run python -c "from src.utils.logger import logger; logger.info('Test message')"

# 5. Run tests
uv run pytest tests/unit/test_config.py -v

# 6. Check code quality
uv run ruff check src/
uv run black --check src/
```

## Expected Output

All tests should pass:
```
tests/unit/test_config.py::test_settings_load_from_env PASSED
tests/unit/test_config.py::test_settings_defaults PASSED
tests/unit/test_config.py::test_logger_setup PASSED
```

Logging should work:
```
INFO: Test message
```

## Success Criteria

- ✅ All directories created
- ✅ Configuration loads from .env
- ✅ Logging writes to file and console
- ✅ All tests pass
- ✅ No import errors
- ✅ Ruff and black pass

## Common Issues & Solutions

### Issue: ImportError when running tests
**Solution**: Make sure you run tests with `uv run pytest`, not just `pytest`

### Issue: Settings not loading from .env
**Solution**: Make sure `.env` file exists and has correct format (KEY=value, no quotes)

### Issue: Log file not created
**Solution**: Check that `data/logs/` directory exists

## Next Story

Once this story is complete, move to:
**[ADHD-2: Database Schema & Migrations](.jira/epic-1-foundation/ADHD-2-database-schema.md)**

## Notes

- This story sets up the skeleton - no business logic yet
- Focus on clean structure and working imports
- All configuration is environment-based for flexibility
- Logging is essential for debugging - set it up properly now!
