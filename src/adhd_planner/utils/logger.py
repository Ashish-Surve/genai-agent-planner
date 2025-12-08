"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path

from adhd_planner.utils.config import get_settings


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
