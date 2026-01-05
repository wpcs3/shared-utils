"""
Playwright Browser Utilities

Provides helpers for browser automation with Playwright.

Usage:
    from shared_utils.browser import get_browser, safe_navigate

    async with get_browser(headless=True) as (browser, page):
        await safe_navigate(page, "https://example.com")
        content = await page.content()

Requires:
    pip install shared_utils[browser]
    # or
    pip install playwright && playwright install
"""

from shared_utils.browser.playwright import (
    get_browser,
    safe_navigate,
    screenshot_on_error,
    wait_for_element,
    extract_text,
    extract_attribute,
)

__all__ = [
    "get_browser",
    "safe_navigate",
    "screenshot_on_error",
    "wait_for_element",
    "extract_text",
    "extract_attribute",
]
