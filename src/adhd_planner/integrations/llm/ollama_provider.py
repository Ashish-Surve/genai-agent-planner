"""Ollama LLM provider implementation."""


import requests

from adhd_planner.integrations.llm.base_provider import BaseLLMProvider, LLMResponse
from adhd_planner.utils.config import get_settings
from adhd_planner.utils.errors import UserFacingError


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float = 0.7,
        base_url: str | None = None
    ):
        """
        Initialize Ollama provider.

        Args:
            model_name: Model to use (defaults to config)
            temperature: Sampling temperature
            base_url: Ollama server URL (defaults to config)
        """
        settings = get_settings()
        model_name = model_name or settings.ollama_model
        super().__init__(model_name, temperature)

        self.base_url = base_url or settings.ollama_base_url
        self.generate_url = f"{self.base_url}/api/generate"

    def provider_name(self) -> str:
        return "ollama"

    def is_available(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None
    ) -> LLMResponse:
        """Generate response using Ollama."""
        self._log_request(prompt, system_prompt)

        # Build full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Prepare request
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "temperature": self.temperature,
            "stream": False
        }

        if max_tokens:
            payload["num_predict"] = max_tokens

        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            data = response.json()

            llm_response = LLMResponse(
                content=data.get("response", "").strip(),
                provider=self.provider_name(),
                model=self.model_name,
                tokens_used=data.get("eval_count"),
                finish_reason=data.get("done_reason"),
                metadata={
                    "total_duration": data.get("total_duration"),
                    "load_duration": data.get("load_duration")
                }
            )

            self._log_response(llm_response)
            return llm_response

        except requests.exceptions.ConnectionError as e:
            raise UserFacingError(
                "Cannot connect to Ollama. Please ensure Ollama is running.",
                technical_message="Ollama connection error"
            ) from e
        except requests.exceptions.Timeout as e:
            raise UserFacingError(
                "Ollama request timed out. The model might be too large.",
                technical_message="Ollama timeout"
            ) from e
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
            raise
