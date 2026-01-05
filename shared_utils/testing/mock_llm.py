"""
Mock LLM Client for Testing

Provides a mock LLM client that returns configurable responses.
"""

from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field

from shared_utils.llm.response import LLMResponse
from shared_utils.llm.client import LLMClient


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing.

    Returns configurable responses without making API calls.

    Usage:
        # Simple usage
        client = MockLLMClient(response="Hello!")
        response = client.chat("Hi")
        assert response.content == "Hello!"

        # Multiple responses (cycles through)
        client = MockLLMClient(responses=["First", "Second", "Third"])
        assert client.chat("1").content == "First"
        assert client.chat("2").content == "Second"
        assert client.chat("3").content == "Third"
        assert client.chat("4").content == "First"  # Cycles

        # Dynamic response based on prompt
        client = MockLLMClient(
            response_fn=lambda prompt, system: f"You said: {prompt}"
        )
        assert client.chat("hello").content == "You said: hello"

        # Track calls
        client = MockLLMClient(response="OK")
        client.chat("message 1")
        client.chat("message 2")
        assert len(client.calls) == 2
        assert client.calls[0]["prompt"] == "message 1"
    """

    def __init__(
        self,
        response: Optional[str] = None,
        responses: Optional[List[str]] = None,
        response_fn: Optional[Callable[[str, Optional[str]], str]] = None,
        model: str = "mock-model",
        usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        error_after: int = 0,
    ):
        """
        Initialize mock client.

        Args:
            response: Static response to return
            responses: List of responses to cycle through
            response_fn: Function(prompt, system) -> response
            model: Model name to report
            usage: Token usage to report
            error: Exception to raise
            error_after: Raise error after N successful calls
        """
        super().__init__(model=model, api_key="mock-key")

        self.response = response or "Mock response"
        self.responses = responses
        self.response_fn = response_fn
        self.usage = usage or {"input_tokens": 10, "output_tokens": 20}
        self.error = error
        self.error_after = error_after

        self.calls: List[Dict[str, Any]] = []
        self._response_index = 0
        self._call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    def _get_response(self, prompt: str, system: Optional[str]) -> str:
        """Get the next response based on configuration."""
        if self.response_fn:
            return self.response_fn(prompt, system)
        elif self.responses:
            response = self.responses[self._response_index % len(self.responses)]
            self._response_index += 1
            return response
        else:
            return self.response

    def chat(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        """Mock chat implementation."""
        self._call_count += 1

        # Record the call
        self.calls.append({
            "prompt": prompt,
            "system": system,
            "messages": None,
        })

        # Check if we should error
        if self.error and self._call_count > self.error_after:
            raise self.error

        content = self._get_response(prompt, system)

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider_name,
            usage=self.usage.copy(),
            finish_reason="stop",
        )

    def chat_with_messages(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
    ) -> LLMResponse:
        """Mock chat with messages implementation."""
        self._call_count += 1

        # Record the call
        self.calls.append({
            "prompt": None,
            "system": system,
            "messages": messages,
        })

        # Check if we should error
        if self.error and self._call_count > self.error_after:
            raise self.error

        # Use last message as prompt
        last_message = messages[-1]["content"] if messages else ""
        content = self._get_response(last_message, system)

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider_name,
            usage=self.usage.copy(),
            finish_reason="stop",
        )

    def reset(self) -> None:
        """Reset call history and state."""
        self.calls = []
        self._response_index = 0
        self._call_count = 0

    def assert_called_with(self, prompt: str, system: Optional[str] = None) -> None:
        """Assert that chat was called with specific arguments."""
        for call in self.calls:
            if call["prompt"] == prompt:
                if system is None or call["system"] == system:
                    return
        raise AssertionError(
            f"Expected call with prompt='{prompt}', system='{system}' not found. "
            f"Calls: {self.calls}"
        )

    def assert_not_called(self) -> None:
        """Assert that no calls were made."""
        if self.calls:
            raise AssertionError(f"Expected no calls but got {len(self.calls)}")


@dataclass
class MockLLMClientFactory:
    """
    Factory for creating mock LLM clients with preset configurations.

    Usage:
        factory = MockLLMClientFactory()

        # Create client that always returns same response
        client = factory.create(response="Fixed response")

        # Create client that simulates rate limiting
        client = factory.create_rate_limited(fail_first=2)

        # Create client that returns JSON
        client = factory.create_json_responder({"status": "ok"})
    """

    def create(self, **kwargs) -> MockLLMClient:
        """Create a mock client with custom settings."""
        return MockLLMClient(**kwargs)

    def create_rate_limited(
        self,
        fail_first: int = 1,
        final_response: str = "Success",
    ) -> MockLLMClient:
        """Create a client that fails first N times with rate limit error."""
        from shared_utils.retry import RetryableError

        return MockLLMClient(
            response=final_response,
            error=RetryableError("Rate limited"),
            error_after=fail_first,
        )

    def create_json_responder(self, data: Dict[str, Any]) -> MockLLMClient:
        """Create a client that returns JSON responses."""
        import json
        return MockLLMClient(response=json.dumps(data))

    def create_echo(self) -> MockLLMClient:
        """Create a client that echoes the prompt."""
        return MockLLMClient(response_fn=lambda p, s: f"Echo: {p}")
