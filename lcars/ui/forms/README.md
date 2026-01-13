"""
Qt Designer Integration Guide for LCARS Framework
==================================================

Як використовувати Qt Designer для створення UI для PyQt6:

1. ЗАПУСК DESIGNER
   ───────────────
   Запустіть файл: launch_designer.bat
   Або: python -m pyqt6.tools.designer

2. СТВОРЕННЯ НОВИХ ФОРМ
   ────────────────────
   - Відкрийте Qt Designer
   - File → New → Dialog, Main Window, Widget (виберіть)
   - Спроектуйте форму перетягуванням компонентів
   - Сукупність компонентів:
     * Buttons (QPushButton, QRadioButton, QCheckBox)
     * Input (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)
     * Display (QLabel, QTextEdit, QTableWidget)
     * Layout (Horizontal, Vertical, Grid, Form)
     * 3D (можна вставити QOpenGLWidget для Vispy)

3. ЗБЕРЕЖЕННЯ ФОРМ
   ───────────────
   Зберігайте як .ui файли в папці: lcars/ui/forms/
   
   Примери:
   - detector_designer.ui (вкладка для дизайну детектора)
   - simulation_params.ui (параметри симуляції)
   - analysis_plots.ui (графіки аналізу)

4. КОНВЕРТАЦІЯ .UI В PYTHON КОД
   ────────────────────────────
   Виконайте команду:
   
   pyuic6 -o lcars/ui/forms/detector_designer.py lcars/ui/forms/detector_designer.ui
   
   Або всі відразу:
   
   for %f in (lcars/ui/forms/*.ui) do pyuic6 -o lcars/ui/forms/%~nf.py %f

5. ВИКОРИСТАННЯ В КОДІ
   ───────────────────
   from lcars.ui.forms.detector_designer import Ui_Form
   from PyQt6.QtWidgets import QWidget
   
   class DetectorDesignerTab(QWidget):
       def __init__(self):
           super().__init__()
           self.ui = Ui_Form()
           self.ui.setupUi(self)
           self.connect_signals()

6. ПРИКЛАДИ
   ────────
   Дивіться:
   - detector_designer_example.py
   - simulation_params_example.py

КОРИСНІ ПОСИЛАННЯ
─────────────────
- Qt Designer Manual: https://doc.qt.io/qt-6/qtdesigner-manual.html
- PyQt6 Docs: https://www.riverbankcomputing.com/static/Docs/PyQt6/
"""

import sys
from pathlib import Path

# Додати до path для імпорту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print(__doc__)
