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
    MODELS = {
        # Expensive reasoning model / Default model
        "gpt-5": "gpt-5.2-2025-12-11",
        "gpt-5.2": "gpt-5.2-2025-12-11",
        # Inexpensive fast model
        "gpt-5-mini": "gpt-5-mini-2025-08-07",
        # Embeddings
        "text-embedding-large": "text-embedding-3-large",
        "text-embedding-small": "text-embedding-3-small",
        "text-embedding-3-large": "text-embedding-3-large",
        "text-embedding-3-small": "text-embedding-3-small",
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
