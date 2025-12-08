"""High-level LLM service with caching and utilities."""

from adhd_planner.integrations.llm.base_provider import LLMResponse
from adhd_planner.integrations.llm.factory import LLMProviderFactory
from adhd_planner.utils.logger import get_logger

logger = get_logger("llm_service")


class LLMService:
    """High-level service for LLM operations."""

    def __init__(
        self,
        provider_name: str | None = None,
        model_name: str | None = None,
        temperature: float = 0.7
    ):
        """
        Initialize LLM service.

        Args:
            provider_name: LLM provider to use
            model_name: Model name
            temperature: Sampling temperature
        """
        self.provider = LLMProviderFactory.create_provider(
            provider_name=provider_name,
            model_name=model_name,
            temperature=temperature
        )
        self.logger = logger

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text content
        """
        response = self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        return response.content

    def generate_with_metadata(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None
    ) -> LLMResponse:
        """
        Generate text and return full response with metadata.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Full LLMResponse object
        """
        return self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )

    def generate_cached(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:
        """
        Generate with caching (for identical prompts).

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text content
        """
        return self.generate(prompt, system_prompt)


# Global service instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def reload_llm_service(provider_name: str | None = None) -> LLMService:
    """Reload LLM service with new provider."""
    global _llm_service
    _llm_service = LLMService(provider_name=provider_name)
    return _llm_service
