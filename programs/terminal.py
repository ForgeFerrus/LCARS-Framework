# LCARS Terminal - Окрема програма

import sys
from pathlib import Path

# Додаємо корінь проекту в шлях
root = Path(__file__).parent.parent.absolute()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from lcars.base.type import LCARS
from lcars.ui.terminal import LCARSTerminal

def main():
    app = LCARS.Application()
    if not app:
        print("Qt not available")
        return

    app = LCARS.Application(sys.argv)
    Display = LCARSTerminal()
    Display.setWindowTitle("LCARS Terminal")
    Display.resize(900, 600)
    Display.setStyleSheet("background-color: black;")
    Display.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
