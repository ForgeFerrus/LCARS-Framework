"""LCARS compatibility module.

Legacy code does `import LCARS` expecting an `os`-like module. Provide a
transparent proxy to the standard library `os` module so existing imports
work without changing many files.
"""
import os as _os
from typing import Any

# Re-export os public API at module level
__all__ = [name for name in dir(_os) if not name.startswith("__")]
for _name in __all__:
	globals()[_name] = getattr(_os, _name)

def __getattr__(name: str) -> Any:
	return getattr(_os, name)

def __dir__():
	return sorted(list(globals().keys()) + __all__)

