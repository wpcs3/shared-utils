"""
Configuration Utilities

Provides utilities for environment variables and cross-platform paths.

Usage:
    from shared_utils.config import load_env, get_project_root

    # Load .env file
    load_env()

    # Get project root
    root = get_project_root()

    # Get environment variables with defaults and validation
    api_key = get_env("API_KEY", required=True)
    debug = get_env_bool("DEBUG", default=False)
"""

from shared_utils.config.env import (
    load_env,
    get_env,
    get_env_bool,
    get_env_int,
    get_env_float,
    get_env_list,
    validate_env,
)
from shared_utils.config.paths import (
    get_project_root,
    normalize_path,
    ensure_dir,
    get_data_dir,
    get_cache_dir,
    get_config_dir,
    relative_to_project,
    is_subpath,
)

__all__ = [
    # Environment
    "load_env",
    "get_env",
    "get_env_bool",
    "get_env_int",
    "get_env_float",
    "get_env_list",
    "validate_env",
    # Paths
    "get_project_root",
    "normalize_path",
    "ensure_dir",
    "get_data_dir",
    "get_cache_dir",
    "get_config_dir",
    "relative_to_project",
    "is_subpath",
]
