# Launcher for PCARS.

import argparse
from pathlib import Path

from .lcars_manager import LcarsManager


def start(configPath: Path = Path(__file__).resolve().parent / "config.json", defaultEra: str | None = None) -> LcarsManager:
    manager = LcarsManager(configPath)
    manager.Boot()
    if defaultEra:
        try:
            manager.SelectEra(defaultEra)
        except KeyError:
            print(f"Warning: era '{defaultEra}' is not available")
    return manager


def main() -> int:
    parser = argparse.ArgumentParser(description="Start the PCARS core manager")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parent / "config.json"), help="Path to PCARS config file")
    parser.add_argument("--era", help="Era key to activate on boot")
    args = parser.parse_args()

    manager = start(Path(args.config), args.era)
    print("PCARS LCARS manager status:", manager.GetStatus())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
