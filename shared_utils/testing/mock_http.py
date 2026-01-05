"""
Mock HTTP Client for Testing

Provides mock HTTP responses for testing HTTP-dependent code.
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
import json


@dataclass
class MockResponse:
    """
    Mock HTTP response.

    Mimics httpx.Response interface for testing.
    """
    status_code: int = 200
    content: bytes = b""
    headers: Dict[str, str] = field(default_factory=dict)
    _json: Optional[Any] = None
    _text: Optional[str] = None

    @property
    def text(self) -> str:
        if self._text is not None:
            return self._text
        return self.content.decode("utf-8")

    def json(self) -> Any:
        if self._json is not None:
            return self._json
        return json.loads(self.content)

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            raise MockHTTPError(f"HTTP {self.status_code}", response=self)

    @classmethod
    def ok(cls, data: Any = None, text: str = None) -> "MockResponse":
        """Create a 200 OK response."""
        if data is not None:
            return cls(
                status_code=200,
                content=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                _json=data,
            )
        elif text is not None:
            return cls(
                status_code=200,
                content=text.encode(),
                _text=text,
            )
        return cls(status_code=200)

    @classmethod
    def error(cls, status_code: int, message: str = "") -> "MockResponse":
        """Create an error response."""
        return cls(
            status_code=status_code,
            content=message.encode(),
            _text=message,
        )

    @classmethod
    def rate_limited(cls, retry_after: int = 60) -> "MockResponse":
        """Create a 429 rate limit response."""
        return cls(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content=b"Rate limited",
        )


class MockHTTPError(Exception):
    """Mock HTTP error for testing."""

    def __init__(self, message: str, response: MockResponse = None):
        super().__init__(message)
        self.response = response


class MockHTTPClient:
    """
    Mock HTTP client for testing.

    Records all requests and returns configurable responses.

    Usage:
        # Basic usage
        client = MockHTTPClient()
        client.add_response("https://api.example.com/data", {"status": "ok"})

        response = await client.get("https://api.example.com/data")
        assert response.json() == {"status": "ok"}

        # Check recorded requests
        assert len(client.requests) == 1
        assert client.requests[0]["url"] == "https://api.example.com/data"

        # Pattern matching
        client.add_response_pattern(r".*users/\\d+", {"id": 123})
        response = await client.get("https://api.example.com/users/456")
    """

    def __init__(self, default_response: Optional[MockResponse] = None):
        self.default_response = default_response or MockResponse.ok()
        self.responses: Dict[str, MockResponse] = {}
        self.response_patterns: List[tuple] = []  # (pattern, response)
        self.response_fn: Optional[Callable] = None
        self.requests: List[Dict[str, Any]] = []
        self.error: Optional[Exception] = None

    def add_response(
        self,
        url: str,
        data: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Add a response for a specific URL."""
        if data is not None:
            response = MockResponse(
                status_code=status_code,
                content=json.dumps(data).encode(),
                headers=headers or {"Content-Type": "application/json"},
                _json=data,
            )
        else:
            response = MockResponse(
                status_code=status_code,
                headers=headers or {},
            )
        self.responses[url] = response

    def add_response_pattern(
        self,
        pattern: str,
        data: Any = None,
        status_code: int = 200,
    ) -> None:
        """Add a response for URLs matching a regex pattern."""
        import re
        if data is not None:
            response = MockResponse(
                status_code=status_code,
                content=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                _json=data,
            )
        else:
            response = MockResponse(status_code=status_code)
        self.response_patterns.append((re.compile(pattern), response))

    def set_response_fn(
        self,
        fn: Callable[[str, str, Dict], MockResponse],
    ) -> None:
        """
        Set a function to generate responses dynamically.

        fn(method, url, kwargs) -> MockResponse
        """
        self.response_fn = fn

    def set_error(self, error: Exception) -> None:
        """Set an error to raise on next request."""
        self.error = error

    def _get_response(self, url: str) -> MockResponse:
        """Get response for a URL."""
        # Check exact match
        if url in self.responses:
            return self.responses[url]

        # Check patterns
        import re
        for pattern, response in self.response_patterns:
            if pattern.match(url):
                return response

        # Return default
        return self.default_response

    async def _request(self, method: str, url: str, **kwargs) -> MockResponse:
        """Record request and return response."""
        self.requests.append({
            "method": method,
            "url": url,
            **kwargs,
        })

        if self.error:
            error = self.error
            self.error = None  # Clear for next request
            raise error

        if self.response_fn:
            return self.response_fn(method, url, kwargs)

        return self._get_response(url)

    async def get(self, url: str, **kwargs) -> MockResponse:
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> MockResponse:
        return await self._request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> MockResponse:
        return await self._request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> MockResponse:
        return await self._request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> MockResponse:
        return await self._request("DELETE", url, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def reset(self) -> None:
        """Reset recorded requests."""
        self.requests = []

    def assert_called(self, url: str, method: str = None) -> None:
        """Assert that a URL was called."""
        for req in self.requests:
            if req["url"] == url:
                if method is None or req["method"] == method:
                    return
        raise AssertionError(f"Expected call to {url} not found")

    def assert_not_called(self) -> None:
        """Assert no requests were made."""
        if self.requests:
            raise AssertionError(f"Expected no calls but got {len(self.requests)}")
