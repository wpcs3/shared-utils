"""
Windows-Safe Logging Module

Provides logging utilities that work correctly on Windows console,
which often can't display emojis and Unicode characters.

Usage:
    from shared_utils.logging import setup_logging, safe_print, timed_operation

    logger = setup_logging("my_app")
    safe_print("Status: ✅ Complete")  # Works on Windows!

    with timed_operation("Processing"):
        # ... your code ...
"""

from shared_utils.logging.windows_safe import (
    SafeStreamHandler,
    safe_print,
    sanitize_for_windows,
    EMOJI_REPLACEMENTS,
)
from shared_utils.logging.formatters import (
    PipelineFormatter,
    setup_logging,
    get_logger,
)
from shared_utils.logging.timing import (
    PipelineTimer,
    StageLogger,
    timed_operation,
    log_timing,
)

__all__ = [
    # Windows safety
    "SafeStreamHandler",
    "safe_print",
    "sanitize_for_windows",
    "EMOJI_REPLACEMENTS",
    # Formatters
    "PipelineFormatter",
    "setup_logging",
    "get_logger",
    # Timing
    "PipelineTimer",
    "StageLogger",
    "timed_operation",
    "log_timing",
]
