"""
LCARS Lock Screen - Federation 25th Century
Direct authentication screen for Federation 25th Century
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# Add project root
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color

def get_simple_font(size, weight="normal"):
    """Simple LCARS font"""
    weight_map = {"light": "200", "normal": "400", "bold": "700"}
    return f"""
        font-family: 'LCARSGTJ3', 'Antonio', 'Arial Black', sans-serif;
        font-size: {size}px;
        font-weight: {weight_map.get(weight, "400")};
        letter-spacing: 2px;
        text-transform: uppercase;
    """

class LockScreen25th(QMainWindow):
    """Federation 25th Century Lock Screen"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS OS - Federation 25th Century")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.colors = get_era_palette(LCARSEra.LCARS_25TH)
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(50, 100, 50, 100)
        layout.setSpacing(30)
        
        # Federation Header
        header = QLabel("◆ FEDERATION 25TH CENTURY")
        header.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {get_random_button_color(LCARSEra.LCARS_25TH)}, 
                    stop:1 {get_random_button_color(LCARSEra.LCARS_25TH)});
                color: #000;
                padding: 20px;
                border-radius: 15px;
                {get_simple_font(32, "bold")}
            }}
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Authentication Panel
        auth_panel = QFrame()
        auth_panel.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 20px;
                padding: 30px;
            }}
        """)
        
        auth_layout = QVBoxLayout(auth_panel)
        auth_layout.setSpacing(20)
        
        # Status
        status = QLabel("SYSTEM READY - AUTHENTICATION REQUIRED")
        status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                {get_simple_font(18, "normal")}
                padding: 10px;
            }}
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auth_layout.addWidget(status)
        
        # Password field
        password_input = QLineEdit()
        password_input.setPlaceholderText("ENTER AUTHORIZATION CODE")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 0.3);
                border: 2px solid {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 10px;
                padding: 15px;
                color: #FFFFFF;
                {get_simple_font(16, "normal")}
            }}
            QLineEdit:focus {{
                border: 2px solid #FFFFFF;
                background-color: rgba(0, 0, 0, 0.5);
            }}
        """)
        auth_layout.addWidget(password_input)
        
        # Enter button
        enter_btn = QPushButton("ENTER SYSTEM")
        enter_btn.setFixedSize(300, 60)
        enter_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {get_random_button_color(LCARSEra.LCARS_25TH)}, 
                    stop:1 {get_random_button_color(LCARSEra.LCARS_25TH)});
                color: #000;
                border: none;
                border-radius: 25px;
                {get_simple_font(16, "bold")}
            }}
            QPushButton:hover {{
                border: 2px solid #FFFFFF;
                box-shadow: 0 0 20px {get_random_button_color(LCARSEra.LCARS_25TH)};
            }}
        """)
        enter_btn.clicked.connect(self.enter_system)
        auth_layout.addWidget(enter_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(auth_panel)
        
        layout.addStretch()
        
        # Footer
        footer = QFrame()
        footer.setFixedHeight(40)
        footer.setStyleSheet(f"background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 5, 20, 5)
        
        time_label = QLabel("STARDATE: 56845.2")
        time_label.setStyleSheet(f"color: #000; {get_simple_font(12, 'bold')}")
        footer_layout.addWidget(time_label)
        
        footer_layout.addStretch()
        
        help_label = QLabel("F1: HELP | ESC: SHUTDOWN")
        help_label.setStyleSheet(f"color: #000; {get_simple_font(12, 'normal')}")
        footer_layout.addWidget(help_label)
        
        layout.addWidget(footer)
        
    def enter_system(self):
        """Go to desktop"""
        self.close()
        # TODO: Load desktop
        print("Entering Federation Desktop...")

def main():
    app = QApplication(sys.argv)
    
    # Direct to Federation 25th lock screen
    lock = LockScreen25th()
    lock.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
