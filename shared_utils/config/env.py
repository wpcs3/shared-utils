"""
Environment Variable Utilities

Provides utilities for loading and validating environment variables.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, TypeVar, Type

T = TypeVar("T")


def load_env(
    env_file: Optional[str] = None,
    override: bool = False,
) -> bool:
    """
    Load environment variables from a .env file.

    Args:
        env_file: Path to .env file. If None, searches for .env in
                  current directory and parent directories.
        override: If True, override existing environment variables.

    Returns:
        True if .env file was loaded, False otherwise

    Usage:
        from shared_utils.config import load_env

        load_env()  # Loads .env from project root
        load_env("config/.env.local")  # Load specific file
        load_env(override=True)  # Override existing vars
    """
    from dotenv import load_dotenv

    if env_file:
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path, override=override)
            return True
        return False

    # Search for .env file in current and parent directories
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=override)
            return True

    return False


def get_env(
    key: str,
    default: Optional[str] = None,
    required: bool = False,
) -> Optional[str]:
    """
    Get an environment variable with optional default and validation.

    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raise ValueError if not set

    Returns:
        Environment variable value

    Raises:
        ValueError: If required=True and variable is not set

    Usage:
        api_key = get_env("API_KEY", required=True)
        debug = get_env("DEBUG", default="false")
    """
    value = os.getenv(key, default)

    if required and (value is None or value == ""):
        raise ValueError(f"Required environment variable not set: {key}")

    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get an environment variable as a boolean.

    True values: "true", "1", "yes", "on" (case-insensitive)
    False values: everything else

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Boolean value
    """
    value = os.getenv(key)
    if value is None:
        return default

    return value.lower() in ("true", "1", "yes", "on")


def get_env_int(
    key: str,
    default: Optional[int] = None,
    required: bool = False,
) -> Optional[int]:
    """
    Get an environment variable as an integer.

    Args:
        key: Environment variable name
        default: Default value if not set or invalid
        required: If True, raise ValueError if not set

    Returns:
        Integer value

    Raises:
        ValueError: If required and not set, or if value is not a valid integer
    """
    value = get_env(key, required=required)

    if value is None or value == "":
        return default

    try:
        return int(value)
    except ValueError:
        if required:
            raise ValueError(f"Environment variable {key} must be an integer: {value}")
        return default


def get_env_float(
    key: str,
    default: Optional[float] = None,
    required: bool = False,
) -> Optional[float]:
    """
    Get an environment variable as a float.

    Args:
        key: Environment variable name
        default: Default value if not set or invalid
        required: If True, raise ValueError if not set

    Returns:
        Float value
    """
    value = get_env(key, required=required)

    if value is None or value == "":
        return default

    try:
        return float(value)
    except ValueError:
        if required:
            raise ValueError(f"Environment variable {key} must be a number: {value}")
        return default


def get_env_list(
    key: str,
    separator: str = ",",
    default: Optional[List[str]] = None,
) -> List[str]:
    """
    Get an environment variable as a list of strings.

    Args:
        key: Environment variable name
        separator: String to split on (default: comma)
        default: Default list if not set

    Returns:
        List of stripped strings

    Usage:
        # ALLOWED_HOSTS=localhost,127.0.0.1,example.com
        hosts = get_env_list("ALLOWED_HOSTS")
        # Returns: ["localhost", "127.0.0.1", "example.com"]
    """
    value = os.getenv(key)

    if value is None or value == "":
        return default or []

    return [item.strip() for item in value.split(separator) if item.strip()]


def validate_env(
    required_vars: List[str],
    optional_vars: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Validate that required environment variables are set.

    Args:
        required_vars: List of required variable names
        optional_vars: List of optional variable names (for info only)

    Returns:
        Dict with 'valid' (bool), 'missing' (list), and 'values' (dict)

    Raises:
        ValueError: If any required variables are missing

    Usage:
        validate_env(["API_KEY", "DATABASE_URL"])
    """
    missing = []
    values = {}

    for var in required_vars:
        value = os.getenv(var)
        if value is None or value == "":
            missing.append(var)
        else:
            values[var] = value

    if optional_vars:
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                values[var] = value

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return {"valid": True, "missing": [], "values": values}
