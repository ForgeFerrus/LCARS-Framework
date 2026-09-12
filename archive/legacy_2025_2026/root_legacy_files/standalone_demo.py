"""
Standalone LCARS Demo - Independent Launchable Version
Can be run without dependencies on the main system
"""
import sys
import os
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont, QPalette, QColor
except ImportError:
    print("PyQt6 not found. Installing...")
    os.system("pip install PyQt6")
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont, QPalette, QColor

class LCARSDemoWindow(QMainWindow):
    """Standalone LCARS Demo Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Framework - Standalone Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # LCARS-style color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QLabel {
                color: #FFAA00;
                font-family: "Courier New", monospace;
                font-size: 14px;
                background-color: #000000;
                border: 2px solid #FFAA00;
                padding: 5px;
            }
            QPushButton {
                color: #000000;
                background-color: #FFAA00;
                font-family: "Courier New", monospace;
                font-size: 12px;
                border: 2px solid #FFAA00;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFCC00;
                border-color: #FFCC00;
            }
            QPushButton:pressed {
                background-color: #FF8800;
                border-color: #FF8800;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel("LCARS FRAMEWORK - STANDALONE DEMO")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFAA00;")
        main_layout.addWidget(header_label)
        
        # Status section
        status_layout = QHBoxLayout()
        
        status_label = QLabel("SYSTEM STATUS: ONLINE")
        status_label.setStyleSheet("color: #00FF00; font-size: 16px;")
        status_layout.addWidget(status_label)
        
        version_label = QLabel("VERSION: DEMO 1.0")
        version_label.setStyleSheet("color: #00AAFF; font-size: 16px;")
        status_layout.addWidget(version_label)
        
        status_layout.addStretch()
        
        time_label = QLabel("STARDATE: 47943.2")
        time_label.setStyleSheet("color: #FF00FF; font-size: 16px;")
        status_layout.addWidget(time_label)
        
        main_layout.addLayout(status_layout)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Left panel
        left_panel = QVBoxLayout()
        
        btn1 = QPushButton("SYSTEM DIAGNOSTICS")
        btn1.clicked.connect(self.show_diagnostics)
        left_panel.addWidget(btn1)
        
        btn2 = QPushButton("SHIP STATUS")
        btn2.clicked.connect(self.show_ship_status)
        left_panel.addWidget(btn2)
        
        btn3 = QPushButton("COMMUNICATIONS")
        btn3.clicked.connect(self.show_communications)
        left_panel.addWidget(btn3)
        
        control_layout.addLayout(left_panel)
        
        # Center display
        center_display = QLabel("MAIN DISPLAY PANEL\n\n[SYSTEM READY]\n\nAwaiting commands...")
        center_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_display.setStyleSheet("""
            QLabel {
                background-color: #001122;
                border: 3px solid #FFAA00;
                font-size: 18px;
                min-height: 300px;
                color: #00FF00;
            }
        """)
        self.display_label = center_display
        control_layout.addWidget(center_display)
        
        # Right panel
        right_panel = QVBoxLayout()
        
        btn4 = QPushButton("TACTICAL")
        btn4.clicked.connect(self.show_tactical)
        right_panel.addWidget(btn4)
        
        btn5 = QPushButton("SCIENCE")
        btn5.clicked.connect(self.show_science)
        right_panel.addWidget(btn5)
        
        btn6 = QPushButton("ENGINEERING")
        btn6.clicked.connect(self.show_engineering)
        right_panel.addWidget(btn6)
        
        control_layout.addLayout(right_panel)
        
        main_layout.addLayout(control_layout)
        
        # Bottom status bar
        bottom_status = QLabel("► ALL SYSTEMS NOMINAL ◄ POWER: 100% ◄ SHIELDS: ONLINE ◄ WEAPONS: STANDBY ◄")
        bottom_status.setStyleSheet("color: #00FF00; font-size: 14px; padding: 10px;")
        main_layout.addWidget(bottom_status)
        
        # Timer for updating display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(2000)  # Update every 2 seconds
        
    def show_diagnostics(self):
        self.display_label.setText(
            "SYSTEM DIAGNOSTICS\n\n"
            "► CPU: 87% IDLE\n"
            "► MEMORY: 64% AVAILABLE\n"
            "► SENSORS: ONLINE\n"
            "► COMMUNICATIONS: ONLINE\n"
            "► LIFE SUPPORT: OPTIMAL\n"
            "► WARP CORE: STABLE\n"
            "► SHIELDS: 100%\n"
            "► PHASERS: STANDBY\n"
            "► TORPEDOES: LOADED"
        )
        
    def show_ship_status(self):
        self.display_label.setText(
            "SHIP STATUS\n\n"
            "► CLASS: GALAXY\n"
            "► REGISTRY: NCC-1701-D\n"
            "► CREW: 1,012\n"
            "► HULL INTEGRITY: 100%\n"
            "► STRUCTURAL INTEGRITY: 100%\n"
            "► ATMOSPHERE: OPTIMAL\n"
            "► GRAVITY: 1.0G\n"
            "► TEMPERATURE: 22°C\n"
            "► HUMIDITY: 45%"
        )
        
    def show_communications(self):
        self.display_label.setText(
            "COMMUNICATIONS\n\n"
            "► SUBSPACE: ACTIVE\n"
            "► UPLINK: ESTABLISHED\n"
            "► FREQUENCY: 1417.2 MHz\n"
            "► ENCRYPTION: LEVEL 4\n"
            "► RANGE: 22.65 LIGHT YEARS\n"
            "► STATUS: CLEAR CHANNEL\n"
            "► PENDING MESSAGES: 0\n"
            "► LOG: NO INTERCEPTIONS"
        )
        
    def show_tactical(self):
        self.display_label.setText(
            "TACTICAL SYSTEMS\n\n"
            "► PHASER BANKS: 100%\n"
            "► PHOTON TORPEDOES: 250/250\n"
            "► QUANTUM TORPEDOES: 50/50\n"
            "► SHIELDS: 100% (4 SECTORS)\n"
            "► TARGETING SYSTEMS: ONLINE\n"
            "► TACTICAL SENSORS: ONLINE\n"
            "► ALERT STATUS: GREEN\n"
            "► WEAPONS STATUS: STANDBY"
        )
        
    def show_science(self):
        self.display_label.setText(
            "SCIENCE SYSTEMS\n\n"
            "► LONG RANGE SENSORS: ONLINE\n"
            "► SHORT RANGE SENSORS: ONLINE\n"
            "► ASTROMETRICS: CALIBRATED\n"
            "► STELLAR CARTOGRAPHY: ACTIVE\n"
            "► BIOLOGICAL SENSORS: ONLINE\n"
            "► GEOLOGICAL SENSORS: ONLINE\n"
            "► TEMPORAL SENSORS: STANDBY\n"
            "► DATA CORE: 87% AVAILABLE"
        )
        
    def show_engineering(self):
        self.display_label.setText(
            "ENGINEERING SYSTEMS\n\n"
            "► WARP CORE: STABLE\n"
            "► IMPULSE ENGINES: READY\n"
            "► THRUSTERS: ONLINE\n"
            "► POWER TRANSFER: 100%\n"
            "► COOLANT SYSTEMS: OPTIMAL\n"
            "► REPLICATORS: ONLINE\n"
            "► TRANSPORTERS: STANDBY\n"
            "► HOLODECKS: AVAILABLE"
        )
        
    def update_display(self):
        # Simulate some system activity
        import random
        messages = [
            "► SCANNING SECTOR 001...",
            "► RUNNING DIAGNOSTICS...",
            "► MONITORING SYSTEMS...",
            "► STANDING BY...",
            "► ALL SYSTEMS NOMINAL...",
            "► Awaiting command input..."
        ]
        if hasattr(self, 'display_label') and "SYSTEM READY" in self.display_label.text():
            self.display_label.setText(f"MAIN DISPLAY PANEL\n\n[{random.choice(messages)}]\n\nAwaiting commands...")

def main():
    """Main entry point for standalone demo"""
    print("[LCARS] Initializing standalone demo...")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 170, 0))
    app.setPalette(palette)
    
    window = LCARSDemoWindow()
    window.show()
    
    print("[LCARS] Demo window launched successfully!")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
