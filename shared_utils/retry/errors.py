"""
Retry Error Classes

Custom exceptions for controlling retry behavior.
"""


class RetryableError(Exception):
    """
    Exception that should trigger a retry.

    Raise this when an operation fails due to a transient issue
    that may succeed on retry (e.g., rate limiting, temporary outage).

    Usage:
        if response.status_code == 429:
            raise RetryableError("Rate limited, try again later")
    """
    pass


class NonRetryableError(Exception):
    """
    Exception that should NOT be retried.

    Raise this when an operation fails due to a permanent issue
    that will not succeed on retry (e.g., invalid API key, bad request).

    Usage:
        if response.status_code == 401:
            raise NonRetryableError("Invalid API key")
    """
    pass


class MaxRetriesExceeded(Exception):
    """
    Exception raised when all retry attempts are exhausted.

    Contains the original error that caused the final failure.
    """

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error
