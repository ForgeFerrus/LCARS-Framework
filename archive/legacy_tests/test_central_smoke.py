from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import sys, os

def run_smoke():
    # ensure repo root on sys.path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    app = QApplication(sys.argv)
    from lcars.ui.lcars_central import LCARSCentralSystem
    win = LCARSCentralSystem()

    # Navigate through known workspace pages
    keys = ['dashboard','applications','operations','analytics','communications','utilities','system','ai','file_manager']
    for k in keys:
        win.switch_workspace(k)

    # close after short delay
    QTimer.singleShot(1000, app.quit)
    app.exec()

if __name__ == '__main__':
    run_smoke()
