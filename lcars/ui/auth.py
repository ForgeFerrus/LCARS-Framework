"""
LCARS Authentication System
Login/Access control for LCARS Desktop
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color


class LCARSButton(QPushButton):
    """LCARS styled button"""
    def __init__(self, text, era, button_index=0, parent=None):
        super().__init__(text, parent)
        self.era = era
        self.button_index = button_index
        self.base_color = get_random_button_color(era)
        
        self.setFixedHeight(50)
        self.update_style()
        
        # Color cycling
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 200, self.color_timer.start)
        self.color_timer.setInterval(3000)
    
    def cycle_color(self):
        self.base_color = get_random_button_color(self.era)
        self.update_style()
    
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: #000;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.brighten(self.base_color)};
            }}
        """)
    
    @staticmethod
    def brighten(color):
        from PyQt6.QtGui import QColor
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()


class LCARSAuthWindow(QMainWindow):
    """LCARS Authentication Window"""
    authentication_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Authentication")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        self.login_attempts = 0
        self.max_attempts = 3
        
        self.setup_ui()
        self.showFullScreen()
    
    def setup_ui(self):
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background-color: {self.colors['button_colors'][0]};")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(40, 15, 40, 15)
        
        title = QLabel("◢ FEDERATION LCARS ACCESS CONTROL")
        title.setStyleSheet("color: #000; font-size: 32px; font-weight: bold;")
        h_layout.addWidget(title)
        
        h_layout.addStretch()
        
        layout.addWidget(header)
        
        # Center content
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(50, 50, 50, 50)
        center_layout.setSpacing(30)
        
        # Login form
        login_frame = QFrame()
        login_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['button_colors'][1]};
                border-radius: 25px;
            }}
        """)
        
        login_layout = QVBoxLayout(login_frame)
        login_layout.setContentsMargins(40, 40, 40, 40)
        login_layout.setSpacing(25)
        
        # Title
        auth_title = QLabel("◢ AUTHENTICATION REQUIRED")
        auth_title.setStyleSheet(f"color: {self.colors['button_colors'][1]}; font-size: 24px; font-weight: bold; background: transparent;")
        auth_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(auth_title)
        
        # Username
        user_label = QLabel("USERNAME:")
        user_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold; background: transparent;")
        login_layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.3);
                color: #000;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QLineEdit:focus {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        self.username_input.setPlaceholderText("Enter username")
        login_layout.addWidget(self.username_input)
        
        # Password
        pass_label = QLabel("ACCESS CODE:")
        pass_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold; background: transparent;")
        login_layout.addWidget(pass_label)
        
        self.password_input = QLineEdit()
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.3);
                color: #000;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QLineEdit:focus {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter access code")
        self.password_input.returnPressed.connect(self.attempt_login)
        login_layout.addWidget(self.password_input)
        
        # Login button
        login_btn = LCARSButton("◢ AUTHENTICATE", self.current_era, 5)
        login_btn.setFixedHeight(60)
        login_btn.clicked.connect(self.attempt_login)
        login_layout.addWidget(login_btn)
        
        # Guest access
        guest_btn = LCARSButton("◢ GUEST ACCESS", self.current_era, 6)
        guest_btn.setFixedHeight(50)
        guest_btn.clicked.connect(self.guest_access)
        login_layout.addWidget(guest_btn)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {self.colors['alert_colors'][0]}; font-size: 14px; font-weight: bold; background: transparent;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(self.status_label)
        
        center_layout.addWidget(login_frame)
        center_layout.addStretch()
        
        layout.addWidget(center, 1)
        
        # Footer
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"background-color: {self.colors['button_colors'][2]};")
        
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(40, 10, 40, 10)
        
        help_text = QLabel("ENTER: Authenticate | ESC: Cancel | F1: Help")
        help_text.setStyleSheet("color: #000; font-size: 14px; font-weight: bold;")
        f_layout.addWidget(help_text)
        
        f_layout.addStretch()
        
        layout.addWidget(footer)
    
    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("Please enter username and access code")
            return
        
        # Simple authentication (in real system, use proper auth)
        if username.lower() == "admin" and password == "admin":
            self.authentication_success.emit()
            self.close()
        else:
            self.login_attempts += 1
            remaining = self.max_attempts - self.login_attempts
            
            if remaining <= 0:
                self.show_error("ACCESS DENIED - Too many attempts")
                QTimer.singleShot(2000, self.close)
            else:
                self.show_error(f"Invalid credentials - {remaining} attempts remaining")
                self.password_input.clear()
    
    def guest_access(self):
        """Allow guest access"""
        self.authentication_success.emit()
        self.close()
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {self.colors['alert_colors'][1]}; font-size: 14px; font-weight: bold; background: transparent;")
        
        # Clear error after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F1:
            QMessageBox.information(self, "Help", 
                "Default credentials:\nUsername: admin\nPassword: admin\n\nOr use Guest Access for limited functionality")


def main():
    app = QApplication(sys.argv)
    auth = LCARSAuthWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
