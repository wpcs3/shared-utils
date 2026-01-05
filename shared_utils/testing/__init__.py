"""
Testing Utilities

Provides mock clients for testing code that depends on external services.

Usage:
    from shared_utils.testing import MockLLMClient, MockHTTPClient

    # Mock LLM client
    client = MockLLMClient(response="Test response")
    response = client.chat("Hello")
    assert response.content == "Test response"

    # Mock HTTP client
    http = MockHTTPClient()
    http.add_response("https://api.example.com/data", {"status": "ok"})
    response = await http.get("https://api.example.com/data")
    assert response.json() == {"status": "ok"}
"""

from shared_utils.testing.mock_llm import (
    MockLLMClient,
    MockLLMClientFactory,
)
from shared_utils.testing.mock_http import (
    MockResponse,
    MockHTTPError,
    MockHTTPClient,
)

__all__ = [
    # LLM mocks
    "MockLLMClient",
    "MockLLMClientFactory",
    # HTTP mocks
    "MockResponse",
    "MockHTTPError",
    "MockHTTPClient",
]
