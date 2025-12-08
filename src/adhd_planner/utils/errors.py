"""Error formatting and user-friendly error messages."""

from typing import Any

from adhd_planner.utils.logger import get_logger

logger = get_logger("errors")


class UserFacingError(Exception):
    """Error with user-friendly message."""

    def __init__(
        self,
        user_message: str,
        technical_message: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        self.details = details or {}
        super().__init__(self.technical_message)


def format_error_for_user(error: Exception) -> str:
    """
    Format an error message for user display.

    Args:
        error: Exception to format

    Returns:
        User-friendly error message
    """
    if isinstance(error, UserFacingError):
        return error.user_message

    # Map common errors to user-friendly messages
    error_type = type(error).__name__
    error_str = str(error)

    if "database" in error_str.lower():
        return "Sorry, there was a problem saving your data. Please try again."

    if "connection" in error_str.lower() or "network" in error_str.lower():
        return "Connection issue detected. Please check your network and try again."

    if "permission" in error_str.lower():
        return "Permission denied. Please check your system permissions."

    # Generic fallback
    logger.error(f"Unhandled error: {error_type}: {error_str}")
    return "Something went wrong. Please try again or contact support if the problem persists."


def log_error_with_context(
    error: Exception, context: dict[str, Any], operation: str
) -> None:
    """
    Log an error with context information.

    Args:
        error: Exception that occurred
        context: Context dictionary
        operation: Operation being performed
    """
    logger.error(
        f"Error in {operation}: {type(error).__name__}: {str(error)}\n"
        f"Context: {context}",
        exc_info=True,
    )
