"""
Timing Utilities

Context managers and decorators for timing operations.
"""

import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Callable, Any, Dict

from shared_utils.logging.formatters import get_logger


# =============================================================================
# TIMING UTILITIES
# =============================================================================

class PipelineTimer:
    """
    Context manager for timing operations with automatic logging.

    Usage:
        with PipelineTimer("Processing data") as timer:
            # ... your code ...
        print(f"Elapsed: {timer.elapsed:.2f}s")
    """

    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        self.operation = operation
        self.logger = logger or get_logger()
        self.start_time: float = 0
        self.end_time: float = 0
        self.elapsed: float = 0

    def __enter__(self) -> "PipelineTimer":
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time

        if exc_type:
            self.logger.error(f"Failed: {self.operation} ({self.elapsed:.2f}s) - {exc_val}")
        else:
            self.logger.info(f"Completed: {self.operation} ({self.elapsed:.2f}s)")

        return False


@contextmanager
def timed_operation(operation: str, logger: Optional[logging.Logger] = None):
    """
    Context manager for timing and logging operations.

    Usage:
        with timed_operation("Fetching data"):
            result = fetch_data()
    """
    timer = PipelineTimer(operation, logger)
    with timer:
        yield timer


def log_timing(operation_name: str = None, logger: logging.Logger = None):
    """
    Decorator to time and log function execution.

    Usage:
        @log_timing("data_processing")
        def process_data():
            # ... your code ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = operation_name or func.__name__
            _logger = logger or get_logger()

            with timed_operation(op_name, _logger):
                return func(*args, **kwargs)

        return wrapper
    return decorator


# =============================================================================
# STAGE LOGGER
# =============================================================================

class StageLogger:
    """
    Helper class for stage-specific logging with progress tracking.

    Usage:
        stage = StageLogger("ingestion")
        stage.start()
        for i, item in enumerate(items):
            process(item)
            stage.item_processed(item.id)
            stage.progress(i + 1, len(items))
        stage.complete()
    """

    def __init__(self, stage_name: str, logger: Optional[logging.Logger] = None):
        self.stage_name = stage_name
        self.logger = logger or get_logger()
        self.start_time: float = 0
        self._item_count = 0
        self._error_count = 0

    def start(self, message: str = None) -> None:
        """Mark stage start."""
        self.start_time = time.time()
        self._item_count = 0
        self._error_count = 0

        msg = message or f"Starting stage: {self.stage_name}"
        self.logger.info(f"[{self.stage_name}] {msg}")

    def progress(self, current: int, total: int, item_name: str = "items") -> None:
        """Log progress for batch operations."""
        pct = (current / total * 100) if total > 0 else 0
        self.logger.debug(
            f"[{self.stage_name}] Progress: {current}/{total} {item_name} ({pct:.1f}%)"
        )

    def item_processed(self, item_id: str = None) -> None:
        """Increment processed item count."""
        self._item_count += 1
        if item_id:
            self.logger.debug(f"[{self.stage_name}] Processed: {item_id}")

    def item_error(self, item_id: str, error: str) -> None:
        """Log item-level error."""
        self._error_count += 1
        self.logger.warning(f"[{self.stage_name}] Error processing {item_id}: {error}")

    def complete(self, message: str = None, stats: Dict[str, Any] = None) -> None:
        """Mark stage complete with summary."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        summary_parts = [f"Completed stage: {self.stage_name}"]
        summary_parts.append(f"({elapsed:.2f}s)")
        summary_parts.append(f"[{self._item_count} items, {self._error_count} errors]")

        if message:
            summary_parts.append(f"- {message}")

        self.logger.info(f"[{self.stage_name}] {' '.join(summary_parts)}")

        if stats:
            for key, value in stats.items():
                self.logger.debug(f"[{self.stage_name}]   {key}: {value}")

    def error(self, message: str, exception: Exception = None) -> None:
        """Log stage-level error."""
        if exception:
            self.logger.error(f"[{self.stage_name}] {message}: {exception}", exc_info=True)
        else:
            self.logger.error(f"[{self.stage_name}] {message}")

    def warning(self, message: str) -> None:
        """Log stage-level warning."""
        self.logger.warning(f"[{self.stage_name}] {message}")

    def info(self, message: str) -> None:
        """Log stage-level info."""
        self.logger.info(f"[{self.stage_name}] {message}")

    def debug(self, message: str) -> None:
        """Log stage-level debug."""
        self.logger.debug(f"[{self.stage_name}] {message}")
