"""
Anthropic Claude Client

Supports Claude Opus, Sonnet, and Haiku models.
"""

from typing import Optional, Dict, List

from shared_utils.llm.client import LLMClient, register_provider
from shared_utils.llm.response import LLMResponse


class AnthropicClient(LLMClient):
    """
    Anthropic Claude client.

    Supports Claude 4.5 series (Opus, Sonnet, Haiku) and legacy models.

    Usage:
        client = AnthropicClient(model="claude-sonnet-4.5", api_key="...")
        response = client.chat("Hello!")
    """

    # Model ID mapping (friendly names -> API IDs)
    MODELS = {
        # Expensive reasoning model
        "claude-opus": "claude-opus-4-5-20250514",
        "claude-opus-4.5": "claude-opus-4-5-20250514",
        # Default model
        "claude-sonnet": "claude-sonnet-4-5-20250514",
        "claude-sonnet-4.5": "claude-sonnet-4-5-20250514",
        # Inexpensive fast model
        "claude-haiku": "claude-haiku-4-5-20251001",
        "claude-haiku-4.5": "claude-haiku-4-5-20251001",
    }

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        super().__init__(model, api_key, max_tokens, temperature)

        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_id = self.MODELS.get(model, model)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def chat(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        """Send a single message."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat_with_messages(messages, system)

    def chat_with_messages(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
    ) -> LLMResponse:
        """Send conversation history."""
        kwargs = {
            "model": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)

        return LLMResponse(
            content=response.content[0].text,
            model=self.model_id,
            provider=self.provider_name,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
            raw_response=response,
        )


# Register on import
register_provider("anthropic", AnthropicClient)
