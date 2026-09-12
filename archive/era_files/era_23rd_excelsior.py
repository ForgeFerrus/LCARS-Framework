import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton)
from PyQt6.QtGui import QColor, QPalette, QPainter, QPen, QFont
from PyQt6.QtCore import Qt

class ExcelsiorPalette:
    def __init__(self):
        self.colors = {
            "red": "#FF0000",
            "amber": "#FFCC00",
            "green": "#009900",
            "blue": "#0066CC",
            "orange": "#FF9900",
            "black": "#000000",
            "border": "#FFCC00"
        }
    def get(self, name):
        return self.colors.get(name, "#FFFFFF")

class ExcelsiorButton(QFrame):
    def __init__(self, palette=None, color="amber", width=120, height=50):
        super().__init__()
        if palette is None:
            palette = ExcelsiorPalette()
        self.palette = palette
        self.color = color
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background: {palette.get(color)};
                border: 2px solid {palette.get('border')};
                border-radius: 10px;
            }}
        """)

class ExcelsiorLabel(QLabel):
    def __init__(self, text, color="#FFCC00", width=54, height=20):
        super().__init__(text)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 13px;
                font-weight: bold;
                padding: 2px 6px;
                background: transparent;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class ExcelsiorDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.excelsior_palette = ExcelsiorPalette()
        self.setWindowTitle("LCARS Excelsior/Late 23rd Demo")
        self.setGeometry(100, 100, 800, 500)
        
        # Set background
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(self.excelsior_palette.get("black")))
        self.setPalette(pal)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = ExcelsiorLabel("USS ENTERPRISE NCC-1701-B", color="#FFCC00", width=400, height=40)
        header.setStyleSheet(header.styleSheet() + "font-size: 20px;")
        
        # Status display
        status = ExcelsiorLabel("STANDBY", color="#00FF00", width=200, height=30)
        
        # Button row 1
        button_row1 = QHBoxLayout()
        buttons1 = [
            ("SENSORS", "amber"),
            ("NAVIGATION", "green"),
            ("ENGINEERING", "red"),
            ("SCIENCE", "blue")
        ]
        
        for text, color in buttons1:
            btn = ExcelsiorButton(self.excelsior_palette, color=color, width=120, height=50)
            btn_layout = QVBoxLayout(btn)
            btn_label = ExcelsiorLabel(text, color=color, width=120, height=20)
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
            btn = ExcelsiorButton(self.excelsior_palette, color=color, width=120, height=50)
            btn_layout = QVBoxLayout(btn)
            btn_label = ExcelsiorLabel(text, color=color, width=120, height=20)
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
    ui = ExcelsiorDemo()
    ui.show()
    
    # Run the application
    sys.exit(app.exec())