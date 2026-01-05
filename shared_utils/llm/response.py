"""
LLM Response Dataclass

Standardized response format for all LLM providers.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class LLMResponse:
    """
    Standardized response from any LLM provider.

    Attributes:
        content: The text response from the model
        model: The model ID used for generation
        provider: The provider name (anthropic, openai, google, grok)
        usage: Token usage dict with input_tokens and output_tokens
        raw_response: The original provider-specific response object
        finish_reason: Why generation stopped (e.g., 'stop', 'max_tokens')
        metadata: Additional provider-specific metadata

    Usage:
        response = client.chat("Hello!")
        print(response.content)
        print(f"Used {response.total_tokens} tokens")
    """
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Any = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def input_tokens(self) -> int:
        """Number of input/prompt tokens used."""
        return self.usage.get("input_tokens", 0)

    @property
    def output_tokens(self) -> int:
        """Number of output/completion tokens used."""
        return self.usage.get("output_tokens", 0)

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes raw_response)."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata,
        }
