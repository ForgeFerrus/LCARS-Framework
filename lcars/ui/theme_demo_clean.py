"""
LCARS Theme Demo - Clean Implementation

Чиста демонстрація LCARS тем з правильною архітектурою.
Використовує новий devtools.theme_editor для редагування.
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
# Titanium Bridge Migration: from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_palette_by_name
from devtools.theme_editor import LCARSThemeEditor

class LCARSThemeDemo(QMainWindow):
    """Clean LCARS Theme Demo"""
    
    def __init__(self):
        super().__init__()
        self.current_era = LCARSEra.LCARS_25TH
        self.current_palette = get_era_palette(self.current_era)
        self.theme_editor = None
        self.setup_ui()
        self.apply_theme()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
    
    def setup_ui(self):
        """Setup clean UI"""
        self.setWindowTitle('LCARS Theme Demo - Clean Version')
        self.setMinimumSize(1200, 800)
        
        # Remove window frame for LCARS look
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with era selector
        self.create_header(main_layout)
        
        # Main content area
        self.create_content_area(main_layout)
        
        # Footer with controls
        self.create_footer(main_layout)
    
    def create_header(self, parent_layout):
        """Create LCARS header"""
        header = QFrame()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Title
        self.title_label = QLabel("◢ LCARS THEME DEMO")
        self.title_label.setObjectName("title")
        header_layout.addWidget(self.title_label)
        
        # Era selector
        era_layout = QHBoxLayout()
        era_layout.addWidget(QLabel("Era:"))
        
        self.era_combo = QComboBox()
        self.era_combo.addItems([
            "22nd Century (PCARS)", "23rd Century", "24th Century", 
            "25th Century", "29th Century (TCARS)", "Romulan", "Klingon"
        ])
        self.era_combo.setCurrentIndex(3)  # 25th Century default
        self.era_combo.currentIndexChanged.connect(self.change_era)
        era_layout.addWidget(self.era_combo)
        
        header_layout.addLayout(era_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        edit_btn = QPushButton("THEME EDITOR")
        edit_btn.clicked.connect(self.open_theme_editor)
        edit_btn.setObjectName("control_btn")
        controls_layout.addWidget(edit_btn)
        
        fullscreen_btn = QPushButton("TOGGLE FULLSCREEN")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setObjectName("control_btn")
        controls_layout.addWidget(fullscreen_btn)
        
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close)
        exit_btn.setObjectName("exit_btn")
        controls_layout.addWidget(exit_btn)
        
        header_layout.addLayout(controls_layout)
        parent_layout.addWidget(header)
    
    def create_content_area(self, parent_layout):
        """Create main content demonstration area"""
        content = QFrame()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Center - Main display
        center_panel = self.create_main_display()
        content_layout.addWidget(center_panel, 2)
        
        # Right panel - Status
        right_panel = self.create_status_panel()
        content_layout.addWidget(right_panel, 1)
        
        parent_layout.addWidget(content, 1)
    
    def create_control_panel(self):
        """Create left control panel"""
        panel = QFrame()
        panel.setObjectName("lcars_panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Panel title
        title = QLabel("CONTROLS")
        title.setObjectName("panel_title")
        layout.addWidget(title)
        
        # Control buttons
        buttons = [
            ("POWER", self.demo_action),
            ("SHIELDS", self.demo_action), 
            ("WEAPONS", self.demo_action),
            ("NAVIGATION", self.demo_action),
            ("SENSORS", self.demo_action),
            ("COMMUNICATIONS", self.demo_action)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setObjectName("lcars_button")
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        return panel
    
    def create_main_display(self):
        """Create center main display"""
        panel = QFrame()
        panel.setObjectName("main_display")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Display title
        self.display_title = QLabel("MAIN DISPLAY")
        self.display_title.setObjectName("display_title")
        layout.addWidget(self.display_title)
        
        # Time display
        self.time_display = QLabel()
        self.time_display.setObjectName("time_display")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_display)
        
        # Status text
        self.status_text = QLabel("All systems operational")
        self.status_text.setObjectName("status_text")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_text)
        
        # Color demonstration squares
        colors_frame = QFrame()
        colors_layout = QHBoxLayout(colors_frame)
        
        self.color_squares = []
        for i in range(5):
            square = QFrame()
            square.setFixedSize(60, 60)
            square.setObjectName(f"color_square_{i}")
            colors_layout.addWidget(square)
            self.color_squares.append(square)
        
        layout.addWidget(colors_frame)
        layout.addStretch()
        return panel
    
    def create_status_panel(self):
        """Create right status panel"""
        panel = QFrame()
        panel.setObjectName("lcars_panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Panel title
        title = QLabel("STATUS")
        title.setObjectName("panel_title")
        layout.addWidget(title)
        
        # Status items
        status_items = [
            "Power: 100%",
            "Shields: Online", 
            "Weapons: Ready",
            "Navigation: Active",
            "Sensors: Scanning",
            "Comms: Open"
        ]
        
        self.status_labels = []
        for item in status_items:
            label = QLabel(item)
            label.setObjectName("status_item")
            layout.addWidget(label)
            self.status_labels.append(label)
        
        layout.addStretch()
        return panel
    
    def create_footer(self, parent_layout):
        """Create footer"""
        footer = QFrame()
        footer.setFixedHeight(50)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        self.footer_label = QLabel("LCARS Operating System - Theme Demo")
        self.footer_label.setObjectName("footer_text")
        footer_layout.addWidget(self.footer_label)
        
        footer_layout.addStretch()
        
        # Era info
        self.era_label = QLabel()
        self.era_label.setObjectName("era_info")
        footer_layout.addWidget(self.era_label)
        
        parent_layout.addWidget(footer)
    
    def change_era(self, index):
        """Change theme era"""
        era_map = {
            0: LCARSEra.PCARS_22ND,
            1: LCARSEra.PCARS_23RD,
            2: LCARSEra.LCARS_24TH,
            3: LCARSEra.LCARS_25TH,
            4: LCARSEra.TCARS_29TH,
            5: LCARSEra.ROMULAN,
            6: LCARSEra.KLINGON
        }
        
        if index in era_map:
            self.current_era = era_map[index]
            self.current_palette = get_era_palette(self.current_era)
            self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme to all UI elements"""
        if not self.current_palette:
            return
            
        # Base styles
        main_style = f"""
            QMainWindow {{
                background-color: {self.current_palette['background']};
                color: {self.current_palette['text']};
                font-family: "Courier New", monospace;
            }}
            
            QLabel#title {{
                background-color: {self.current_palette['button_colors'][0]};
                color: {self.current_palette['background']};
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
            }}
            
            QFrame#lcars_panel {{
                background-color: {self.current_palette['panel']};
                border: 2px solid {self.current_palette['primary']};
                border-radius: 15px;
            }}
            
            QFrame#main_display {{
                background-color: {self.current_palette['background']};
                border: 3px solid {self.current_palette['primary']};
                border-radius: 20px;
            }}
            
            QLabel#panel_title {{
                color: {self.current_palette['primary']};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }}
            
            QLabel#display_title {{
                color: {self.current_palette['primary']};
                font-size: 22px;
                font-weight: bold;
                padding: 15px;
            }}
            
            QLabel#time_display {{
                color: {self.current_palette['text']};
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
            }}
            
            QLabel#status_text {{
                color: {self.current_palette['secondary']};
                font-size: 16px;
                padding: 10px;
            }}
            
            QPushButton#lcars_button {{
                background-color: {self.current_palette['button_colors'][0]};
                color: {self.current_palette['background']};
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                margin: 3px;
            }}
            
            QPushButton#lcars_button:hover {{
                background-color: {self.current_palette['button_colors'][1]};
            }}
            
            QPushButton#control_btn {{
                background-color: {self.current_palette['secondary']};
                color: {self.current_palette['text']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton#exit_btn {{
                background-color: {self.current_palette['alert_colors'][0]};
                color: {self.current_palette['background']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QLabel#status_item {{
                color: {self.current_palette['text']};
                font-size: 12px;
                padding: 5px;
            }}
            
            QLabel#footer_text {{
                color: {self.current_palette['secondary']};
                font-size: 12px;
            }}
            
            QLabel#era_info {{
                color: {self.current_palette['primary']};
                font-weight: bold;
            }}
            
            QComboBox {{
                background-color: {self.current_palette['panel']};
                color: {self.current_palette['text']};
                border: 1px solid {self.current_palette['secondary']};
                border-radius: 5px;
                padding: 5px;
            }}
        """
        
        # Apply color squares
        for i, square in enumerate(self.color_squares):
            if i < len(self.current_palette['button_colors']):
                color = self.current_palette['button_colors'][i]
                square.setStyleSheet(f"""
                    QFrame#{square.objectName()} {{
                        background-color: {color};
                        border: 2px solid {self.current_palette['primary']};
                        border-radius: 5px;
                    }}
                """)
        
        self.setStyleSheet(main_style)
        
        # Update era info
        era_names = {
            LCARSEra.PCARS_22ND: "22nd Century PCARS",
            LCARSEra.PCARS_23RD: "23rd Century",
            LCARSEra.LCARS_24TH: "24th Century",
            LCARSEra.LCARS_25TH: "25th Century", 
            LCARSEra.TCARS_29TH: "29th Century TCARS",
            LCARSEra.ROMULAN: "Romulan Empire",
            LCARSEra.KLINGON: "Klingon Empire"
        }
        
        self.era_label.setText(era_names.get(self.current_era, "Unknown Era"))
    
    def update_display(self):
        """Update time and status"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y.%m.%d")
        
        self.time_display.setText(f"{time_str}\n{date_str}")
    
    def demo_action(self):
        """Demo button action"""
        button = self.sender()
        if button:
            self.status_text.setText(f"{button.text()} activated")
            QTimer.singleShot(2000, lambda: self.status_text.setText("All systems operational"))
    
    def open_theme_editor(self):
        """Open theme editor"""
        if not self.theme_editor:
            self.theme_editor = LCARSThemeEditor()
        self.theme_editor.show()
        self.theme_editor.raise_()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Courier New", 10)
    app.setFont(font)
    
    demo = LCARSThemeDemo()
    demo.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
