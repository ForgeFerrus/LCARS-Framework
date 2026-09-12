"""Compatibility shim for EnvironmentManager.

The full implementation has been moved to `lcars.utils.environment`. This
shim re-exports `EnvironmentManager` to avoid breaking imports that still
refer to `lcars.core.environment`.
"""

from lcars.utils.environment import EnvironmentManager  # type: ignore

__all__ = ["EnvironmentManager"]
