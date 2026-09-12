import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from lcars.ui.desktop import LCARSDesktop
from lcars.themes.lcars_palette import LCARSEra

def main():
    app = QApplication(sys.argv)
    desktop = LCARSDesktop()
    desktop.setup_desktop("FEDERATION", "25th")
    desktop.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
