"""Test LLM service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from adhd_planner.services.llm_service import LLMService, get_llm_service, reload_llm_service
from adhd_planner.integrations.llm.base_provider import LLMResponse
from adhd_planner.integrations.llm.factory import LLMProviderFactory


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


def test_llm_service_with_max_tokens(mock_provider):
    """Test generation with max tokens."""
    with patch.object(LLMProviderFactory, 'create_provider', return_value=mock_provider):
        service = LLMService()
        service.generate("Test prompt", max_tokens=100)

        mock_provider.generate.assert_called_with(
            prompt="Test prompt",
            system_prompt=None,
            max_tokens=100
        )


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


def test_get_llm_service_singleton(mock_provider):
    """Test that get_llm_service returns same instance."""
    with patch.object(LLMProviderFactory, 'create_provider', return_value=mock_provider):
        service1 = get_llm_service()
        service2 = get_llm_service()
        assert service1 is service2


def test_reload_llm_service(mock_provider):
    """Test reloading LLM service."""
    with patch.object(LLMProviderFactory, 'create_provider', return_value=mock_provider):
        service1 = reload_llm_service()
        service2 = reload_llm_service()
        # Should be different instances after reload
        assert service1 is not service2
