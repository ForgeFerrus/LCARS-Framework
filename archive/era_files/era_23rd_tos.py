import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton)
from PyQt6.QtGui import QColor, QPalette, QPainter, QPen, QFont
from PyQt6.QtCore import Qt

class TOSPalette:
    def __init__(self):
        self.colors = {
            "red": "#FF0000",
            "orange": "#FF9900",
            "green": "#009900",
            "yellow": "#FFFF00",
            "black": "#000000",
            "border": "#FF9900"
        }
    def get(self, name):
        return self.colors.get(name, "#FFFFFF")

class TOSRectButton(QFrame):
    def __init__(self, palette=None, color="red", width=48, height=28):
        super().__init__()
        if palette is None:
            palette = TOSPalette()
        self.palette = palette
        self.color = color
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background: {palette.get(color)};
                border: 2px solid {palette.get('border')};
                border-radius: 4px;
            }}
        """)

class TOSLabel(QLabel):
    def __init__(self, text, color="#FF9900", width=48, height=20):
        super().__init__(text)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
                padding: 2px 6px;
                background: transparent;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class TOSDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.tos_palette = TOSPalette()
        self.setWindowTitle("LCARS TOS/23rd Century Demo")
        self.setGeometry(100, 100, 800, 500)
        
        # Set background
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(self.tos_palette.get("black")))
        self.setPalette(pal)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = TOSLabel("USS ENTERPRISE NCC-1701", color="#FF9900", width=400, height=40)
        header.setStyleSheet(header.styleSheet() + "font-size: 20px;")
        
        # Status display
        status = TOSLabel("STANDBY", color="#00FF00", width=200, height=30)
        
        # Button row 1
        button_row1 = QHBoxLayout()
        buttons1 = [
            ("SENSORS", "red"),
            ("NAVIGATION", "orange"),
            ("ENGINEERING", "red"),
            ("SCIENCE", "yellow")
        ]
        
        for text, color in buttons1:
            btn = TOSRectButton(self.tos_palette, color=color, width=120, height=50)
            btn_layout = QVBoxLayout(btn)
            btn_label = TOSLabel(text, color=color, width=120, height=20)
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
            btn = TOSRectButton(self.tos_palette, color=color, width=120, height=50)
            btn_layout = QVBoxLayout(btn)
            btn_label = TOSLabel(text, color=color, width=120, height=20)
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
    ui = TOSDemo()
    ui.show()
    
    # Run the application
    sys.exit(app.exec())