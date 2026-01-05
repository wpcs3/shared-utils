"""
Cross-Platform Path Utilities

Provides utilities for finding project roots and normalizing paths
across Windows, macOS, and Linux.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Union


def get_project_root(
    markers: Optional[List[str]] = None,
    start_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Find the project root directory by looking for marker files.

    Searches upward from start_path (or cwd) for directories containing
    any of the marker files/folders.

    Args:
        markers: List of files/folders that indicate project root.
                 Default: [".git", "pyproject.toml", "setup.py", ".env"]
        start_path: Path to start searching from. Default: current directory.

    Returns:
        Path to project root directory

    Raises:
        FileNotFoundError: If no project root found

    Usage:
        root = get_project_root()
        config_path = root / "config" / "settings.yaml"
    """
    if markers is None:
        markers = [".git", "pyproject.toml", "setup.py", ".env", "requirements.txt"]

    if start_path is None:
        current = Path.cwd()
    else:
        current = Path(start_path).resolve()

    # Search current and all parent directories
    for directory in [current] + list(current.parents):
        for marker in markers:
            if (directory / marker).exists():
                return directory

    raise FileNotFoundError(
        f"Could not find project root. Searched for: {markers}"
    )


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a path for cross-platform compatibility.

    - Resolves to absolute path
    - Normalizes separators
    - Resolves symlinks
    - Expands user (~) and environment variables

    Args:
        path: Path string or Path object

    Returns:
        Normalized absolute Path object
    """
    path_str = str(path)

    # Expand user home directory
    path_str = os.path.expanduser(path_str)

    # Expand environment variables
    path_str = os.path.expandvars(path_str)

    # Convert to Path and resolve
    return Path(path_str).resolve()


def ensure_dir(path: Union[str, Path], parents: bool = True) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path
        parents: If True, create parent directories as needed

    Returns:
        Path object for the directory
    """
    path = normalize_path(path)
    path.mkdir(parents=parents, exist_ok=True)
    return path


def get_data_dir(app_name: str) -> Path:
    """
    Get the appropriate data directory for an application.

    Uses platform-specific conventions:
    - Windows: %LOCALAPPDATA%/app_name
    - macOS: ~/Library/Application Support/app_name
    - Linux: ~/.local/share/app_name

    Args:
        app_name: Application name

    Returns:
        Path to data directory (created if needed)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / app_name
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir(app_name: str) -> Path:
    """
    Get the appropriate cache directory for an application.

    Uses platform-specific conventions:
    - Windows: %LOCALAPPDATA%/app_name/cache
    - macOS: ~/Library/Caches/app_name
    - Linux: ~/.cache/app_name

    Args:
        app_name: Application name

    Returns:
        Path to cache directory (created if needed)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        cache_dir = base / app_name / "cache"
    elif sys.platform == "darwin":
        cache_dir = Path.home() / "Library" / "Caches" / app_name
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        cache_dir = base / app_name

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_config_dir(app_name: str) -> Path:
    """
    Get the appropriate config directory for an application.

    Uses platform-specific conventions:
    - Windows: %APPDATA%/app_name
    - macOS: ~/Library/Preferences/app_name
    - Linux: ~/.config/app_name

    Args:
        app_name: Application name

    Returns:
        Path to config directory (created if needed)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Preferences"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    config_dir = base / app_name
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def relative_to_project(
    path: Union[str, Path],
    project_root: Optional[Path] = None,
) -> Path:
    """
    Convert an absolute path to a path relative to project root.

    Args:
        path: Absolute path
        project_root: Project root (auto-detected if None)

    Returns:
        Relative path from project root
    """
    path = normalize_path(path)
    if project_root is None:
        project_root = get_project_root()

    try:
        return path.relative_to(project_root)
    except ValueError:
        # Path is not under project root
        return path


def is_subpath(path: Union[str, Path], parent: Union[str, Path]) -> bool:
    """
    Check if a path is under a parent directory.

    Args:
        path: Path to check
        parent: Parent directory

    Returns:
        True if path is under parent
    """
    path = normalize_path(path)
    parent = normalize_path(parent)

    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
