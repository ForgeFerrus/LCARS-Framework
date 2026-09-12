# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import os
import logging

Log = logging.getLogger("paths")


def get_project_root() -> str:
    """Return the project root directory as a string.

    This is a minimal implementation used by UI components to locate
    project files when running from source.
    """
    # Prefer environment override for tests/CI
    env = os.environ.get("LCARS_PROJECT_ROOT")
    if env:
        return env
    # Fallback: two levels up from this file
    return str(Path(".").resolve().parent.parent)


def get_config_dir() -> str:
    """Return a writable config directory for LCARS user configs.

    Uses XDG-style or falls back to a `.lcars` folder in the project root.
    """
    env = os.environ.get("LCARS_CONFIG_DIR")
    if env:
        return env
    # Try common user config locations
    home = Path.home()
    cfg = home / ".lcars"
    cfg.mkdir(parents=True, exist_ok=True)
    return str(cfg)
