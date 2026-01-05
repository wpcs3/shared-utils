"""
Retry Module with Exponential Backoff

Provides decorators and utilities for retrying operations that may fail
due to transient errors (rate limits, network issues, server errors).

Usage:
    from shared_utils.retry import with_retry, with_retry_sync

    # Async decorator
    @with_retry(max_retries=3, base_delay=1.0)
    async def fetch_data():
        response = await client.get(url)
        return response.json()

    # Sync decorator
    @with_retry_sync(max_retries=3)
    def call_api():
        return requests.get(url).json()

    # One-off retry
    result = await retry_async(fetch_data, url, max_retries=5)

    # Custom retryable error
    from shared_utils.retry import RetryableError
    if rate_limited:
        raise RetryableError("Rate limited, will retry")
"""

from shared_utils.retry.errors import (
    RetryableError,
    NonRetryableError,
    MaxRetriesExceeded,
)
from shared_utils.retry.backoff import (
    with_retry,
    with_retry_sync,
    retry_async,
    retry_sync,
    is_retryable_error,
    RETRYABLE_STATUS_CODES,
    NON_RETRYABLE_STATUS_CODES,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BASE_DELAY,
    DEFAULT_MAX_DELAY,
)

__all__ = [
    # Error classes
    "RetryableError",
    "NonRetryableError",
    "MaxRetriesExceeded",
    # Decorators
    "with_retry",
    "with_retry_sync",
    # One-off functions
    "retry_async",
    "retry_sync",
    # Utilities
    "is_retryable_error",
    # Constants
    "RETRYABLE_STATUS_CODES",
    "NON_RETRYABLE_STATUS_CODES",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_BASE_DELAY",
    "DEFAULT_MAX_DELAY",
]
