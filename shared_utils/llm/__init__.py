"""
Unified LLM Client Module

Provides a consistent interface for multiple LLM providers:
- Anthropic (Claude Opus, Sonnet, Haiku)
- OpenAI (GPT-4o, GPT-5 series)
- Google (Gemini 2.0, 2.5, 3.0)
- xAI (Grok-2, Grok-3)

Usage:
    from shared_utils.llm import get_llm_client

    # Use environment variables (LLM_PROVIDER, LLM_MODEL)
    client = get_llm_client()
    response = client.chat("What is AI?")
    print(response.content)
    print(f"Used {response.total_tokens} tokens")

    # Or specify provider/model explicitly
    client = get_llm_client(provider="grok", model="grok-3")

Environment Variables:
    LLM_PROVIDER: Default provider (anthropic, openai, google, grok)
    LLM_MODEL: Default model name
    LLM_MAX_TOKENS: Max tokens for response (default: 4096)
    LLM_TEMPERATURE: Sampling temperature (default: 0.3)
    ANTHROPIC_API_KEY: Anthropic API key
    OPENAI_API_KEY: OpenAI API key
    GOOGLE_API_KEY: Google AI API key
    XAI_API_KEY: xAI API key for Grok
"""

from shared_utils.llm.response import LLMResponse
from shared_utils.llm.client import (
    LLMClient,
    get_llm_client,
    list_available_models,
    test_connection,
    register_provider,
)
from shared_utils.llm.providers import (
    AnthropicClient,
    OpenAIClient,
    GoogleClient,
    GrokClient,
)

__all__ = [
    # Core types
    "LLMResponse",
    "LLMClient",
    # Factory functions
    "get_llm_client",
    "list_available_models",
    "test_connection",
    "register_provider",
    # Provider clients
    "AnthropicClient",
    "OpenAIClient",
    "GoogleClient",
    "GrokClient",
]
