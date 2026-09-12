# [LCARS] English Learning System - Launcher Wrapper
# ------------------------------------------------------
# This file provides the entry point to the learning interface.
# It launches the desktop learning UI using the shared LCARS application layer.

import sys
from pathlib import Path

# Resolve project root
projRoot = Path(__file__).resolve().parents[2]
if str(projRoot) not in sys.path:
    sys.path.insert(0, str(projRoot))

from programs.learning.English import main as runEnglishMain

def main():
    # Unified launch path goes through programs.learning.English.
    sys.exit(runEnglishMain())

if __name__ == "__main__":
    main()
