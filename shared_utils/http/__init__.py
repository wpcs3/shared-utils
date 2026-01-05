"""
HTTP Client Utilities

Provides rate-limited and retry-capable HTTP clients.

Usage:
    from shared_utils.http import RateLimitedClient, RetryingClient

    # Rate-limited client
    async with RateLimitedClient(requests_per_second=5.0) as client:
        response = await client.get("https://api.example.com/data")

    # Client with retries
    async with RetryingClient(max_retries=3) as client:
        response = await client.get("https://api.example.com/data")
"""

from shared_utils.http.client import (
    RateLimiter,
    RateLimitConfig,
    RateLimitedClient,
    RetryingClient,
)

__all__ = [
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitedClient",
    "RetryingClient",
]
