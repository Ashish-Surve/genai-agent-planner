# ADHD-7: LLM Service & Provider Factory

## Story Information

- **Epic**: Core Services
- **Story Points**: 3
- **Estimated Time**: 3 hours
- **Prerequisites**: ADHD-6 (Configuration & Logging Enhancement)
- **Status**: 📋 Not Started

## Description

Implement the LLM service layer with a factory pattern to support multiple LLM providers (Ollama, Google Gemini, Anthropic Claude). This abstraction allows agents to use LLMs without knowing the specific provider, and enables easy switching between providers.

## Goals

1. Create base LLM provider interface
2. Implement Ollama provider (local)
3. Implement Google Gemini provider (API)
4. Implement Anthropic Claude provider (API)
5. Create provider factory for runtime selection
6. Implement prompt template management
7. Add response parsing utilities

## Acceptance Criteria

- [ ] Base provider interface defined
- [ ] All three providers implemented and tested
- [ ] Factory creates correct provider based on configuration
- [ ] Providers handle errors gracefully
- [ ] Prompt templates are reusable
- [ ] Response parsing handles edge cases
- [ ] All providers return consistent response format

## Files to Create

```
src/integrations/llm/base_provider.py       # Abstract base class
src/integrations/llm/ollama_provider.py     # Ollama implementation
src/integrations/llm/gemini_provider.py     # Gemini implementation
src/integrations/llm/claude_provider.py     # Claude implementation
src/integrations/llm/factory.py             # Provider factory
src/services/llm_service.py                 # High-level LLM service
src/utils/prompts.py                        # Prompt templates
tests/unit/test_llm_service.py              # Service tests
```

## Implementation Steps

### Step 1: Base Provider Interface (20 min)

**File**: `src/integrations/llm/base_provider.py`

```python
"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from src.utils.logger import get_logger

logger = get_logger("llm.base")


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


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
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
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

    def _log_request(self, prompt: str, system_prompt: Optional[str]) -> None:
        """Log request details."""
        self.logger.debug(
            f"Generating with {self.provider_name()} "
            f"(model={self.model_name}, temp={self.temperature})"
        )
        self.logger.debug(f"Prompt length: {len(prompt)} chars")

    def _log_response(self, response: LLMResponse) -> None:
        """Log response details."""
        self.logger.debug(
            f"Response from {self.provider_name()}: "
            f"{len(response.content)} chars, "
            f"{response.tokens_used} tokens"
        )
```

### Step 2: Ollama Provider (30 min)

**File**: `src/integrations/llm/ollama_provider.py`

```python
"""Ollama LLM provider implementation."""

from typing import Optional
import requests
from src.integrations.llm.base_provider import BaseLLMProvider, LLMResponse
from src.utils.config import get_settings
from src.utils.errors import UserFacingError


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        base_url: Optional[str] = None
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
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
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

        except requests.exceptions.ConnectionError:
            raise UserFacingError(
                "Cannot connect to Ollama. Please ensure Ollama is running.",
                technical_message="Ollama connection error"
            )
        except requests.exceptions.Timeout:
            raise UserFacingError(
                "Ollama request timed out. The model might be too large.",
                technical_message="Ollama timeout"
            )
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
            raise
```

### Step 3: Gemini Provider (30 min)

**File**: `src/integrations/llm/gemini_provider.py`

```python
"""Google Gemini LLM provider implementation."""

from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from src.integrations.llm.base_provider import BaseLLMProvider, LLMResponse
from src.utils.config import get_settings
from src.utils.errors import UserFacingError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        api_key: Optional[str] = None
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
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
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
                )
            elif "quota" in error_str or "rate limit" in error_str:
                raise UserFacingError(
                    "Gemini API quota exceeded. Please try again later or check your billing.",
                    technical_message=f"Gemini quota error: {e}"
                )
            else:
                self.logger.error(f"Gemini generation error: {e}")
                raise
```

### Step 4: Claude Provider (30 min)

**File**: `src/integrations/llm/claude_provider.py`

```python
"""Anthropic Claude LLM provider implementation."""

from typing import Optional
from langchain_anthropic import ChatAnthropic
from src.integrations.llm.base_provider import BaseLLMProvider, LLMResponse
from src.utils.config import get_settings
from src.utils.errors import UserFacingError


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        api_key: Optional[str] = None
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
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate response using Claude."""
        self._log_request(prompt, system_prompt)

        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append(("system", system_prompt))
            messages.append(("human", prompt))

            # Set max tokens if specified
            if max_tokens:
                self.llm.max_tokens = max_tokens

            # Generate
            response = self.llm.invoke(messages)

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
                )
            elif "rate limit" in error_str:
                raise UserFacingError(
                    "Claude API rate limit exceeded. Please try again in a moment.",
                    technical_message=f"Claude rate limit: {e}"
                )
            else:
                self.logger.error(f"Claude generation error: {e}")
                raise
```

### Step 5: Provider Factory (20 min)

**File**: `src/integrations/llm/factory.py`

```python
"""LLM provider factory."""

from typing import Optional
from src.integrations.llm.base_provider import BaseLLMProvider
from src.integrations.llm.ollama_provider import OllamaProvider
from src.integrations.llm.gemini_provider import GeminiProvider
from src.integrations.llm.claude_provider import ClaudeProvider
from src.utils.config import get_settings
from src.utils.logger import get_logger

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
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None
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
```

### Step 6: High-Level LLM Service (30 min)

**File**: `src/services/llm_service.py`

```python
"""High-level LLM service with caching and utilities."""

from typing import Optional, Dict, Any
from functools import lru_cache
from src.integrations.llm.factory import LLMProviderFactory
from src.integrations.llm.base_provider import LLMResponse
from src.utils.logger import get_logger

logger = get_logger("llm_service")


class LLMService:
    """High-level service for LLM operations."""

    def __init__(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
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
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
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
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
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

    @lru_cache(maxsize=100)
    def generate_cached(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
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
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def reload_llm_service(provider_name: Optional[str] = None) -> LLMService:
    """Reload LLM service with new provider."""
    global _llm_service
    _llm_service = LLMService(provider_name=provider_name)
    return _llm_service
```

### Step 7: Prompt Templates (20 min)

**File**: `src/utils/prompts.py`

```python
"""Reusable prompt templates."""

from typing import Dict, Any


def format_prompt(template: str, **kwargs: Any) -> str:
    """
    Format a prompt template with variables.

    Args:
        template: Prompt template with {variable} placeholders
        **kwargs: Variable values

    Returns:
        Formatted prompt
    """
    return template.format(**kwargs)


# System prompts
PLANNING_SYSTEM_PROMPT = """You are a helpful AI assistant specializing in task planning
for people with ADHD. You understand the challenges of executive function, context switching,
and energy management. Always provide clear, actionable suggestions."""

SCHEDULING_SYSTEM_PROMPT = """You are an AI scheduling assistant that creates ADHD-friendly
schedules. Consider energy levels, break needs, buffer time, and context switching costs.
Prioritize realistic, sustainable schedules over cramming tasks."""

# Task extraction prompt
EXTRACT_TASKS_PROMPT = """Extract tasks from the following text. For each task, identify:
- Title (brief, clear)
- Estimated duration in minutes
- Energy level needed (LOW, MEDIUM, HIGH)
- Priority (URGENT, HIGH, MEDIUM, LOW)

Text: {text}

Return tasks in a structured format."""

# Time estimation prompt
ESTIMATE_DURATION_PROMPT = """Estimate how long this task will take, considering:
- Task complexity
- Need for focus
- Potential interruptions
- ADHD time-blindness (add buffer)

Task: {task_title}
Description: {task_description}

Provide estimate in minutes. Be realistic and generous."""
```

### Step 8: Unit Tests (30 min)

**File**: `tests/unit/test_llm_service.py`

```python
"""Test LLM service."""

import pytest
from unittest.mock import Mock, patch
from src.services.llm_service import LLMService
from src.integrations.llm.base_provider import LLMResponse
from src.integrations.llm.factory import LLMProviderFactory


@pytest.fixture
def mock_provider():
    """Create mock LLM provider."""
    provider = Mock()
    provider.provider_name.return_value = "mock"
    provider.model_name = "test-model"
    provider.is_available.return_value = True
    provider.generate.return_value = LLMResponse(
        content="Test response",
        provider="mock",
        model="test-model",
        tokens_used=10
    )
    return provider


def test_llm_service_generate(mock_provider):
    """Test basic generation."""
    with patch.object(LLMProviderFactory, 'create_provider', return_value=mock_provider):
        service = LLMService()
        response = service.generate("Test prompt")

        assert response == "Test response"
        mock_provider.generate.assert_called_once()


def test_llm_service_with_system_prompt(mock_provider):
    """Test generation with system prompt."""
    with patch.object(LLMProviderFactory, 'create_provider', return_value=mock_provider):
        service = LLMService()
        service.generate("Test prompt", system_prompt="System instructions")

        mock_provider.generate.assert_called_with(
            prompt="Test prompt",
            system_prompt="System instructions",
            max_tokens=None
        )


def test_llm_service_generate_with_metadata(mock_provider):
    """Test generation with full metadata."""
    with patch.object(LLMProviderFactory, 'create_provider', return_value=mock_provider):
        service = LLMService()
        response = service.generate_with_metadata("Test prompt")

        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.provider == "mock"
        assert response.tokens_used == 10


def test_provider_factory_unknown_provider():
    """Test factory with unknown provider."""
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        LLMProviderFactory.create_provider(provider_name="invalid")


def test_get_available_providers():
    """Test getting available providers."""
    providers = LLMProviderFactory.get_available_providers()
    assert "ollama" in providers
    assert "gemini" in providers
    assert "claude" in providers
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_llm_service.py -v

# 2. Test Ollama (if running locally)
uv run python -c "
from src.integrations.llm.ollama_provider import OllamaProvider
provider = OllamaProvider()
if provider.is_available():
    response = provider.generate('Say hello')
    print(f'Ollama: {response.content}')
else:
    print('Ollama not available')
"

# 3. Test factory
uv run python -c "
from src.integrations.llm.factory import LLMProviderFactory
print('Available providers:', LLMProviderFactory.get_available_providers())
"

# 4. Test LLM service
uv run python -c "
from src.services.llm_service import get_llm_service
service = get_llm_service()
print(f'Using provider: {service.provider.provider_name()}')
"

# 5. Run all tests
uv run pytest tests/unit/ -v

# 6. Code quality
uv run ruff check src/integrations/llm/ src/services/llm_service.py
uv run black --check src/integrations/ src/services/
```

## Success Criteria

- ✅ All three providers implemented
- ✅ Factory creates correct provider
- ✅ Providers handle errors gracefully
- ✅ Consistent response format across providers
- ✅ Unit tests pass with mocked providers
- ✅ Integration works with at least one provider
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: Ollama connection refused
**Solution**: Ensure Ollama is running with `ollama serve` or install Ollama

### Issue: API key errors
**Solution**: Set API keys in `.env` file (GEMINI_API_KEY, ANTHROPIC_API_KEY)

### Issue: Import errors with langchain packages
**Solution**: Run `uv sync` to ensure all dependencies installed

### Issue: Timeout on first request
**Solution**: First Ollama request loads model - increase timeout or pre-load model

## Next Story

Once this story is complete, move to:
**[ADHD-8: Task Service](ADHD-8-task-service.md)**

## Notes

- Start with Ollama for development (free, local, no API key needed)
- API providers (Gemini, Claude) are optional - add keys when needed
- LLM responses can be cached to reduce costs and latency
- Always handle LLM errors gracefully - don't crash the app
- Consider rate limiting for API providers to avoid quota issues