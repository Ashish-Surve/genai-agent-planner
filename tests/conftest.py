"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest

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

    from adhd_planner.utils.config import reload_settings

    return reload_settings()
