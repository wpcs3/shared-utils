"""
HTTP Client Utilities

Provides rate-limited and retry-capable HTTP clients.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: float = 10.0
    burst_size: int = 10
    retry_after_header: str = "Retry-After"


class RateLimiter:
    """
    Token bucket rate limiter.

    Limits the rate of operations to prevent hitting API rate limits.

    Usage:
        limiter = RateLimiter(requests_per_second=5.0)

        async with limiter:
            response = await client.get(url)
    """

    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: Optional[int] = None,
    ):
        self.rate = requests_per_second
        self.burst_size = burst_size or int(requests_per_second)
        self.tokens = float(self.burst_size)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Add tokens based on elapsed time
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.rate
            )

            if self.tokens < 1:
                # Calculate wait time
                wait_time = (1 - self.tokens) / self.rate
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class RateLimitedClient:
    """
    Async HTTP client with rate limiting.

    Wraps httpx.AsyncClient with automatic rate limiting.

    Usage:
        async with RateLimitedClient(requests_per_second=5.0) as client:
            response = await client.get("https://api.example.com/data")
    """

    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: Optional[int] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.limiter = RateLimiter(requests_per_second, burst_size)
        self.timeout = timeout
        self.headers = headers or {}
        self._client = None

    async def __aenter__(self):
        import httpx
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        """Make a rate-limited request."""
        async with self.limiter:
            response = await getattr(self._client, method)(url, **kwargs)
            response.raise_for_status()
            return response

    async def get(self, url: str, **kwargs) -> Any:
        """Rate-limited GET request."""
        return await self._request("get", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Any:
        """Rate-limited POST request."""
        return await self._request("post", url, **kwargs)

    async def put(self, url: str, **kwargs) -> Any:
        """Rate-limited PUT request."""
        return await self._request("put", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Any:
        """Rate-limited DELETE request."""
        return await self._request("delete", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Any:
        """Rate-limited PATCH request."""
        return await self._request("patch", url, **kwargs)


class RetryingClient:
    """
    Async HTTP client with automatic retries.

    Combines rate limiting with exponential backoff retries.

    Usage:
        async with RetryingClient(max_retries=3) as client:
            response = await client.get("https://api.example.com/data")
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        requests_per_second: float = 10.0,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.rate_limited_client = RateLimitedClient(
            requests_per_second=requests_per_second,
            timeout=timeout,
            headers=headers,
        )

    async def __aenter__(self):
        await self.rate_limited_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rate_limited_client.__aexit__(exc_type, exc_val, exc_tb)

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> Any:
        """Make a request with retries."""
        import httpx

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return await getattr(self.rate_limited_client, method)(url, **kwargs)
            except httpx.HTTPStatusError as e:
                last_error = e
                status = e.response.status_code

                # Don't retry client errors (except 429)
                if 400 <= status < 500 and status != 429:
                    raise

                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)

                    # Check for Retry-After header
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            pass

                    logger.warning(
                        f"Request failed ({status}), retry {attempt + 1}/{self.max_retries} "
                        f"after {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(
                        f"Connection failed, retry {attempt + 1}/{self.max_retries} "
                        f"after {delay:.1f}s: {e}"
                    )
                    await asyncio.sleep(delay)

        raise last_error

    async def get(self, url: str, **kwargs) -> Any:
        """GET request with retries."""
        return await self._request_with_retry("get", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Any:
        """POST request with retries."""
        return await self._request_with_retry("post", url, **kwargs)

    async def put(self, url: str, **kwargs) -> Any:
        """PUT request with retries."""
        return await self._request_with_retry("put", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Any:
        """DELETE request with retries."""
        return await self._request_with_retry("delete", url, **kwargs)
