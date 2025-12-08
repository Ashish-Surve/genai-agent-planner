"""LLM provider factory."""


from adhd_planner.integrations.llm.base_provider import BaseLLMProvider
from adhd_planner.integrations.llm.claude_provider import ClaudeProvider
from adhd_planner.integrations.llm.gemini_provider import GeminiProvider
from adhd_planner.integrations.llm.ollama_provider import OllamaProvider
from adhd_planner.utils.config import get_settings
from adhd_planner.utils.logger import get_logger

logger = get_logger("llm.factory")


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    _providers = {
        "ollama": OllamaProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "anthropic": ClaudeProvider,  # Alias
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Provider to use (defaults to config)
            model_name: Model to use (defaults to provider default)
            temperature: Sampling temperature (defaults to config)

        Returns:
            Configured provider instance

        Raises:
            ValueError: If provider is unknown or unavailable
        """
        settings = get_settings()

        provider_name = provider_name or settings.llm_provider
        provider_name_lower = provider_name.lower()

        if provider_name_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name_lower]

        # Create provider with optional overrides
        kwargs = {}
        if model_name:
            kwargs["model_name"] = model_name
        if temperature is not None:
            kwargs["temperature"] = temperature

        provider = provider_class(**kwargs)

        # Check availability
        if not provider.is_available():
            logger.warning(f"Provider {provider_name} is not available")
            raise ValueError(
                f"Provider {provider_name} is not available. "
                f"Please check your configuration."
            )

        logger.info(f"Created {provider_name} provider with model {provider.model_name}")
        return provider

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())
