import sys
import pathlib
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Ensure project root is on sys.path so package imports work when running this script
project_root = str(pathlib.Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from lcars.ui.desktop import LCARSDesktop
except Exception:
    import traceback
    traceback.print_exc()
    raise

app = QApplication([])
win = LCARSDesktop()
win.show()
print('WINDOW_CREATED')
# Quit after short delay so test is non-blocking
QTimer.singleShot(800, app.quit)
ret = app.exec()
print('EXIT', ret)
sys.exit(ret)
