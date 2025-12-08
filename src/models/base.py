"""Base Pydantic model with common functionality."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseAppModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Allow from_orm() for SQLAlchemy models
        validate_assignment=True,  # Validate on field assignment
        use_enum_values=True,  # Use enum values instead of enum objects
        str_strip_whitespace=True,  # Strip whitespace from strings
    )


class TimestampedModel(BaseAppModel):
    """Model with created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    def mark_updated(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
