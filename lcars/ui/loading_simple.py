from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class LCARSLoadingScreen(QWidget):
    loading_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Loading text
        self.loading_label = QLabel("LCARS SYSTEM LOADING...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-family: 'Arial', sans-serif;
                font-size: 24px;
                font-weight: bold;
                text-transform: uppercase;
            }
        """)
        
        layout.addWidget(self.loading_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #000000;")
        
        # Full screen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
