"""
LCARS Interface - 25th Century "Boarding Computer" OS - MODERN VERSION
The primary functional hub for Geant4 simulations and ship systems.
"""

# Titanium Bridge Migration: import sys
import random
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout, QGroupBox, 
                            QTextEdit, QProgressBar, QTabWidget, QListWidget,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QProcess, pyqtSlot, QDateTime, QSize, QThread
from PyQt6.QtGui import QFont, QColor

# Add project root to path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color

# Simple font function without complex dependencies
def get_simple_font_style(size, weight="normal"):
    """Simple LCARS font style"""
    weight_map = {
        "light": "200",
        "normal": "400", 
        "bold": "700"
    }
    return f"""
        font-family: 'LCARSGTJ3', 'Antonio', 'Helvetica Ultra Compressed', 'Arial Black', sans-serif;
        font-size: {size}px;
        font-weight: {weight_map.get(weight, "400")};
        letter-spacing: 2px;
        text-transform: uppercase;
    """


class DynamicButton(QPushButton):
    """Button with dynamic color cycling from palette - MODERN VERSION"""
    def __init__(self, text, era, width=None, height=None, button_index=0):
        super().__init__(text)
        self.era = era
        self.button_index = button_index
        self.current_color = get_random_button_color(era)
        
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        
        # Динамічна зміна кольорів кожні 2 секунди
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 200, self.color_timer.start)
        self.color_timer.setInterval(2000)
        
        self.update_style()
    
    def cycle_color(self):
        """Get random color from palette"""
        self.current_color = get_random_button_color(self.era)
        self.update_style()
    
    def update_style(self):
        """Modern style with gradients and effects"""
        font_style = get_simple_font_style(14, "bold")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {self.current_color}, 
                    stop:1 {self.brighten(self.current_color)});
                color: #000;
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                {font_style}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {self.brighten(self.current_color)}, 
                    stop:1 {self.current_color});
                border: 2px solid #FFFFFF;
                box-shadow: 0 0 15px {self.current_color};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {self.darken(self.current_color)}, 
                    stop:1 {self.darken(self.current_color)});
            }}
        """)
        print(f"[25th] Button color: {self.current_color}")
    
    @staticmethod
    def brighten(color):
        """Make color 20% brighter"""
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = max(0, (c.saturation() or 0) - 30)
        v = min(255, (c.value() or 0) + 40)
        c.setHsv(h, s, v)
        return c.name()
    
    @staticmethod
    def darken(color):
        """Make color 20% darker"""
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = min(255, (c.saturation() or 0) + 30)
        v = max(0, (c.value() or 0) - 40)
        c.setHsv(h, s, v)
        return c.name()


class LCARS25thCentury(QMainWindow):
    """
    Advanced 25th Century OS Interface - MODERN VERSION
    Clean interface with dynamic colors and modern LCARS design.
    """
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        self.root_path = root_path or Path(project_root)
        self.selector = selector
        self.colors = get_era_palette(LCARSEra.LCARS_25TH)
        
        # Fix background color issue
        if 'background' not in self.colors:
            self.colors['background'] = '#000000'
        if 'text' not in self.colors:
            self.colors['text'] = '#FFFFFF'
        
        self.setup_window()
        self.setup_ui()
        
        # System Update Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_system_time)
        self.timer.start(1000)
        
        print("[25th] LCARS 25th Century OS initialized")

    def setup_window(self):
        """Setup modern window with proper fonts"""
        self.setWindowTitle("LCARS OS - 25TH CENTURY NODE")
        self.showFullScreen()
        
        # Use simple font system
        font_style = get_simple_font_style(12, "normal")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                {font_style}
            }}
        """)

    def setup_ui(self):
        """Setup modern UI interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 1. MODERN HEADER AREA
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        
        # Modern title with gradient
        title = QLabel("◆ LCARS 25TH CENTURY")
        title_style = get_simple_font_style(28, "bold")
        title.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {get_random_button_color(LCARSEra.LCARS_25TH)}, 
                    stop:1 {get_random_button_color(LCARSEra.LCARS_25TH)});
                color: #000;
                padding: 15px 30px;
                border-radius: 15px;
                {title_style}
            }}
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("SYSTEM ONLINE")
        status_style = get_simple_font_style(16, "normal")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                color: #000;
                padding: 10px 20px;
                border-radius: 10px;
                {status_style}
            }}
        """)
        header_layout.addWidget(self.status_label)
        
        self.main_layout.addLayout(header_layout)
        
        # 2. MODERN CONTROL PANEL
        control_panel = QFrame()
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        
        # System info
        info_label = QLabel("25TH CENTURY ADVANCED SYSTEM")
        info_style = get_simple_font_style(18, "light")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                {info_style}
                padding: 10px;
            }}
        """)
        control_layout.addWidget(info_label)
        
        # Dynamic buttons grid
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(10)
        
        button_configs = [
            ("SYSTEM STATUS", 0),
            ("GEANT4 WORKSTATION", 1),
            ("QUANTUM ANALYSIS", 2),
            ("TEMPORAL MECHANICS", 3),
            ("COMMUNICATIONS", 4),
            ("SECURITY PROTOCOLS", 5)
        ]
        
        for i, (text, index) in enumerate(button_configs):
            btn = DynamicButton(text, LCARSEra.LCARS_25TH, width=250, height=60, button_index=index)
            btn.clicked.connect(lambda checked, t=text: self.handle_button_click(t))
            buttons_grid.addWidget(btn, i // 3, i % 3)
        
        control_layout.addLayout(buttons_grid)
        control_layout.addStretch()
        
        self.main_layout.addWidget(control_panel)
        
        # 3. STATUS BAR
        status_bar = QFrame()
        status_bar.setFixedHeight(50)
        status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 0px;
            }}
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(20, 5, 20, 5)
        
        self.time_label = QLabel()
        time_style = get_simple_font_style(14, "bold")
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: #000;
                {time_style}
            }}
        """)
        status_layout.addWidget(self.time_label)
        
        status_layout.addStretch()
        
        help_text = QLabel("F1: HELP | ESC: EXIT")
        help_style = get_simple_font_style(12, "normal")
        help_text.setStyleSheet(f"""
            QLabel {{
                color: #000;
                {help_style}
            }}
        """)
        status_layout.addWidget(help_text)
        
        self.main_layout.addWidget(status_bar)
        
        print("[25th] Modern UI setup completed")

    def handle_button_click(self, button_text):
        """Handle button clicks"""
        print(f"[25th] Button clicked: {button_text}")
        self.status_label.setText(f"ACTIVE: {button_text}")
        
        # Update status color
        new_color = get_random_button_color(LCARSEra.LCARS_25TH)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {new_color};
                color: #000;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
        """)

    def update_system_time(self):
        """Update system time display"""
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)

    def keyPressEvent(self, event):
        """Handle key events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F1:
            QMessageBox.information(self, "Help", "LCARS 25th Century OS\n\nAdvanced interface for modern systems.\n\nFeatures:\n• Dynamic color algorithms\n• Modern font system\n• Quantum interface design")


def main():
    """Launch 25th Century OS"""
    print("Starting LCARS 25th Century OS...")
    
    app = QApplication(sys.argv)
    window = LCARS25thCentury()
    
    print("LCARS 25th Century OS launched!")
    print("Features: Dynamic colors, Modern fonts, Clean interface")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
