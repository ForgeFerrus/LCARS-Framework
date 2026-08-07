"""
Qt Designer Integration Guide for LCARS Framework
==================================================

╨п╨║ ╨▓╨╕╨║╨╛╤А╨╕╤Б╤В╨╛╨▓╤Г╨▓╨░╤В╨╕ Qt Designer ╨┤╨╗╤П ╤Б╤В╨▓╨╛╤А╨╡╨╜╨╜╤П UI ╨┤╨╗╤П PyQt6:

1. ╨Ч╨Р╨Я╨г╨б╨Ъ DESIGNER
   тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФА
   ╨Ч╨░╨┐╤Г╤Б╤В╤Ц╤В╤М ╤Д╨░╨╣╨╗: launch_designer.bat
   ╨Р╨▒╨╛: python -m pyqt6.tools.designer

2. ╨б╨в╨Т╨Ю╨а╨Х╨Э╨Э╨п ╨Э╨Ю╨Т╨Ш╨е ╨д╨Ю╨а╨Ь
   тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФА
   - ╨Т╤Ц╨┤╨║╤А╨╕╨╣╤В╨╡ Qt Designer
   - File тЖТ New тЖТ Dialog, Main Window, Widget (╨▓╨╕╨▒╨╡╤А╤Ц╤В╤М)
   - ╨б╨┐╤А╨╛╨╡╨║╤В╤Г╨╣╤В╨╡ ╤Д╨╛╤А╨╝╤Г ╨┐╨╡╤А╨╡╤В╤П╨│╤Г╨▓╨░╨╜╨╜╤П╨╝ ╨║╨╛╨╝╨┐╨╛╨╜╨╡╨╜╤В╤Ц╨▓
   - ╨б╤Г╨║╤Г╨┐╨╜╤Ц╤Б╤В╤М ╨║╨╛╨╝╨┐╨╛╨╜╨╡╨╜╤В╤Ц╨▓:
     * Buttons (QPushButton, QRadioButton, QCheckBox)
     * Input (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)
     * Display (QLabel, QTextEdit, QTableWidget)
     * Layout (Horizontal, Vertical, Grid, Form)
     * 3D (╨╝╨╛╨╢╨╜╨░ ╨▓╤Б╤В╨░╨▓╨╕╤В╨╕ QOpenGLWidget ╨┤╨╗╤П Vispy)

3. ╨Ч╨С╨Х╨а╨Х╨Ц╨Х╨Э╨Э╨п ╨д╨Ю╨а╨Ь
   тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФА
   ╨Ч╨▒╨╡╤А╤Ц╨│╨░╨╣╤В╨╡ ╤П╨║ .ui ╤Д╨░╨╣╨╗╨╕ ╨▓ ╨┐╨░╨┐╤Ж╤Ц: lcars/ui/forms/
   
   ╨Я╤А╨╕╨╝╨╡╤А╨╕:
   - detector_designer.ui (╨▓╨║╨╗╨░╨┤╨║╨░ ╨┤╨╗╤П ╨┤╨╕╨╖╨░╨╣╨╜╤Г ╨┤╨╡╤В╨╡╨║╤В╨╛╤А╨░)
   - simulation_params.ui (╨┐╨░╤А╨░╨╝╨╡╤В╤А╨╕ ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╤Ц╤Ч)
   - analysis_plots.ui (╨│╤А╨░╤Д╤Ц╨║╨╕ ╨░╨╜╨░╨╗╤Ц╨╖╤Г)

4. ╨Ъ╨Ю╨Э╨Т╨Х╨а╨в╨Р╨ж╨Ж╨п .UI ╨Т PYTHON ╨Ъ╨Ю╨Ф
   тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФА
   ╨Т╨╕╨║╨╛╨╜╨░╨╣╤В╨╡ ╨║╨╛╨╝╨░╨╜╨┤╤Г:
   
   pyuic6 -o lcars/ui/forms/detector_designer.py lcars/ui/forms/detector_designer.ui
   
   ╨Р╨▒╨╛ ╨▓╤Б╤Ц ╨▓╤Ц╨┤╤А╨░╨╖╤Г:
   
   for %f in (lcars/ui/forms/*.ui) do pyuic6 -o lcars/ui/forms/%~nf.py %f

5. ╨Т╨Ш╨Ъ╨Ю╨а╨Ш╨б╨в╨Р╨Э╨Э╨п ╨Т ╨Ъ╨Ю╨Ф╨Ж
   тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФА
   from lcars.ui.forms.detector_designer import Ui_Form
   from PyQt6.QtWidgets import QWidget
   
   class DetectorDesignerTab(QWidget):
       def __init__(self):
           super().__init__()
           self.ui = Ui_Form()
           self.ui.setupUi(self)
           self.connect_signals()

6. ╨Я╨а╨Ш╨Ъ╨Ы╨Р╨Ф╨Ш
   тФАтФАтФАтФАтФАтФАтФАтФА
   ╨Ф╨╕╨▓╤Ц╤В╤М╤Б╤П:
   - detector_designer_example.py
   - simulation_params_example.py

╨Ъ╨Ю╨а╨Ш╨б╨Э╨Ж ╨Я╨Ю╨б╨Ш╨Ы╨Р╨Э╨Э╨п
тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФА
- Qt Designer Manual: https://doc.qt.io/qt-6/qtdesigner-manual.html
- PyQt6 Docs: https://www.riverbankcomputing.com/static/Docs/PyQt6/
"""

import sys
from pathlib import Path

# ╨Ф╨╛╨┤╨░╤В╨╕ ╨┤╨╛ path ╨┤╨╗╤П ╤Ц╨╝╨┐╨╛╤А╤В╤Г
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print(__doc__)
