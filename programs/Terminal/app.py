# ◤ LCARS STANDALONE TERMINAL APPLICATION 🖖
from __future__ import annotations

import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.ui.terminal import main, User

if __name__ == "__main__":
    sys.exit(main())
