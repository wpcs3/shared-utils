"""
Supabase Client Utilities

Provides a centralized Supabase client with:
- Lazy initialization (client created on first use)
- Environment variable configuration
- Error handling for missing credentials
- Connection health checking
"""

import os
from functools import lru_cache
from typing import Optional, Tuple, Any

from shared_utils.config import load_env

# Ensure environment is loaded
load_env()


class SupabaseClientError(Exception):
    """Raised when Supabase client cannot be initialized."""
    pass


class SupabaseNotConfiguredError(SupabaseClientError):
    """Raised when Supabase credentials are not configured."""
    pass


@lru_cache(maxsize=1)
def get_supabase_client():
    """
    Get or create a Supabase client singleton.

    Uses lru_cache to ensure only one client instance exists.

    Environment Variables:
        SUPABASE_URL: Your Supabase project URL
        SUPABASE_SERVICE_KEY: Your Supabase service role key

    Returns:
        supabase.Client: Configured Supabase client

    Raises:
        SupabaseNotConfiguredError: If credentials not set
        SupabaseClientError: If client creation fails

    Usage:
        from shared_utils.database import get_supabase_client

        client = get_supabase_client()
        result = client.table('users').select('*').execute()
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        missing = []
        if not url:
            missing.append("SUPABASE_URL")
        if not key:
            missing.append("SUPABASE_SERVICE_KEY")
        raise SupabaseNotConfiguredError(
            f"Missing Supabase credentials: {', '.join(missing)}. "
            "Please configure these in your .env file."
        )

    try:
        from supabase import create_client, Client
        client: Client = create_client(url, key)
        return client
    except ImportError:
        raise SupabaseClientError(
            "supabase package not installed. Run: pip install supabase"
        )
    except Exception as e:
        raise SupabaseClientError(f"Failed to create Supabase client: {e}")


def is_supabase_configured() -> bool:
    """
    Check if Supabase credentials are configured.

    Returns:
        bool: True if both SUPABASE_URL and SUPABASE_SERVICE_KEY are set
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return bool(url and key)


def check_supabase_connection() -> Tuple[bool, Optional[str]]:
    """
    Test the Supabase connection.

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    if not is_supabase_configured():
        return False, "Supabase credentials not configured"

    try:
        client = get_supabase_client()
        # Client creation succeeded
        return True, None
    except SupabaseClientError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Connection test failed: {e}"


def reset_client() -> None:
    """
    Reset the cached client.

    Useful for testing or after credential changes.
    """
    get_supabase_client.cache_clear()


def table(name: str) -> Any:
    """
    Get a table reference for queries.

    Args:
        name: Table name

    Returns:
        Table reference for building queries

    Usage:
        from shared_utils.database import table

        # Insert
        table('items').insert({'title': 'Test'}).execute()

        # Select
        result = table('items').select('*').eq('id', 1).execute()

        # Update
        table('items').update({'title': 'New'}).eq('id', 1).execute()

        # Delete
        table('items').delete().eq('id', 1).execute()
    """
    client = get_supabase_client()
    return client.table(name)


def rpc(function_name: str, params: Optional[dict] = None) -> Any:
    """
    Call a Supabase RPC (stored procedure/function).

    Args:
        function_name: Name of the Postgres function
        params: Parameters to pass to the function

    Returns:
        Result of the RPC call

    Usage:
        result = rpc('get_user_stats', {'user_id': 123}).execute()
    """
    client = get_supabase_client()
    return client.rpc(function_name, params or {})


def storage(bucket_name: str) -> Any:
    """
    Get a storage bucket reference.

    Args:
        bucket_name: Name of the storage bucket

    Returns:
        Storage bucket reference

    Usage:
        from shared_utils.database import storage

        # Upload file
        storage('avatars').upload('user1.png', file_data)

        # Download file
        data = storage('avatars').download('user1.png')

        # Get public URL
        url = storage('avatars').get_public_url('user1.png')
    """
    client = get_supabase_client()
    return client.storage.from_(bucket_name)
