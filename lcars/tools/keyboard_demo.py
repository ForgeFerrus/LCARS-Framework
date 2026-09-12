"""
Simple demo harness to show TitaniumKeyboard attached to a QMainWindow.
Adds project root to sys.path so imports resolve when run from tools/.
"""
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt6.QtCore import QTimer

from tools.keyboard import TitaniumKeyboard


def run_demo():
    app = QApplication.instance() or QApplication([])
    main_win = QMainWindow()
    main_win.resize(900, 600)

    # central widget to receive keystrokes
    txt = QTextEdit()
    main_win.setCentralWidget(txt)
    main_win.show()

    kb = TitaniumKeyboard(FactionStr='Federation', EraStr='25th')
    kb.attach_to(main_win, with_toggle=True)

    # show drawer briefly then hide and quit
    kb.showDrawer(duration=300)
    QTimer.singleShot(900, lambda: kb.hideDrawer(duration=300))
    QTimer.singleShot(1400, app.quit)

    return app.exec()


if __name__ == '__main__':
    sys.exit(run_demo())
