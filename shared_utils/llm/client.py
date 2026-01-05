"""
LLM Client Base Class and Factory

Provides abstract base class and factory function for LLM clients.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Type

from shared_utils.llm.response import LLMResponse

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.

    All provider implementations must inherit from this class and
    implement the chat() and chat_with_messages() methods.

    Attributes:
        model: The model identifier
        api_key: API key for authentication
        max_tokens: Maximum tokens for response (from env or default)
        temperature: Sampling temperature (from env or default)
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens or int(os.getenv("LLM_MAX_TOKENS", "4096"))
        self.temperature = temperature or float(os.getenv("LLM_TEMPERATURE", "0.3"))

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'anthropic', 'openai')."""
        pass

    @abstractmethod
    def chat(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        """
        Send a single message and get a response.

        Args:
            prompt: The user message
            system: Optional system prompt

        Returns:
            LLMResponse with the model's response
        """
        pass

    @abstractmethod
    def chat_with_messages(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
    ) -> LLMResponse:
        """
        Send a conversation history and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system: Optional system prompt

        Returns:
            LLMResponse with the model's response
        """
        pass


# Registry for provider classes (populated by imports)
_PROVIDERS: Dict[str, Type[LLMClient]] = {}

# API key environment variable names
API_KEY_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "grok": "XAI_API_KEY",
}

# Default models per provider
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5-20250514",
    "openai": "gpt-4o",
    "google": "gemini-2.0-flash",
    "grok": "grok-3",
}


def register_provider(name: str, client_class: Type[LLMClient]) -> None:
    """Register a provider class."""
    _PROVIDERS[name] = client_class


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> LLMClient:
    """
    Get an LLM client instance.

    Args:
        provider: LLM provider (anthropic, openai, google, grok).
                  Defaults to LLM_PROVIDER env var or "anthropic".
        model: Model name. Defaults to LLM_MODEL env var or provider default.
        api_key: API key. Defaults to provider-specific env var.
        max_tokens: Maximum tokens for response.
        temperature: Sampling temperature.

    Returns:
        LLMClient instance

    Raises:
        ValueError: If provider is unknown or API key is missing

    Example:
        client = get_llm_client()  # Uses env vars
        client = get_llm_client(provider="openai", model="gpt-4o")
        response = client.chat("Hello!")
    """
    # Import providers to ensure registration
    from shared_utils.llm import providers  # noqa: F401

    # Get provider from env if not specified
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

    # Validate provider
    if provider not in _PROVIDERS:
        available = list(_PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider: {provider}. Available: {available}"
        )

    # Get model from env or use provider default
    if model is None:
        model = os.getenv("LLM_MODEL", DEFAULT_MODELS.get(provider, ""))

    # Get API key from env if not provided
    if api_key is None:
        api_key_var = API_KEY_ENV_VARS.get(provider, f"{provider.upper()}_API_KEY")
        api_key = os.getenv(api_key_var)

        if not api_key or api_key.startswith("your_"):
            raise ValueError(
                f"API key not set for {provider}. "
                f"Set {api_key_var} in your environment."
            )

    logger.info(f"Initializing {provider} client with model: {model}")

    # Create and return client
    client_class = _PROVIDERS[provider]
    return client_class(
        model=model,
        api_key=api_key,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def list_available_models() -> Dict[str, List[str]]:
    """
    Return available models by provider.

    Returns:
        Dict mapping provider names to lists of model names
    """
    # Import providers to ensure registration
    from shared_utils.llm import providers  # noqa: F401

    result = {}
    for name, client_class in _PROVIDERS.items():
        if hasattr(client_class, "MODELS"):
            result[name] = list(client_class.MODELS.keys())
        else:
            result[name] = []
    return result


def test_connection(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    """
    Test the LLM connection with a simple prompt.

    Returns:
        True if connection works, False otherwise
    """
    try:
        client = get_llm_client(provider, model)
        response = client.chat("Say 'Hello' and nothing else.")
        logger.info(f"Test successful. Response: {response.content[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
