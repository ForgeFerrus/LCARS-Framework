# LCARS Framework :: Recovery v1.0.0
# Recovery context manager for safe block execution
# Автор: LCARS Development Team
# Ліцензія: MIT

from lcars.base.version import getVersion

version = getVersion()
print(f"LCARS Recovery v{version}")

# Recovery context manager for safe block execution (analog of try/except, but without try/except in user code)
class Recovery:
    def __init__(self, exc_type=Exception):
        self.exc_type = exc_type
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
        return isinstance(exc_val, self.exc_type)
