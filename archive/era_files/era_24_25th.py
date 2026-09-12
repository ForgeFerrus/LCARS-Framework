import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton)
from PyQt6.QtGui import QColor, QPalette, QPainter, QPen, QFont
from PyQt6.QtCore import Qt

# 24th/25th century LCARS palette
class LCARSPalette:
    def __init__(self):
        self.colors = {
            "orange": "#FF9900",
            "peach": "#FFCC99",
            "cyan": "#33FFFF",
            "purple": "#CC66FF",
            "yellow": "#FFFF66",
            "red": "#FF6666",
            "blue": "#3399FF",
            "gray": "#CCCCCC",
            "black": "#000000",
            "border": "#FF9900"
        }
    def get(self, name):
        return self.colors.get(name, "#FFFFFF")

class LCARSButton(QFrame):
    def __init__(self, palette=None, color="orange", width=120, height=50):
        super().__init__()
        if palette is None:
            palette = LCARSPalette()
        self.palette = palette
        self.color = color
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background: {palette.get(color)};
                border: 2px solid {palette.get('border')};
                border-radius: 16px;
            }}
        """)

class LCARSLabel(QLabel):
    def __init__(self, text, color="#FF9900", width=120, height=30):
        super().__init__(text)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15px;
                font-weight: bold;
                padding: 2px 6px;
                background: transparent;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class LCARSDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.lcars_palette = LCARSPalette()
        self.setWindowTitle("LCARS 24th/25th Century Demo")
        self.setGeometry(100, 100, 800, 500)
        
        # Set background
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(self.lcars_palette.get("black")))
        self.setPalette(pal)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = LCARSLabel("USS ENTERPRISE NCC-1701-D", color="#FF9900", width=400, height=40)
        header.setStyleSheet(header.styleSheet() + "font-size: 20px;")
        
        # Status display
        status = LCARSLabel("STANDBY", color="#33FFFF", width=200, height=30)
        
        # Button row 1
        button_row1 = QHBoxLayout()
        buttons1 = [
            ("SENSORS", "orange"),
            ("NAVIGATION", "cyan"),
            ("ENGINEERING", "purple"),
            ("SCIENCE", "blue")
        ]
        
        for text, color in buttons1:
            btn = LCARSButton(self.lcars_palette, color=color, width=120, height=50)
            btn_layout = QVBoxLayout(btn)
            btn_label = LCARSLabel(text, color=color, width=120, height=20)
            btn_layout.addWidget(btn_label)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_row1.addWidget(btn)
        
        button_row1.addStretch()
        
        # Button row 2
        button_row2 = QHBoxLayout()
        buttons2 = [
            ("SHIELDS", "red"),
            ("PHASERS", "orange"),
            ("TORPEDOES", "red"),
            ("RED ALERT", "red")
        ]
        
        for text, color in buttons2:
            btn = LCARSButton(self.lcars_palette, color=color, width=120, height=50)
            btn_layout = QVBoxLayout(btn)
            btn_label = LCARSLabel(text, color=color, width=120, height=20)
            btn_layout.addWidget(btn_label)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_row2.addWidget(btn)
        
        button_row2.addStretch()
        
        # Add all to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(status)
        main_layout.addLayout(button_row1)
        main_layout.addLayout(button_row2)
        main_layout.addStretch()
        
        # Set a minimum size for the window
        self.setMinimumSize(800, 500)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide styles
    app.setStyle('Fusion')
    
    # Set default font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Create and show the main window
    ui = LCARSDemo()
    ui.show()
    
    # Run the application
    sys.exit(app.exec())