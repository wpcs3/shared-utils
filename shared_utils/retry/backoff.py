"""
Exponential Backoff Retry Utilities

Provides decorators and functions for retrying operations with
exponential backoff, supporting both sync and async functions.
"""

import asyncio
import functools
import logging
import time
from typing import Callable, TypeVar, Optional, Set, Union, Any

from shared_utils.retry.errors import RetryableError, NonRetryableError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 30.0

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES: Set[int] = {
    429,  # Rate limit
    500,  # Internal server error
    502,  # Bad gateway
    503,  # Service unavailable
    504,  # Gateway timeout
}

# Status codes that should NOT be retried
NON_RETRYABLE_STATUS_CODES: Set[int] = {
    400,  # Bad request
    401,  # Unauthorized
    403,  # Forbidden
    404,  # Not found
}


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error should trigger a retry.

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable, False otherwise

    Checks:
        - RetryableError: Always retry
        - NonRetryableError: Never retry
        - httpx.HTTPStatusError: Check status code
        - httpx network errors: Retry (ConnectError, TimeoutException)
        - Unknown errors: Don't retry (conservative default)
    """
    if isinstance(error, RetryableError):
        return True
    if isinstance(error, NonRetryableError):
        return False

    # Try to check httpx errors without hard dependency
    try:
        import httpx
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code in RETRYABLE_STATUS_CODES
        if isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
            return True
    except ImportError:
        pass

    # Try to check requests errors
    try:
        import requests
        if isinstance(error, requests.HTTPError):
            if error.response is not None:
                return error.response.status_code in RETRYABLE_STATUS_CODES
        if isinstance(error, (requests.ConnectionError, requests.Timeout)):
            return True
    except ImportError:
        pass

    # Check for common API rate limit errors by message
    error_str = str(error).lower()
    if any(phrase in error_str for phrase in ["rate limit", "too many requests", "429"]):
        return True

    # Default: don't retry unknown errors
    return False


def with_retry(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    retryable_exceptions: Optional[tuple] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
):
    """
    Decorator for async functions that implements exponential backoff retry.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries (default: 30.0)
        retryable_exceptions: Tuple of exception types to retry (optional)
        on_retry: Callback function(attempt, error, delay) called before each retry

    Returns:
        Decorated async function with retry logic

    Usage:
        @with_retry(max_retries=5, base_delay=2.0)
        async def fetch_data():
            response = await client.get(url)
            return response.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Check if we should retry based on exception type
                    if retryable_exceptions and isinstance(e, retryable_exceptions):
                        should_retry = True
                    else:
                        should_retry = is_retryable_error(e)

                    if not should_retry:
                        raise

                    # Check if we have retries left
                    if attempt >= max_retries:
                        logger.warning(f"Max retries ({max_retries}) exceeded: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt + 1, e, delay)
                    else:
                        logger.debug(
                            f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}"
                        )

                    await asyncio.sleep(delay)

            # Should never reach here, but just in case
            if last_error:
                raise last_error
            raise RuntimeError("Retry loop completed without success or error")

        return wrapper
    return decorator


def with_retry_sync(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    retryable_exceptions: Optional[tuple] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
):
    """
    Decorator for sync functions that implements exponential backoff retry.

    Same as with_retry but for synchronous functions.

    Usage:
        @with_retry_sync(max_retries=3)
        def fetch_data():
            response = requests.get(url)
            return response.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Check if we should retry
                    if retryable_exceptions and isinstance(e, retryable_exceptions):
                        should_retry = True
                    else:
                        should_retry = is_retryable_error(e)

                    if not should_retry:
                        raise

                    if attempt >= max_retries:
                        logger.warning(f"Max retries ({max_retries}) exceeded: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)

                    if on_retry:
                        on_retry(attempt + 1, e, delay)
                    else:
                        logger.debug(
                            f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}"
                        )

                    time.sleep(delay)

            if last_error:
                raise last_error
            raise RuntimeError("Retry loop completed without success or error")

        return wrapper
    return decorator


async def retry_async(
    func: Callable[..., T],
    *args,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    **kwargs
) -> T:
    """
    Execute an async function with retry logic (one-off wrapper).

    Alternative to decorator for single calls.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay cap
        **kwargs: Keyword arguments for func

    Returns:
        Result of the function call

    Usage:
        result = await retry_async(fetch_data, url, max_retries=5)
    """
    @with_retry(max_retries=max_retries, base_delay=base_delay, max_delay=max_delay)
    async def wrapped():
        return await func(*args, **kwargs)

    return await wrapped()


def retry_sync(
    func: Callable[..., T],
    *args,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    **kwargs
) -> T:
    """
    Execute a sync function with retry logic (one-off wrapper).

    Args:
        func: Sync function to execute
        *args: Positional arguments for func
        max_retries: Maximum retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay cap
        **kwargs: Keyword arguments for func

    Returns:
        Result of the function call

    Usage:
        result = retry_sync(fetch_data, url, max_retries=5)
    """
    @with_retry_sync(max_retries=max_retries, base_delay=base_delay, max_delay=max_delay)
    def wrapped():
        return func(*args, **kwargs)

    return wrapped()
