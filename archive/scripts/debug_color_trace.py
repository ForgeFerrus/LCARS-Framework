import sys
import logging

# Minimal GUI test to exercise RandomButtonColor and ApplyTitaniumStyles
logging.basicConfig(level=logging.DEBUG)

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
except Exception as e:
    print("PyQt6 not available:", e)
    raise

print("DEBUG SCRIPT: start")
from lcars.base.defaults import RandomButtonColor
from lcars.base.components import LCARSButton

print("RandomButtonColor sample:", RandomButtonColor())

app = QApplication(sys.argv)
btn = LCARSButton("DBG_TEST")
print("Created LCARSButton, stylesheet:", btn.styleSheet())

# Quit shortly after to allow logs to flush
QTimer.singleShot(1200, app.quit)
app.exec()
print("DEBUG SCRIPT: exit")
