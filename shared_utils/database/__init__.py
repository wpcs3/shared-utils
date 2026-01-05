"""
Database Utilities

Provides Supabase client utilities for database operations.

Usage:
    from shared_utils.database import get_supabase_client, table

    # Get client directly
    client = get_supabase_client()

    # Or use table helper for queries
    result = table('users').select('*').execute()

    # Insert data
    table('posts').insert({'title': 'Hello', 'content': '...'}).execute()

    # Update data
    table('posts').update({'title': 'Updated'}).eq('id', 1).execute()

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Your Supabase service role key
"""

from shared_utils.database.supabase import (
    # Client management
    get_supabase_client,
    is_supabase_configured,
    check_supabase_connection,
    reset_client,
    # Query helpers
    table,
    rpc,
    storage,
    # Errors
    SupabaseClientError,
    SupabaseNotConfiguredError,
)

__all__ = [
    # Client management
    "get_supabase_client",
    "is_supabase_configured",
    "check_supabase_connection",
    "reset_client",
    # Query helpers
    "table",
    "rpc",
    "storage",
    # Errors
    "SupabaseClientError",
    "SupabaseNotConfiguredError",
]
