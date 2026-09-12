"""
Federation 22nd Century Login Screen with Boot Sequence
Based on NX-01 Enterprise Master Systems Display
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class NXButton(QPushButton):
    """NX-style rectangular button with corner indicator"""
    def __init__(self, text, color="#269EEE", parent=None):
        super().__init__(text, parent)
        self.btn_color = color
        self.setMinimumHeight(35)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Hover effect
        bg_color = QColor(self.btn_color)
        if self.underMouse():
            bg_color = bg_color.lighter(120)
        if self.isDown():
            bg_color = bg_color.darker(120)
            
        # Draw main button
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawRect(rect)
        
        # Draw text
        painter.setPen(QColor("#000000"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class Federation22ndLogin(QMainWindow):
    """22nd Century Federation Login Screen - NX-01 Style with Boot Sequence"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Boot sequence state
        self.boot_stage = 0
        self.boot_complete = False
        
        # Boot messages for NX-01
        self.boot_messages = [
            "INITIALIZING NX-01 SYSTEMS...",
            "LOADING DUOTRONIC COMPUTER CORE...", 
            "ACTIVATING PLASMA MANIFOLDS...",
            "SYNCHRONIZING WARP DRIVE SYSTEMS...",
            "ENABLING UNIVERSAL TRANSLATOR...",
            "LOADING TACTICAL SYSTEMS...",
            "CONNECTING TO STARFLEET COMMAND...",
            "NX-01 ENTERPRISE - SYSTEMS READY"
        ]
        
        self.setup_nx_interface()
        self.start_boot_sequence()
        
        # Color update timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(3000)  # Every 3 seconds
        
    def setup_nx_interface(self):
        """Setup NX-01 Enterprise interface"""
        self.setWindowTitle("NX-01 Enterprise Master Systems Display")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # NX-01 color scheme
        self.colors = {
            'background': '#1A1A1A',    # Dark grey
            'text': '#E0E0E0',          # Light grey
            'primary': '#269EEE',       # NX Blue
            'secondary': '#4A90E2',     # Lighter blue
            'accent': '#FF6B35',        # Orange accent
            'panel': '#2A2A2A',         # Panel grey
        }
        
        # Apply NX-01 styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # NX-01 Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("NX-01 ENTERPRISE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {self.colors['primary']};
            padding: 15px;
        """)
        
        subtitle_label = QLabel("STARFLEET COMMAND • 22ND CENTURY")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['secondary']};
            padding: 10px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)
        
        # Boot message display
        self.boot_message = QLabel(self.boot_messages[0])
        self.boot_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.boot_message.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors['accent']};
            padding: 25px;
            background-color: {self.colors['panel']};
            border: 2px solid {self.colors['primary']};
            border-radius: 8px;
            margin: 15px;
        """)
        main_layout.addWidget(self.boot_message)
        
        # Progress dots
        self.progress_container = QWidget()
        progress_layout = QHBoxLayout(self.progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setSpacing(15)
        
        self.progress_dots = []
        for i in range(len(self.boot_messages)):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {self.colors['panel']}; font-size: 20px; padding: 8px;")
            progress_layout.addWidget(dot)
            self.progress_dots.append(dot)
        
        main_layout.addWidget(self.progress_container)
        
        # Login interface (hidden initially)
        self.login_interface = self.create_login_interface()
        self.login_interface.hide()
        main_layout.addWidget(self.login_interface)
        
        main_layout.addStretch()
    
    def create_login_interface(self):
        """Create the actual login interface"""
        login_frame = QFrame()
        login_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                border-radius: 8px;
                margin: 15px;
                padding: 30px;
            }}
        """)
        
        login_layout = QVBoxLayout(login_frame)
        login_layout.setSpacing(20)
        
        access_label = QLabel("SELECT SYSTEM ACCESS")
        access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        access_label.setStyleSheet(f"""
            font-size: 22px;
            color: {self.colors['primary']};
            font-weight: bold;
            padding: 15px;
        """)
        login_layout.addWidget(access_label)
        
        # System access buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(15)
        
        systems = [
            ("COMPUTER CORE", self.colors['primary']),
            ("DATA BANK", self.colors['secondary']),
            ("COMMUNICATION", self.colors['accent']),
            ("SECURITY", "#60A060")
        ]
        
        for system, color in systems:
            btn = NXButton(system, color)
            btn.setMinimumHeight(60)
            btn.clicked.connect(self.authenticate)
            button_layout.addWidget(btn)
            
        login_layout.addWidget(button_container)
        return login_frame
    
    def start_boot_sequence(self):
        """Start NX-01 boot sequence"""
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.advance_boot)
        self.boot_timer.start(1200)  # 1.2 seconds per stage
        
    def advance_boot(self):
        """Advance boot sequence"""
        if self.boot_stage < len(self.boot_messages):
            # Update progress dot
            if self.boot_stage < len(self.progress_dots):
                self.progress_dots[self.boot_stage].setStyleSheet(f"""
                    color: {self.colors['primary']};
                    font-size: 20px;
                    padding: 8px;
                """)
            
            # Update boot message
            self.boot_message.setText(self.boot_messages[self.boot_stage])
            self.boot_stage += 1
        else:
            # Boot complete - show login interface
            self.boot_timer.stop()
            self.boot_complete = True
            self.boot_message.setText("SYSTEM READY - SELECT ACCESS LEVEL")
            self.boot_message.setStyleSheet(f"""
                font-size: 24px;
                color: {self.colors['primary']};
                padding: 25px;
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['accent']};
                border-radius: 8px;
                margin: 15px;
                font-weight: bold;
            """)
            self.login_interface.show()
    
    def authenticate(self):
        """Handle authentication"""
        if not self.boot_complete:
            return
            
        print("✅ NX-01 authentication successful!")
        QTimer.singleShot(1000, self.launch_nx_desktop)
    
    def launch_nx_desktop(self):
        """Launch NX-01 desktop"""
        print("🚀 Launching NX-01 Desktop...")
        if True:
            from .desktop import NX01Desktop
            self.desktop = NX01Desktop()
            self.desktop.authentication_success.connect(self.on_desktop_logout)
            self.hide()
            self.desktop.show()
        if False: # Removed except block
            print("⚠️ NX-01 Desktop not available - returning to launcher")
            self.authentication_success.emit()
            self.close()
    
    def on_desktop_logout(self):
        """Handle desktop logout"""
        self.desktop = None
        self.authentication_success.emit()  # Signal back to launcher
        self.close()
    
    def update_colors(self):
        """Update NX-01 colors for dynamic effect"""
        import random
        
        # Subtle color variations for NX-01 theme
        blue_variants = ["#269EEE", "#2B87CC", "#3294FF", "#1E7DB8"]
        orange_variants = ["#FF6B35", "#FF7F50", "#FF8C42", "#E55A2B"]
        
        if not self.boot_complete:
            # During boot, pulse the accent color
            new_accent = random.choice(orange_variants)
            self.boot_message.setStyleSheet(self.boot_message.styleSheet().replace(
                self.colors['accent'], new_accent
            ))
            self.colors['accent'] = new_accent

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation22ndLogin()
    login.show()
    sys.exit(app.exec())
        
    def setup_nx_interface(self):
        """Setup NX-01 Enterprise interface"""
        self.setWindowTitle("NX-01 Enterprise Master Systems Display")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # NX-01 color scheme
        self.colors = {
            'background': '#1A1A1A',    # Dark grey
            'text': '#E0E0E0',          # Light grey
            'primary': '#269EEE',       # NX Blue
            'secondary': '#4A90E2',     # Lighter blue
            'accent': '#FF6B35',        # Orange accent
            'panel': '#2A2A2A',         # Panel grey
        }
        
        # Apply NX-01 styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                padding: 8px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # NX-01 Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                border-radius: 5px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("NX-01 ENTERPRISE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {self.colors['primary']};
            padding: 15px;
        """)
        
        subtitle_label = QLabel("STARFLEET COMMAND AUTHORIZATION")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 18px;
            color: {self.colors['secondary']};
            padding: 5px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)
        
        # Boot message display
        self.boot_message = QLabel(self.boot_messages[0])
        self.boot_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.boot_message.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['accent']};
            padding: 20px;
            background-color: {self.colors['panel']};
            border: 1px solid {self.colors['primary']};
            border-radius: 5px;
            margin: 10px;
        """)
        main_layout.addWidget(self.boot_message)
        
        # Progress dots
        self.progress_container = QWidget()
        progress_layout = QHBoxLayout(self.progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_dots = []
        for i in range(len(self.boot_messages)):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {self.colors['panel']}; font-size: 16px; padding: 5px;")
            progress_layout.addWidget(dot)
            self.progress_dots.append(dot)
        
        main_layout.addWidget(self.progress_container)
        
        # Login interface (hidden initially)
        self.login_interface = self.create_login_interface()
        self.login_interface.hide()
        main_layout.addWidget(self.login_interface)
    
    def create_login_interface(self):
        """Create the actual login interface"""
        login_frame = QFrame()
        login_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                border-radius: 5px;
                margin: 10px;
            }}
        """)
        
        login_layout = QVBoxLayout(login_frame)
        
        # System access buttons
        systems = [
            ("COMPUTER CORE", self.colors['primary']),
            ("DATA BANK", self.colors['secondary']),
            ("COMMUNICATION", self.colors['accent']),
            ("SECURITY", "#60A060")
        ]
        
        for system, color in systems:
            btn = NXButton(system, color)
            btn.setMinimumHeight(50)
            btn.clicked.connect(self.authenticate)
            login_layout.addWidget(btn)
            
        return login_frame
    
    def start_boot_sequence(self):
        """Start NX-01 boot sequence"""
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.advance_boot)
        self.boot_timer.start(1000)  # 1 second per stage
        
    def advance_boot(self):
        """Advance boot sequence"""
        if self.boot_stage < len(self.boot_messages):
            # Update progress dot
            if self.boot_stage < len(self.progress_dots):
                self.progress_dots[self.boot_stage].setStyleSheet(f"""
                    color: {self.colors['primary']};
                    font-size: 16px;
                    padding: 5px;
                """)
            
            # Update boot message
            self.boot_message.setText(self.boot_messages[self.boot_stage])
            self.boot_stage += 1
        else:
            # Boot complete - show login interface
            self.boot_timer.stop()
            self.boot_complete = True
            self.boot_message.setText("SYSTEM READY - SELECT ACCESS LEVEL")
            self.login_interface.show()
    
    def authenticate(self):
        """Handle authentication"""
        if not self.boot_complete:
            return
            
        print("✅ NX-01 authentication successful!")
        QTimer.singleShot(1000, self.launch_nx_desktop)
        self.auth_field.setPlaceholderText("Enter Starfleet authorization...")
        self.auth_field.setFixedHeight(40)
        
        # NX-style buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        
        self.nx_buttons = []
        nx_commands = [
            ("MAIN SYSTEMS", "#269EEE"),
            ("NAVIGATION", "#4A90E2"),
            ("ENGINEERING", "#FF6B35"),
            ("COMMAND AUTH", "#7B68EE")
        ]
        
        for text, color in nx_commands:
            btn = NXButton(text, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(200, 50)
            self.nx_buttons.append(btn)
            button_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_field)
        auth_layout.addWidget(button_frame)
        
        main_layout.addWidget(header_frame)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
    def update_colors(self):
        """Update NX-01 button colors"""
        nx_colors = ["#269EEE", "#4A90E2", "#FF6B35", "#7B68EE", "#20B2AA", "#FF69B4"]
        import random
        
        for btn in self.nx_buttons:
            btn.btn_color = random.choice(nx_colors)
            btn.update()
            
    def authenticate(self):
        """Handle authentication and launch NX-01 Desktop"""
        print("✅ NX-01 Enterprise authentication successful!")
        
        # Launch NX-01 Desktop
        from .desktop import NX01Desktop
        self.desktop = NX01Desktop()
        self.desktop.authentication_success.connect(self.on_desktop_logout)
        
        # Hide login and show desktop
        self.hide()
        self.desktop.show()
        
    def on_desktop_logout(self):
        """Handle desktop logout"""
        print("🚪 Returned from NX-01 Desktop")
        self.desktop.close()
        self.authentication_success.emit()  # Signal back to boot system

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation22ndLogin()
    login.show()
    sys.exit(app.exec())
