from __future__ import annotations
# Titanium Bridge Migration: from pathlib import Path

from .system_manager import OperatingSystemManager


def LaunchOperatingSystem(root_path: Path | None = None) -> OperatingSystemManager:
    manager = OperatingSystemManager(root_path)
    manager.Boot()
    return manager


if __name__ == "__main__":
    manager = LaunchOperatingSystem()
    print("LCARS Core Operating System initialized.")
    print(manager.Status())
