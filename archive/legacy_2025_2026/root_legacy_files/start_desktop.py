#!/usr/bin/env python3

import sys
from pathlib import Path

ProjectRoot = Path(__file__).parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.desktop import Run

if __name__ == "__main__":
    sys.exit(Run())


