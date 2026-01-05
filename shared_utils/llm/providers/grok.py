"""
xAI Grok Client

Supports Grok-2 and Grok-3 series models via xAI API.
"""

from typing import Optional, Dict, List

from shared_utils.llm.client import LLMClient, register_provider
from shared_utils.llm.response import LLMResponse


class GrokClient(LLMClient):
    """
    xAI Grok client.

    Supports Grok-2 and Grok-3 models via xAI's OpenAI-compatible API.

    The xAI API uses an OpenAI-compatible interface, so we leverage
    the OpenAI SDK with a custom base URL.

    Usage:
        client = GrokClient(model="grok-3", api_key="...")
        response = client.chat("Hello!")

    Environment:
        Set XAI_API_KEY with your xAI API key.
    """

    # Model ID mapping
    MODELS = {
        # Expensive reasoning model / Default model
        "grok": "grok-4-1-fast-reasoning",
        "grok-4": "grok-4-1-fast-reasoning",
        "grok-reasoning": "grok-4-1-fast-reasoning",
        # Inexpensive fast model
        "grok-fast": "grok-4-1-fast-non-reasoning",
        "grok-4-fast": "grok-4-1-fast-non-reasoning",
    }

    # xAI API base URL
    BASE_URL = "https://api.x.ai/v1"

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        super().__init__(model, api_key, max_tokens, temperature)

        # Use OpenAI SDK with xAI base URL
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
        )
        self.model_id = self.MODELS.get(model, model)

    @property
    def provider_name(self) -> str:
        return "grok"

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

        # Handle usage - may not always be present
        usage = {"input_tokens": 0, "output_tokens": 0}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens or 0,
                "output_tokens": response.usage.completion_tokens or 0,
            }

        return LLMResponse(
            content=choice.message.content,
            model=self.model_id,
            provider=self.provider_name,
            usage=usage,
            finish_reason=choice.finish_reason,
            raw_response=response,
        )


# Register on import
register_provider("grok", GrokClient)
