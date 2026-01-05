"""
Shared Python Utilities

A collection of reusable utilities for Python projects:
- logging: Windows-safe logging with emoji fallbacks
- llm: Unified LLM client (Anthropic, OpenAI, Google, Grok)
- retry: Exponential backoff decorators
- database: Supabase helpers
- config: Environment and path utilities
- http: Rate-limited HTTP client
- browser: Playwright helpers
- schemas: Pydantic utilities
- testing: Mock clients for testing
"""

__version__ = "0.1.0"

# Convenience imports for common usage
from shared_utils.logging import safe_print, setup_logging
