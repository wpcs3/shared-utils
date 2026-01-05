"""
OpenAI GPT Client

Supports GPT-4, GPT-4o, and future GPT-5 series models.
"""

from typing import Optional, Dict, List

from shared_utils.llm.client import LLMClient, register_provider
from shared_utils.llm.response import LLMResponse


class OpenAIClient(LLMClient):
    """
    OpenAI GPT client.

    Supports GPT-4o, GPT-4 Turbo, and future GPT-5 models.

    Usage:
        client = OpenAIClient(model="gpt-4o", api_key="...")
        response = client.chat("Hello!")
    """

    # Model ID mapping
    # See: https://platform.openai.com/docs/models
    MODELS = {
        # GPT-4.1 series (April 2025 - 1M context)
        "gpt-4.1": "gpt-4.1",
        "gpt-4.1-mini": "gpt-4.1-mini",
        "gpt-4.1-nano": "gpt-4.1-nano",
        # O-series reasoning models (latest)
        "o3": "o3",
        "o3-mini": "o3-mini",
        "o3-pro": "o3-pro",
        "o4-mini": "o4-mini",
        "o1": "o1",
        "o1-pro": "o1-pro",
        # GPT-4o models (legacy but still available)
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        # Legacy models
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-4": "gpt-4",
    }

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        super().__init__(model, api_key, max_tokens, temperature)

        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model_id = self.MODELS.get(model, model)

    @property
    def provider_name(self) -> str:
        return "openai"

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
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=formatted_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content,
            model=self.model_id,
            provider=self.provider_name,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            },
            finish_reason=choice.finish_reason,
            raw_response=response,
        )


# Register on import
register_provider("openai", OpenAIClient)
