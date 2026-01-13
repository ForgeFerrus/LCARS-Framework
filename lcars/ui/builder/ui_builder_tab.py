"""
LCARS UI Builder Tab for Launcher
- Integrates the drag-n-drop UI builder as a QWidget for use in the main launcher tab interface.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from lcars.ui.builder.ui_builder import LCARSUIBuilder

class LCARSUIBuilderTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.builder = LCARSUIBuilder()
        layout.addWidget(self.builder.centralWidget())
        self.setLayout(layout)
