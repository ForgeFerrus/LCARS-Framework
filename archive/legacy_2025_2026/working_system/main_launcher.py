"""
LCARS Working System - Main Launcher
Integrated Era Selection and Desktop Launch
Everything that actually works!
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import LCARSEra, get_era_palette

class WorkingSystemLauncher(QMainWindow):
    """Main launcher for all working LCARS systems"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Working System - Select Era")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup main selection interface"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000008, stop:1 #001122);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("LCARS WORKING SYSTEM")
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #00CCFF;
            text-align: center;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select Era Interface")
        subtitle.setStyleSheet("""
            font-size: 24px;
            color: #66DDFF;
            text-align: center;
            padding: 10px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Working era buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(20)
        
        # 25th Century - WORKS
        btn_25th = self.create_era_button("25TH CENTURY - HOLOGRAPHIC FEDERATION", "#00CCFF")
        btn_25th.clicked.connect(self.launch_25th_century)
        button_layout.addWidget(btn_25th)
        
        # 22nd Century - WORKS  
        btn_22nd = self.create_era_button("22ND CENTURY - NX-01 ENTERPRISE", "#FF6600")
        btn_22nd.clicked.connect(self.launch_22nd_century)
        button_layout.addWidget(btn_22nd)
        
        # 24th Century - WORKS
        btn_24th = self.create_era_button("24TH CENTURY - CLASSIC LCARS", "#FFCC00")
        btn_24th.clicked.connect(self.launch_24th_century)
        button_layout.addWidget(btn_24th)
        
        # 29th Century - WORKS
        btn_29th = self.create_era_button("29TH CENTURY - USS RELATIVITY", "#CC66FF")
        btn_29th.clicked.connect(self.launch_29th_century)
        button_layout.addWidget(btn_29th)
        
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        # Exit button
        exit_btn = self.create_era_button("EXIT SYSTEM", "#FF3366")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def create_era_button(self, text, color):
        """Create styled era button"""
        btn = QPushButton(text)
        btn.setMinimumSize(600, 80)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {QColor(color).darker(150).name()});
                color: #000000;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {QColor(color).lighter(120).name()}, stop:1 {color});
                border: 2px solid #FFFFFF;
            }}
            QPushButton:pressed {{
                background: {QColor(color).darker(130).name()};
            }}
        """)
        return btn
        
    def launch_25th_century(self):
        """Launch 25th Century Holographic Interface"""
        print("🚀 Launching 25th Century Holographic Federation Interface...")
        try:
            from working_system.era_25th import Federation25thLogin
            self.hide()
            self.era_interface = Federation25thLogin()
            self.era_interface.authentication_success.connect(self.return_to_launcher)
            self.era_interface.show()
        except Exception as e:
            print(f"Error launching 25th century: {e}")
            
    def launch_22nd_century(self):
        """Launch 22nd Century NX-01 Interface"""
        print("🚀 Launching 22nd Century NX-01 Enterprise Interface...")
        try:
            from working_system.era_22nd import Federation22ndLogin
            self.hide()
            self.era_interface = Federation22ndLogin()
            self.era_interface.authentication_success.connect(self.return_to_launcher)
            self.era_interface.show()
        except Exception as e:
            print(f"Error launching 22nd century: {e}")
            
    def launch_24th_century(self):
        """Launch 24th Century Classic LCARS"""
        print("🚀 Launching 24th Century Classic LCARS Interface...")
        try:
            from working_system.era_24th import Federation24thLogin
            self.hide()
            self.era_interface = Federation24thLogin()
            self.era_interface.authentication_success.connect(self.return_to_launcher)
            self.era_interface.show()
        except Exception as e:
            print(f"Error launching 24th century: {e}")
            
    def launch_29th_century(self):
        """Launch 29th Century USS Relativity TCARS"""
        print("🚀 Launching 29th Century USS Relativity Interface...")
        try:
            from working_system.era_29th import Federation29thLogin
            self.hide()
            self.era_interface = Federation29thLogin()
            self.era_interface.authentication_success.connect(self.return_to_launcher)
            self.era_interface.show()
        except Exception as e:
            print(f"Error launching 29th century: {e}")
            
    def return_to_launcher(self):
        """Return to main launcher"""
        self.era_interface = None
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = WorkingSystemLauncher()
    launcher.show()
    sys.exit(app.exec())