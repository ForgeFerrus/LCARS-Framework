"""
LCARS Widgets - Basic widget definitions
"""

from PyQt6.QtWidgets import QPushButton, QLabel, QFrame, QWidget
from PyQt6.QtCore import Qt

class LCARSButton(QPushButton):
    """Basic LCARS button"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: #FFCC66;
                color: #000000;
                border: 2px solid #FFAA33;
                border-radius: 25px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

class LCARSPanel(QFrame):
    """Basic LCARS panel"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setStyleSheet("""
            QFrame {
                background: #000000;
                border: 2px solid #FFCC66;
                border-radius: 15px;
                padding: 15px;
            }
        """)

class LCARSLabel(QLabel):
    """Basic LCARS label"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)

class LCARSConsole(QWidget):
    """Basic LCARS console"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background: #000000;
                border: 2px solid #FFCC66;
                border-radius: 10px;
                color: #00FF00;
                font-family: monospace;
                font-size: 12px;
            }
        """)