"""
Modular LCARS Launcher - Об'єднує всі модулі в один інтерфейс
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path('.').absolute().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTabWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Імпортуємо основні компоненти
from lcars.ui.lcars_central import AnimatedButton
from lcars.ui.base_interface import BaseLCARSInterface

class ModularLCARS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Modular System")
        self.showFullScreen()
        
        # Colors
        self.colors = {
            'background': '#000000',
            'text': '#FFFFFF', 
            'accent': '#FF9900',
            'primary': '#3366CC',
            'secondary': '#4477DD',
            'warning': '#FF4444',
            'success': '#00FF00'
        }
        
        # Animation
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(3000)
        
        self.animated_elements = []
        self.setup_ui()
        
    def _color(self, *keys, default="#FFFFFF"):
        for k in keys:
            if k in self.colors:
                return self.colors[k]
        return default
        
    def add_animated_element(self, element):
        if element not in self.animated_elements:
            self.animated_elements.append(element)
            
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QFrame()
        header.setFixedHeight(120)
        header_layout = QHBoxLayout(header)
        
        title = QLabel('LCARS MODULAR SYSTEM')
        title.setFont(QFont('Arial', 36, QFont.Weight.Bold))
        title.setStyleSheet(f'color: {self._color("accent")};')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        self.add_animated_element(title)
        
        layout.addWidget(header)
        
        # Tab Widget for modules
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {self._color('accent')};
                background-color: {self._color('background')};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background: {self._color('primary')};
                color: white;
                padding: 15px 30px;
                margin: 2px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background: {self._color('accent')};
            }}
        """)
        
        # Add main tabs
        self.add_main_tabs()
        
        layout.addWidget(self.tabs)
        
        # Footer
        footer = QFrame()
        footer.setFixedHeight(100)
        footer_layout = QHBoxLayout(footer)
        
        # Status
        status = QLabel('STATUS: ALL SYSTEMS OPERATIONAL')
        status.setStyleSheet(f'color: {self._color("text")}; font-size: 18px; padding: 10px;')
        status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        footer_layout.addWidget(status)
        self.add_animated_element(status)
        
        # Return button
        return_btn = QPushButton('RETURN TO MAIN')
        return_btn.setStyleSheet(f'background: {self._color("warning")}; color: white; padding: 15px; font-size: 16px; border-radius: 10px;')
        return_btn.clicked.connect(self.close)
        footer_layout.addWidget(return_btn)
        self.add_animated_element(return_btn)
        
        layout.addWidget(footer)
        
    def add_main_tabs(self):
        # Central Command Tab
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        
        # Add buttons for main systems
        systems = [
            ("LCARS 24th Century", self.launch_24th, self._color('primary')),
            ("LCARS 25th Century", self.launch_25th, self._color('secondary')),
            ("PCARS 22nd Century", self.launch_22nd, self._color('accent')),
            ("TCARS 29th Century", self.launch_29th, self._color('warning')),
            ("Klingon System", self.launch_klingon, '#FF0000'),
            ("Romulan Interface", self.launch_romulan, '#00FF00'),
            ("Base Interface", self.launch_base, self._color('success')),
            ("System Monitor", self.launch_monitor, '#FF00FF')
        ]
        
        for name, callback, color in systems:
            btn = AnimatedButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: 3px solid white;
                    border-radius: 15px;
                    padding: 20px;
                    font-weight: bold;
                    font-size: 18px;
                    min-height: 80px;
                }}
                QPushButton:hover {{
                    background: {color}CC;
                    border-color: {self._color('accent')};
                }}
            """)
            btn.clicked.connect(callback)
            central_layout.addWidget(btn)
            self.add_animated_element(btn)
        
        self.tabs.addTab(central_widget, "🚀 Central Command")
        
        # File Manager Tab
        if True:
            from lcars.modules.file_manager import FileManager
            file_manager = FileManager(self)
            self.tabs.addTab(file_manager, "📁 File Manager")
        if False: # Removed except block
            # Create placeholder
            placeholder = self.create_placeholder("📁 File Manager", "File Manager module not available")
            self.tabs.addTab(placeholder, "📁 File Manager")
        
        # System Monitor Tab
        if True:
            from lcars.modules.system_monitor import SystemMonitor
            monitor = SystemMonitor(self)
            self.tabs.addTab(monitor, "📊 System Monitor")
        if False: # Removed except block
            placeholder = self.create_placeholder("📊 System Monitor", "System Monitor module not available")
            self.tabs.addTab(placeholder, "📊 System Monitor")
        
        # Network Hub Tab
        if True:
            from lcars.modules.network_hub import NetworkHub
            network = NetworkHub(self)
            self.tabs.addTab(network, "🌐 Network Hub")
        if False: # Removed except block
            placeholder = self.create_placeholder("🌐 Network Hub", "Network Hub module not available")
            self.tabs.addTab(placeholder, "🌐 Network Hub")
        
    def create_placeholder(self, title, message):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel(title)
        label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        label.setStyleSheet(f'color: {self._color("accent")};')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        msg = QLabel(message)
        msg.setStyleSheet(f'color: {self._color("text")}; font-size: 16px;')
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)
        
        return widget
        
    def launch_24th(self):
        if True:
            from lcars.ui.LCARS_24th import LCARS24thCentury
            window = LCARS24thCentury()
            window.show()
        if False: # Removed except block
            self.show_error("LCARS 24th Century not available")
            
    def launch_25th(self):
        if True:
            from lcars.ui.LCARS_25th import LCARS25thCentury
            window = LCARS25thCentury()
            window.show()
        if False: # Removed except block
            self.show_error("LCARS 25th Century not available")
            
    def launch_22nd(self):
        if True:
            from lcars.ui.PCARS_22nd import PCARS22ndCentury
            window = PCARS22ndCentury()
            window.show()
        if False: # Removed except block
            self.show_error("PCARS 22nd Century not available")
            
    def launch_29th(self):
        if True:
            from lcars.ui.TCARS_29th import TCARS29thCentury
            window = TCARS29thCentury()
            window.show()
        if False: # Removed except block
            self.show_error("TCARS 29th Century not available")
            
    def launch_klingon(self):
        if True:
            from lcars.ui.Klingon_system import KlingonInterface
            window = KlingonInterface()
            window.show()
        if False: # Removed except block
            self.show_error("Klingon System not available")
            
    def launch_romulan(self):
        if True:
            from lcars.ui.Romulan_interface import RomulanInterface
            window = RomulanInterface()
            window.show()
        if False: # Removed except block
            self.show_error("Romulan Interface not available")
            
    def launch_base(self):
        if True:
            window = BaseLCARSInterface(str(Path('.').absolute().parent))
            window.show()
        if False: # Removed except block
            self.show_error(f"Base Interface error: {e}")
            
    def launch_monitor(self):
        self.show_error("System Monitor launching from main launcher")
        
    def show_error(self, message):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Launch Error")
        msg.exec()
        
    def update_colors(self):
        import random
        colors = [self._color('primary'), self._color('accent'), self._color('secondary'), self._color('success')]
        
        for element in self.animated_elements:
            if True:
                color = random.choice(colors)
                if isinstance(element, QPushButton):
                    element.setStyleSheet(f"""
                        QPushButton {{
                            background: {color};
                            color: white;
                            border: 3px solid white;
                            border-radius: 15px;
                            padding: 20px;
                            font-weight: bold;
                            font-size: 18px;
                            min-height: 80px;
                        }}
                        QPushButton:hover {{
                            background: {color}CC;
                            border-color: {self._color('accent')};
                        }}
                    """)
                elif isinstance(element, QLabel):
                    if 'STATUS' in element.text():
                        element.setStyleSheet(f'color: {color}; font-size: 18px; padding: 10px;')
                    else:
                        element.setStyleSheet(f'color: {color}; font-size: 36px; font-weight: bold;')
            if False: # Removed except block
                pass

def main():
    app = QApplication([])
    window = ModularLCARS()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
