"""
Logging Formatters and Setup

Provides colored console output and centralized logging configuration.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from shared_utils.logging.windows_safe import SafeStreamHandler


# =============================================================================
# CONFIGURATION
# =============================================================================

LOG_LEVELS: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

DEFAULT_CONSOLE_LEVEL = "INFO"
DEFAULT_FILE_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# =============================================================================
# FORMATTERS
# =============================================================================

class PipelineFormatter(logging.Formatter):
    """Custom formatter with optional color support for terminal output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }

    def __init__(self, use_colors: bool = True):
        super().__init__(LOG_FORMAT, LOG_DATE_FORMAT)
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        if self.use_colors:
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            return f"{color}{formatted}{reset}"

        return formatted


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

def setup_logging(
    name: str = "app",
    console_level: str = DEFAULT_CONSOLE_LEVEL,
    file_level: str = DEFAULT_FILE_LEVEL,
    log_dir: Optional[Path] = None,
    run_id: Optional[str] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Set up logging with console and optional file output.

    Args:
        name: Logger name
        console_level: Minimum level for console output
        file_level: Minimum level for file output
        log_dir: Directory for log files (None = no file logging)
        run_id: Optional run ID to include in log filename
        use_colors: Whether to use colored console output

    Returns:
        Configured logger instance

    Example:
        logger = setup_logging("my_app", console_level="DEBUG")
        logger.info("Application started")
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # Capture all, filter at handler level

    # Console handler - use SafeStreamHandler for Windows emoji compatibility
    console_handler = SafeStreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVELS.get(console_level.upper(), logging.INFO))
    console_handler.setFormatter(PipelineFormatter(use_colors=use_colors))
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y.%m.%d")
        if run_id:
            log_filename = f"{name}_{date_str}_{run_id}.log"
        else:
            log_filename = f"{name}_{date_str}.log"

        file_handler = logging.FileHandler(
            log_dir / log_filename,
            encoding='utf-8'
        )
        file_handler.setLevel(LOG_LEVELS.get(file_level.upper(), logging.DEBUG))
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """
    Get a logger instance. Sets up logging if not already configured.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        return setup_logging(name)

    return logger
