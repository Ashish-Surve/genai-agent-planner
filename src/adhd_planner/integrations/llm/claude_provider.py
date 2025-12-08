"""Anthropic Claude LLM provider implementation."""


from langchain_anthropic import ChatAnthropic

from adhd_planner.integrations.llm.base_provider import BaseLLMProvider, LLMResponse
from adhd_planner.utils.config import get_settings
from adhd_planner.utils.errors import UserFacingError


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float = 0.7,
        api_key: str | None = None
    ):
        """
        Initialize Claude provider.

        Args:
            model_name: Model to use (defaults to config)
            temperature: Sampling temperature
            api_key: Anthropic API key (defaults to config)
        """
        settings = get_settings()
        model_name = model_name or settings.anthropic_model
        super().__init__(model_name, temperature)

        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.llm = ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            anthropic_api_key=self.api_key
        )

    def provider_name(self) -> str:
        return "claude"

    def is_available(self) -> bool:
        """Check if Claude API key is configured."""
        return bool(self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None
    ) -> LLMResponse:
        """Generate response using Claude."""
        self._log_request(prompt, system_prompt)

        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append(("system", system_prompt))
            messages.append(("human", prompt))

            # Create LLM with max_tokens if specified
            llm = self.llm
            if max_tokens:
                llm = llm.bind(max_tokens=max_tokens)

            # Generate
            response = llm.invoke(messages)

            llm_response = LLMResponse(
                content=response.content.strip(),
                provider=self.provider_name(),
                model=self.model_name,
                tokens_used=response.response_metadata.get("usage", {}).get("total_tokens"),
                finish_reason=response.response_metadata.get("stop_reason"),
                metadata=response.response_metadata
            )

            self._log_response(llm_response)
            return llm_response

        except Exception as e:
            error_str = str(e).lower()

            if "api key" in error_str or "authentication" in error_str:
                raise UserFacingError(
                    "Claude API key is invalid or missing. Please check your configuration.",
                    technical_message=f"Claude auth error: {e}"
                ) from e
            elif "rate limit" in error_str:
                raise UserFacingError(
                    "Claude API rate limit exceeded. Please try again in a moment.",
                    technical_message=f"Claude rate limit: {e}"
                ) from e
            else:
                self.logger.error(f"Claude generation error: {e}")
                raise
