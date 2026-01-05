"""
Windows Console Unicode Safety

Handles UnicodeEncodeError that occurs when printing emojis
to Windows console (which often uses cp1252 encoding).
"""

import logging
import sys
from typing import Dict


# =============================================================================
# EMOJI REPLACEMENTS FOR WINDOWS CONSOLE COMPATIBILITY
# =============================================================================

EMOJI_REPLACEMENTS: Dict[str, str] = {
    # Status indicators
    '\u2705': '[OK]',      # ✅
    '\u274c': '[X]',       # ❌
    '\u26a0\ufe0f': '[!]', # ⚠️
    '\u26a0': '[!]',       # ⚠ (without variation selector)

    # Data/charts
    '\U0001f4ca': '[=]',   # 📊
    '\U0001f4c8': '[^]',   # 📈
    '\U0001f4c9': '[v]',   # 📉

    # Actions
    '\U0001f50d': '[?]',   # 🔍
    '\U0001f4a1': '[*]',   # 💡
    '\U0001f680': '[>]',   # 🚀
    '\u23f3': '[~]',       # ⏳
    '\u2728': '[+]',       # ✨
    '\U0001f3af': '[o]',   # 🎯
    '\U0001f4dd': '[-]',   # 📝
    '\U0001f504': '[R]',   # 🔄

    # Status colors
    '\u2b1c': '[ ]',       # ⬜
    '\U0001f7e2': '[G]',   # 🟢
    '\U0001f534': '[R]',   # 🔴
    '\U0001f7e1': '[Y]',   # 🟡
    '\U0001f7e0': '[O]',   # 🟠

    # Common symbols
    '\u2192': '->',        # →
    '\u2190': '<-',        # ←
    '\u2713': '[v]',       # ✓
    '\u2717': '[x]',       # ✗
}


def sanitize_for_windows(text: str) -> str:
    """
    Replace emojis with ASCII equivalents for Windows console compatibility.

    Args:
        text: String that may contain emojis

    Returns:
        String with emojis replaced by ASCII equivalents
    """
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        text = text.replace(emoji, replacement)
    return text


def safe_print(*args, **kwargs) -> None:
    """
    Print that handles Unicode encoding errors on Windows.

    Use this instead of print() when outputting text that may contain emojis
    or other Unicode characters that Windows console can't display.

    Works identically to built-in print() but with fallback encoding.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Convert all args to sanitized strings
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(sanitize_for_windows(arg))
            else:
                try:
                    safe_args.append(sanitize_for_windows(str(arg)))
                except Exception:
                    safe_args.append(str(arg))
        try:
            print(*safe_args, **kwargs)
        except UnicodeEncodeError:
            # Last resort: encode with 'replace' error handling
            for safe_arg in safe_args:
                encoded = safe_arg.encode('ascii', errors='replace').decode('ascii')
                print(encoded, **kwargs)


class SafeStreamHandler(logging.StreamHandler):
    """
    A StreamHandler that gracefully handles Unicode encoding errors on Windows.

    On Windows, the console often uses cp1252 encoding which can't display emojis.
    This handler catches encoding errors and replaces problematic characters.

    Usage:
        handler = SafeStreamHandler(sys.stdout)
        logger.addHandler(handler)
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            stream = self.stream

            # Try to write directly first
            try:
                stream.write(msg + self.terminator)
                self.flush()
            except UnicodeEncodeError:
                # If encoding fails, sanitize the message and try again
                safe_msg = sanitize_for_windows(msg)
                try:
                    stream.write(safe_msg + self.terminator)
                except UnicodeEncodeError:
                    # Last resort: encode with 'replace' error handling
                    encoding = stream.encoding or 'utf-8'
                    safe_msg = safe_msg.encode(encoding, errors='replace').decode(encoding, errors='replace')
                    stream.write(safe_msg + self.terminator)
                self.flush()

        except RecursionError:
            raise
        except Exception:
            self.handleError(record)
