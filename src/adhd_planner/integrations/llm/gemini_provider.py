"""Google Gemini LLM provider implementation."""


from langchain_google_genai import ChatGoogleGenerativeAI

from adhd_planner.integrations.llm.base_provider import BaseLLMProvider, LLMResponse
from adhd_planner.utils.config import get_settings
from adhd_planner.utils.errors import UserFacingError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float = 0.7,
        api_key: str | None = None
    ):
        """
        Initialize Gemini provider.

        Args:
            model_name: Model to use (defaults to config)
            temperature: Sampling temperature
            api_key: Google API key (defaults to config)
        """
        settings = get_settings()
        model_name = model_name or settings.gemini_model
        super().__init__(model_name, temperature)

        self.api_key = api_key or settings.gemini_api_key

        if not self.api_key:
            raise ValueError("Gemini API key not provided")

        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key
        )

    def provider_name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None
    ) -> LLMResponse:
        """Generate response using Gemini."""
        self._log_request(prompt, system_prompt)

        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append(("system", system_prompt))
            messages.append(("human", prompt))

            # Generate
            response = self.llm.invoke(messages)

            llm_response = LLMResponse(
                content=response.content.strip(),
                provider=self.provider_name(),
                model=self.model_name,
                tokens_used=response.response_metadata.get("token_count"),
                metadata=response.response_metadata
            )

            self._log_response(llm_response)
            return llm_response

        except Exception as e:
            error_str = str(e).lower()

            if "api key" in error_str or "authentication" in error_str:
                raise UserFacingError(
                    "Gemini API key is invalid or missing. Please check your configuration.",
                    technical_message=f"Gemini auth error: {e}"
                ) from e
            elif "quota" in error_str or "rate limit" in error_str:
                raise UserFacingError(
                    "Gemini API quota exceeded. Please try again later or check your billing.",
                    technical_message=f"Gemini quota error: {e}"
                ) from e
            else:
                self.logger.error(f"Gemini generation error: {e}")
                raise
