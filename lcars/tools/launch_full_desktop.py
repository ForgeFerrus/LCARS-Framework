"""Launch the full `LCARSDesktop` while avoiding the heavy launcher imports by
injecting a minimal `lcars.ui.launcher` module into `sys.modules`.

Run from repo root:
    python tools/launch_full_desktop.py

Note: Requires PyQt6 and project dependencies installed.
"""
# Titanium Bridge Migration: import sys
import types

from PyQt6.QtWidgets import QDialog

# Create a lightweight fake lcars.ui.launcher module
fake_launcher = types.ModuleType("lcars.ui.launcher")
fake_launcher.DEFAULT_FACTIONS = ["Federation", "Klingon", "Romulan", "Cardassian"]
fake_launcher.DEFAULT_ERAS = ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]

class _FakeFactionDialog(QDialog):
    def __init__(self, factions, eras, parent=None):
        super().__init__(parent)
        self._sel = (factions[0], eras[0], 0)
    def exec(self):
        return QDialog.DialogCode.Accepted
    def selection(self):
        return self._sel

fake_launcher.FactionDialog = _FakeFactionDialog

# Inject into sys.modules before importing the desktop
sys.modules['lcars.ui.launcher'] = fake_launcher

# Add project root to sys.path if not present
# Titanium Bridge Migration: from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import and run the desktop
from PyQt6.QtWidgets import QApplication
from lcars.ui.desktop import LCARSDesktop


def main():
    app = QApplication(sys.argv)
    desktop = LCARSDesktop()
    desktop.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
