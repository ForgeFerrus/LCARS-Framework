#!/usr/bin/env python3
"""Main LCARS Interface - Clean Design without Contours"""

# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient, QPen, QBrush


class WelcomePanel(QFrame):
    """Clean welcome panel with faction selection - no contours"""
    
    faction_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_welcome_ui()
        
    def setup_welcome_ui(self):
        self.setFixedSize(900, 700)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000011, stop:0.5 #000022, stop:1 #000011);
                border: none;
                border-radius: 0px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # Welcome title
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-size: 42px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select Faction")
        subtitle.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Faction buttons grid
        button_layout = QGridLayout()
        button_layout.setSpacing(30)
        
        # Starfleet
        starfleet_btn = QPushButton("STARFLEET")
        starfleet_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFCC66;
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 20px 30px;
                border: none;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FFD699;
            }
            QPushButton:pressed {
                background-color: #E6B85C;
            }
        """)
        starfleet_btn.clicked.connect(lambda: self.faction_selected.emit("STARFLEET"))
        button_layout.addWidget(starfleet_btn, 0, 0)
        
        # Klingon
        klingon_btn = QPushButton("KLINGON")
        klingon_btn.setStyleSheet("""
            QPushButton {
                background-color: #CC3333;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 20px 30px;
                border: none;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FF4444;
            }
            QPushButton:pressed {
                background-color: #AA2222;
            }
        """)
        klingon_btn.clicked.connect(lambda: self.faction_selected.emit("KLINGON"))
        button_layout.addWidget(klingon_btn, 0, 1)
        
        # Romulan
        romulan_btn = QPushButton("ROMULAN")
        romulan_btn.setStyleSheet("""
            QPushButton {
                background-color: #00CC66;
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 20px 30px;
                border: none;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #00FF88;
            }
            QPushButton:pressed {
                background-color: #00AA55;
            }
        """)
        romulan_btn.clicked.connect(lambda: self.faction_selected.emit("ROMULAN"))
        button_layout.addWidget(romulan_btn, 1, 0)
        
        # Cardassian
        cardassian_btn = QPushButton("CARDASSIAN")
        cardassian_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9933;
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 20px 30px;
                border: none;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FFB366;
            }
            QPushButton:pressed {
                background-color: #E68529;
            }
        """)
        cardassian_btn.clicked.connect(lambda: self.faction_selected.emit("CARDASSIAN"))
        button_layout.addWidget(cardassian_btn, 1, 1)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)


class MainLCARSInterface(QMainWindow):
    """Main LCARS Interface Window"""
    
    def __init__(self):
        super().__init__()
        self.setup_main_window()
        
    def setup_main_window(self):
        self.setWindowTitle("LCARS Framework")
        self.setGeometry(100, 100, 900, 700)
        
        # Set central widget with gradient background
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.3 #000011, stop:0.7 #000022, stop:1 #000000);
                border: none;
            }
        """)
        self.setCentralWidget(central_widget)
        
        # Create layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add welcome panel
        self.welcome_panel = WelcomePanel()
        self.welcome_panel.faction_selected.connect(self.launch_faction_interface)
        main_layout.addWidget(self.welcome_panel, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def launch_faction_interface(self, faction):
        """Launch selected faction interface"""
        # Clear welcome panel
        self.welcome_panel.hide()
        
        # Create faction interface
        faction_widget = QWidget()
        faction_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(faction_widget)
        
        # Title
        title = QLabel(f"{faction} INTERFACE")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.get_faction_color(faction)};
                font-size: 36px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Content area
        content = QLabel(f"{faction} system interface ready")
        content.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 18px;
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }
        """)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        # Back button
        back_btn = QPushButton("BACK TO MAIN MENU")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 10px 20px;
                border: none;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #888888;
            }
        """)
        back_btn.clicked.connect(self.show_welcome_panel)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        # Replace central widget
        self.setCentralWidget(faction_widget)
        
    def show_welcome_panel(self):
        """Show welcome panel again"""
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.3 #000011, stop:0.7 #000022, stop:1 #000000);
                border: none;
            }
        """)
        
        layout = QVBoxLayout(welcome_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        welcome_panel = WelcomePanel()
        welcome_panel.faction_selected.connect(self.launch_faction_interface)
        layout.addWidget(welcome_panel, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setCentralWidget(welcome_widget)
        
    def get_faction_color(self, faction):
        """Get faction color"""
        colors = {
            "STARFLEET": "#FFCC66",
            "KLINGON": "#CC3333", 
            "ROMULAN": "#00CC66",
            "CARDASSIAN": "#FF9933"
        }
        return colors.get(faction, "#FFFFFF")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main interface
    window = MainLCARSInterface()
    window.show()
    
    sys.exit(app.exec())
