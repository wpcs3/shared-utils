# Shared Python Utilities

A collection of reusable Python utilities for cross-project use.

## Installation

### From GitHub (recommended for any device)

```bash
pip install git+https://github.com/wpcs3/shared-utils.git
```

### Local Development

```bash
cd C:\Users\wpcol\claudecode\shared_utils
pip install -e .
```

### Optional Dependencies

```bash
# LLM providers (Anthropic, OpenAI, Google)
pip install shared_utils[llm]

# Supabase database
pip install shared_utils[supabase]

# Playwright browser automation
pip install shared_utils[browser]

# All optional dependencies
pip install shared_utils[all]
```

## Modules

### logging - Windows-Safe Logging

Provides logging utilities that work correctly on Windows console, which often can't display emojis and Unicode characters.

```python
from shared_utils.logging import setup_logging, safe_print, timed_operation

# Setup colored console logging
logger = setup_logging("my_app")

# Print safely on Windows (emojis → ASCII)
safe_print("Status: ✅ Complete")  # Shows "[OK] Complete" on Windows

# Time operations
with timed_operation("Processing data"):
    process_data()
# Logs: "Completed: Processing data (2.34s)"
```

### llm - Unified LLM Client

Consistent interface for multiple LLM providers: Anthropic, OpenAI, Google, and xAI Grok.

```python
from shared_utils.llm import get_llm_client

# Uses LLM_PROVIDER and LLM_MODEL from environment
client = get_llm_client()
response = client.chat("What is AI?")
print(response.content)
print(f"Used {response.total_tokens} tokens")

# Or specify provider/model explicitly
client = get_llm_client(provider="grok", model="grok-3")
```

**Environment Variables:**
- `LLM_PROVIDER`: anthropic, openai, google, or grok
- `LLM_MODEL`: Model name
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY`

### retry - Exponential Backoff

Decorators for retrying operations with exponential backoff.

```python
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
```

### config - Environment & Paths

Utilities for environment variables and cross-platform paths.

```python
from shared_utils.config import load_env, get_env, get_project_root

# Load .env file
load_env()

# Get environment variables with validation
api_key = get_env("API_KEY", required=True)
debug = get_env_bool("DEBUG", default=False)
hosts = get_env_list("ALLOWED_HOSTS")

# Cross-platform paths
root = get_project_root()
data_dir = get_data_dir("my_app")  # Platform-appropriate location
```

### database - Supabase Helpers

Centralized Supabase client with connection management.

```python
from shared_utils.database import get_supabase_client, table

# Get client
client = get_supabase_client()

# Or use table helper
result = table('users').select('*').eq('id', 1).execute()

# Insert/Update/Delete
table('posts').insert({'title': 'Hello'}).execute()
table('posts').update({'title': 'Updated'}).eq('id', 1).execute()
table('posts').delete().eq('id', 1).execute()
```

**Environment Variables:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key

### http - Rate-Limited HTTP

HTTP clients with built-in rate limiting and retries.

```python
from shared_utils.http import RateLimitedClient, RetryingClient

# Rate-limited client
async with RateLimitedClient(requests_per_second=5.0) as client:
    response = await client.get("https://api.example.com/data")

# Client with retries
async with RetryingClient(max_retries=3) as client:
    response = await client.get("https://api.example.com/data")
```

### browser - Playwright Helpers

Utilities for browser automation with Playwright.

```python
from shared_utils.browser import get_browser, safe_navigate

async with get_browser(headless=True) as (browser, page):
    await safe_navigate(page, "https://example.com", max_retries=3)
    content = await page.content()
```

### schemas - Pydantic Utilities

Helpers for working with Pydantic models.

```python
from shared_utils.schemas import to_json_schema, validate_json

# Generate JSON schema
schema = to_json_schema(MyModel)

# Validate data (raises on error)
instance = validate_json(MyModel, {"name": "John"})

# Safe validation (returns None on failure)
instance = validate_json_safe(MyModel, data)
```

### testing - Mock Utilities

Mock clients for testing.

```python
from shared_utils.testing import MockLLMClient, MockHTTPClient

# Mock LLM
client = MockLLMClient(response="Test response")
response = client.chat("Hello")
assert response.content == "Test response"
assert len(client.calls) == 1

# Mock HTTP
http = MockHTTPClient()
http.add_response("https://api.example.com/data", {"status": "ok"})
response = await http.get("https://api.example.com/data")
assert response.json() == {"status": "ok"}
```

## Project Structure

```
shared_utils/
├── pyproject.toml
├── README.md
└── shared_utils/
    ├── __init__.py
    ├── logging/       # Windows-safe logging
    ├── llm/           # Unified LLM client
    ├── retry/         # Exponential backoff
    ├── config/        # Environment & paths
    ├── database/      # Supabase helpers
    ├── http/          # Rate-limited HTTP
    ├── browser/       # Playwright helpers
    ├── schemas/       # Pydantic utilities
    └── testing/       # Mock clients
```

## License

MIT
