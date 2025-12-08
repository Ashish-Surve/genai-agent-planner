"""Centralized logging configuration."""

import logging
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from adhd_planner.utils.config import get_settings

# Context storage
_log_context: ContextVar[dict[str, Any] | None] = ContextVar("log_context", default=None)


def setup_logging(name: str | None = None, level: str | None = None) -> logging.Logger:
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
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

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


def set_log_context(**kwargs: Any) -> None:
    """
    Set context values that will be included in all log messages.

    Args:
        **kwargs: Context key-value pairs
    """
    context = _log_context.get() or {}
    context = context.copy()
    context.update(kwargs)
    _log_context.set(context)


def clear_log_context() -> None:
    """Clear all log context."""
    _log_context.set(None)


def get_log_context() -> dict[str, Any]:
    """Get current log context."""
    context = _log_context.get()
    return context.copy() if context else {}


class ContextFormatter(logging.Formatter):
    """Formatter that includes context in log messages."""

    def format(self, record: logging.LogRecord) -> str:
        context = get_log_context()
        if context:
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            record.msg = f"[{context_str}] {record.msg}"
        return super().format(record)
