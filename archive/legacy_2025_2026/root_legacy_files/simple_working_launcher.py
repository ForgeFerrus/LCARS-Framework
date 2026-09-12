"""
LCARS Era Selector - Proper LCARS Style
Classic LCARS interface for era selection
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from lcars.themes.lcars_palette import get_era_palette, get_random_button_color, LCARSEra

class SimpleLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup proper LCARS style UI"""
        self.setWindowTitle("LCARS Framework")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # Use LCARS 24th century palette for launcher
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_era_palette(self.era)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: none;
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 24px;
                background: transparent;
                border: none;
            }}
            QPushButton {{
                color: #000000;
                text-align: center;
                padding: 20px 30px;
                border-radius: 20px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 24px;
                font-weight: bold;
                border: none;
                min-width: 250px;
                min-height: 80px;
            }}
            QPushButton:hover {{
                background-color: {get_random_button_color(self.era)};
            }}
        """)
        
        self.create_layouts()
        self.create_widgets()
        
    def create_layouts(self):
        """Create LCARS layout structure"""
        # Main layout
        self.main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        
        # Header area
        self.header_layout = QHBoxLayout()
        
        # Content area for buttons
        self.content_layout = QVBoxLayout()
        
        # Footer area
        self.footer_layout = QHBoxLayout()
        
    def create_widgets(self):
        """Create LCARS widgets"""
        # Create header with LCARS style
        self.create_header()
        
        # Create era buttons
        self.create_era_buttons()
        
        # Create footer
        self.create_footer()
        
    def create_header(self):
        """Create LCARS header"""
        header = QFrame()
        header.setFixedHeight(120)
        header_layout = QHBoxLayout()
        
        # Left corner element
        corner = QWidget()
        corner.setFixedWidth(200)
        corner.setStyleSheet(f"""
            background-color: {get_random_button_color(self.era)};
            border-top-right-radius: 40px;
            border-bottom-right-radius: 40px;
            border: none;
        """)
        header_layout.addWidget(corner)
        
        # Title
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors['text']};
            padding: 20px;
            border: none;
            background: transparent;
        """)
        header_layout.addWidget(title)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors['background']};
            padding: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background-color: {get_random_button_color(self.era)};
            border-radius: 10px;
        """)
        header_layout.addWidget(self.time_label)
        
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
        
        # Update time
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
    def create_era_buttons(self):
        """Create era selection buttons"""
        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)
        
        # Era information
        eras = [
            ("22nd Century", "PCARS", self.launch_22nd),
            ("23rd Century", "LCARS", self.launch_23rd),
            ("24th Century", "LCARS", self.launch_24th),
            ("25th Century", "LCARS", self.launch_25th)
        ]
        
        for era_name, system, callback in eras:
            btn = QPushButton(f"{era_name}\n{system}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {get_random_button_color(self.era)};
                    color: {self.colors['background']};
                }}
            """)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        
        button_container.setLayout(button_layout)
        self.main_layout.addWidget(button_container)
        
    def create_footer(self):
        """Create LCARS footer"""
        footer = QFrame()
        footer.setFixedHeight(60)
        footer_layout = QHBoxLayout()
        
        status_label = QLabel("SYSTEM READY")
        status_label.setStyleSheet(f"color: {get_random_button_color(self.era)};")
        footer_layout.addWidget(status_label)
        
        footer_layout.addStretch()
        
        exit_btn = QPushButton("EXIT")
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color(self.era)};
                color: {self.colors['background']};
                min-width: 150px;
                min-height: 40px;
            }}
        """)
        exit_btn.clicked.connect(self.close)
        footer_layout.addWidget(exit_btn)
        
        footer.setLayout(footer_layout)
        self.main_layout.addWidget(footer)
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
    def launch_22nd(self):
        """Launch 22nd century interface"""
        
        try:
            from archive.era_files.PCARS_22nd import PCARS22ndCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            window = PCARS22ndCentury(root_path, selector=self)
            window.show()
        except Exception as e:
            print(f"Error launching 22nd century: {e}")
            
    def launch_23rd(self):
        """Launch 23rd century interface"""
        try:
            from archive.era_files.LCARS_23rd import LCARS23rdCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            window = LCARS23rdCentury(root_path, selector=self)
            window.show()
        except Exception as e:
            print(f"Error launching 23rd century: {e}")
            
    def launch_24th(self):
        """Launch 24th century interface"""
        try:
            from archive.era_files.LCARS_24th import LCARS24thCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            window = LCARS24thCentury(root_path, selector=self)
            window.show()
        except Exception as e:
            print(f"Error launching 24th century: {e}")
            
    def launch_25th(self):
        """Launch 25th century interface"""
        try:
            from archive.era_files.LCARS_25th import LCARS25thCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            window = LCARS25thCentury(root_path, selector=self)
            window.show()
        except Exception as e:
            print(f"Error launching 25th century: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = SimpleLauncher()
    launcher.show()
    sys.exit(app.exec())
        
    def create_era_buttons(self, layout):
        """Create era selection buttons"""
        eras = [
            ("22nd Century", self.launch_22nd),
            ("23rd Century", self.launch_23rd),
            ("24th Century", self.launch_24th),
            ("Klingon Empire", self.launch_klingon),
            ("Romulan Star Empire", self.launch_romulan),
            ("Cardassian Union", self.launch_cardassian),
            ("Project Explorer", self.launch_explorer)
        ]
        
        for era_name, callback in eras:
            btn = QPushButton(era_name)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
            
    def launch_22nd(self):
        """Launch 22nd century interface"""
        try:
            from archive.era_files.PCARS_22nd import PCARS22ndCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            interface = PCARS22ndCentury(root_path, selector=self)
            interface.show()
        except Exception as e:
            self.status_label.setText(f"Error launching 22nd Century: {str(e)}")
            
    def launch_23rd(self):
        """Launch 23rd century interface"""
        try:
            from archive.era_files.LCARS_23rd import LCARS23rdCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            interface = LCARS23rdCentury(root_path, selector=self)
            interface.show()
        except Exception as e:
            self.status_label.setText(f"Error launching 23rd Century: {str(e)}")
            
    def launch_24th(self):
        """Launch 24th century interface"""
        try:
            from archive.era_files.LCARS_24th import LCARS24thCentury
            root_path = Path(__file__).parent.parent
            self.hide()
            interface = LCARS24thCentury(root_path, selector=self)
            interface.show()
        except Exception as e:
            self.status_label.setText(f"Error launching 24th Century: {str(e)}")
            
    def launch_klingon(self):
        """Launch Klingon interface"""
        try:
            from archive.era_files.Klingon_system import KlingonInterface
            root_path = Path(__file__).parent.parent
            self.hide()
            interface = KlingonInterface(root_path, selector=self)
            interface.show()
        except Exception as e:
            self.status_label.setText(f"Error launching Klingon: {str(e)}")
            
    def launch_romulan(self):
        """Launch Romulan interface"""
        try:
            from archive.era_files.Romulan_interface import RomulanInterface
            root_path = Path(__file__).parent.parent
            self.hide()
            interface = RomulanInterface(root_path, selector=self)
            interface.show()
        except Exception as e:
            self.status_label.setText(f"Error launching Romulan: {str(e)}")
            
    def launch_cardassian(self):
        """Launch Cardassian interface"""
        try:
            from archive.era_files.Cardassian_interface import CardassianInterface
            root_path = Path(__file__).parent.parent
            self.hide()
            interface = CardassianInterface(root_path, selector=self)
            interface.show()
        except Exception as e:
            self.status_label.setText(f"Error launching Cardassian: {str(e)}")
            
    def launch_explorer(self):
        """Launch project explorer"""
        try:
            from project_explorer import ProjectExplorer
            self.hide()
            explorer = ProjectExplorer()
            explorer.show()
        except Exception as e:
            self.status_label.setText(f"Error launching Explorer: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle("Fusion")
    
    launcher = SimpleLauncher()
    launcher.show()
    
    sys.exit(app.exec())