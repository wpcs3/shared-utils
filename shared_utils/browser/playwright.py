"""
Playwright Browser Utilities

Provides helpers for browser automation with Playwright.
"""

import asyncio
import functools
import logging
from pathlib import Path
from typing import Optional, Any, Callable, TypeVar
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

T = TypeVar("T")


@asynccontextmanager
async def get_browser(
    headless: bool = True,
    browser_type: str = "chromium",
    slow_mo: int = 0,
    timeout: int = 30000,
    user_data_dir: Optional[Path] = None,
):
    """
    Context manager for Playwright browser.

    Args:
        headless: Run browser in headless mode
        browser_type: Browser type (chromium, firefox, webkit)
        slow_mo: Slow down operations by ms (for debugging)
        timeout: Default timeout in ms
        user_data_dir: Path to persistent browser profile

    Yields:
        Browser context and page

    Usage:
        async with get_browser(headless=False) as (browser, page):
            await page.goto("https://example.com")
            content = await page.content()
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser_launcher = getattr(p, browser_type)

        # Launch with or without persistent context
        if user_data_dir:
            context = await browser_launcher.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=headless,
                slow_mo=slow_mo,
            )
            page = context.pages[0] if context.pages else await context.new_page()
            page.set_default_timeout(timeout)

            try:
                yield context, page
            finally:
                await context.close()
        else:
            browser = await browser_launcher.launch(
                headless=headless,
                slow_mo=slow_mo,
            )
            context = await browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(timeout)

            try:
                yield browser, page
            finally:
                await browser.close()


async def safe_navigate(
    page: Any,
    url: str,
    wait_until: str = "domcontentloaded",
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> bool:
    """
    Navigate to a URL with retry logic.

    Args:
        page: Playwright page object
        url: URL to navigate to
        wait_until: When to consider navigation complete
                   ("load", "domcontentloaded", "networkidle")
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        True if navigation succeeded, False otherwise
    """
    for attempt in range(max_retries + 1):
        try:
            await page.goto(url, wait_until=wait_until)
            return True
        except Exception as e:
            if attempt < max_retries:
                logger.warning(
                    f"Navigation failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Navigation failed after {max_retries} retries: {e}")
                return False

    return False


def screenshot_on_error(
    screenshot_dir: Path,
    filename_prefix: str = "error",
):
    """
    Decorator to capture screenshot on exception.

    The decorated function must receive a 'page' keyword argument.

    Args:
        screenshot_dir: Directory to save screenshots
        filename_prefix: Prefix for screenshot filenames

    Usage:
        @screenshot_on_error(Path("./screenshots"))
        async def scrape_page(page):
            await page.goto("https://example.com")
            # If this raises, screenshot is saved
            await page.click("#missing-button")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Try to get page from kwargs or args
                page = kwargs.get("page")
                if page is None and args:
                    # Check if first arg has screenshot method
                    if hasattr(args[0], "screenshot"):
                        page = args[0]

                if page:
                    try:
                        screenshot_dir.mkdir(parents=True, exist_ok=True)
                        import time
                        timestamp = int(time.time())
                        path = screenshot_dir / f"{filename_prefix}_{timestamp}.png"
                        await page.screenshot(path=str(path))
                        logger.error(f"Screenshot saved: {path}")
                    except Exception as screenshot_error:
                        logger.warning(f"Failed to save screenshot: {screenshot_error}")

                raise

        return wrapper
    return decorator


async def wait_for_element(
    page: Any,
    selector: str,
    timeout: int = 10000,
    state: str = "visible",
) -> Optional[Any]:
    """
    Wait for an element with error handling.

    Args:
        page: Playwright page object
        selector: CSS selector
        timeout: Maximum wait time in ms
        state: Element state to wait for ("visible", "attached", "hidden")

    Returns:
        Element handle or None if not found
    """
    try:
        element = await page.wait_for_selector(
            selector,
            timeout=timeout,
            state=state,
        )
        return element
    except Exception as e:
        logger.debug(f"Element not found: {selector} - {e}")
        return None


async def extract_text(
    page: Any,
    selector: str,
    default: str = "",
) -> str:
    """
    Extract text content from an element.

    Args:
        page: Playwright page object
        selector: CSS selector
        default: Default value if element not found

    Returns:
        Text content or default value
    """
    try:
        element = await page.query_selector(selector)
        if element:
            return await element.inner_text()
        return default
    except Exception:
        return default


async def extract_attribute(
    page: Any,
    selector: str,
    attribute: str,
    default: str = "",
) -> str:
    """
    Extract an attribute from an element.

    Args:
        page: Playwright page object
        selector: CSS selector
        attribute: Attribute name (e.g., "href", "src")
        default: Default value if not found

    Returns:
        Attribute value or default
    """
    try:
        element = await page.query_selector(selector)
        if element:
            value = await element.get_attribute(attribute)
            return value or default
        return default
    except Exception:
        return default
