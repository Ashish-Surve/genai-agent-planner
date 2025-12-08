"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from adhd_planner.utils.logger import get_logger

logger = get_logger("llm.base")


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str
    provider: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] = {}


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model_name: str, temperature: float = 0.7):
        """
        Initialize provider.

        Args:
            model_name: Model identifier
            temperature: Sampling temperature (0.0-1.0)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.logger = get_logger(f"llm.{self.provider_name()}")

    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (e.g., 'ollama', 'gemini')."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with generated content

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available.

        Returns:
            True if provider can be used
        """
        pass

    def _log_request(self, prompt: str, system_prompt: str | None) -> None:
        """Log request details."""
        self.logger.debug(
            f"Generating with {self.provider_name()} "
            f"(model={self.model_name}, temp={self.temperature})"
        )
        self.logger.debug(f"Prompt length: {len(prompt)} chars")

    def _log_response(self, response: "LLMResponse") -> None:
        """Log response details."""
        self.logger.debug(
            f"Response from {self.provider_name()}: "
            f"{len(response.content)} chars, "
            f"{response.tokens_used} tokens"
        )
