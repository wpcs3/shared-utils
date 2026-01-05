"""
Google Gemini Client

Supports Gemini 2.0 and 3.0 series models.
"""

from typing import Optional, Dict, List

from shared_utils.llm.client import LLMClient, register_provider
from shared_utils.llm.response import LLMResponse


class GoogleClient(LLMClient):
    """
    Google Gemini client.

    Supports Gemini 2.0, 2.5, and 3.0 series models.

    Usage:
        client = GoogleClient(model="gemini-2.0-flash", api_key="...")
        response = client.chat("Hello!")
    """

    # Model ID mapping
    MODELS = {
        # Gemini 3.0 (preview)
        "gemini-3-pro-preview": "gemini-3.0-pro-preview",
        "gemini-3-flash-preview": "gemini-3.0-flash-preview",
        # Gemini 2.5
        "gemini-2.5-pro": "gemini-2.5-pro",
        "gemini-2.5-flash": "gemini-2.5-flash",
        # Gemini 2.0
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.0-flash-thinking": "gemini-2.0-flash-thinking-exp",
        # Gemini 1.5 (legacy)
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash",
    }

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        super().__init__(model, api_key, max_tokens, temperature)

        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model_id = self.MODELS.get(model, model)

    @property
    def provider_name(self) -> str:
        return "google"

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
        from google.genai import types

        # Build generation config
        config_kwargs = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        if system:
            config_kwargs["system_instruction"] = system

        config = types.GenerateContentConfig(**config_kwargs)

        # Convert messages to Gemini format
        # For multi-turn, build contents list
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            ))

        # Make API call
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config,
        )

        # Extract usage metadata
        usage = {
            "input_tokens": getattr(
                response.usage_metadata, "prompt_token_count", 0
            ),
            "output_tokens": getattr(
                response.usage_metadata, "candidates_token_count", 0
            ),
        }

        # Get finish reason
        finish_reason = None
        if response.candidates:
            finish_reason = str(response.candidates[0].finish_reason)

        return LLMResponse(
            content=response.text,
            model=self.model_id,
            provider=self.provider_name,
            usage=usage,
            finish_reason=finish_reason,
            raw_response=response,
        )


# Register on import
register_provider("google", GoogleClient)
