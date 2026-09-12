"""
LCARS Demo Interface - Updated to use new authentic interfaces
This script provides a PyQt6-based interface to test LCARS themes, palettes, and UI elements.
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QPushButton, QLabel, QComboBox, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt

# Import authentic interfaces
try:
    from lcars.ui.authentic_interfaces import (
        Starfleet24thInterface, KlingonInterface as KlingonAuthInterface,
        RomulanQuantumInterface, CardassianInterface
    )
    AUTHENTIC_INTERFACES_AVAILABLE = True
except ImportError:
    AUTHENTIC_INTERFACES_AVAILABLE = False

class LCARSInterfaceDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Demo Interface - Updated")
        self.setGeometry(100, 100, 900, 700)

        # Main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Setup main UI
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = QLabel("LCARS FRAMEWORK DEMO")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FFCC66;
                background: #000000;
                padding: 15px;
                text-align: center;
                text-transform: uppercase;
                border: 2px solid #FFCC66;
                border-radius: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)
        
        # Selection panel
        selection_panel = QFrame()
        selection_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #001144, stop:0.5 #002266, stop:1 #001144);
                border: 2px solid #00AAFF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        selection_layout = QVBoxLayout(selection_panel)
        
        # Era selection
        era_layout = QHBoxLayout()
        era_label = QLabel("Select Era:")
        era_label.setStyleSheet("color: #FFCC66; font-weight: bold;")
        self.era_dropdown = QComboBox()
        self.era_dropdown.addItems(['22nd', '23rd', '24th', '25th'])
        self.era_dropdown.setStyleSheet("""
            QComboBox {
                background: #FFCC66;
                color: #000000;
                border: 2px solid #FFAA33;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
        """)
        era_layout.addWidget(era_label)
        era_layout.addWidget(self.era_dropdown)
        era_layout.addStretch()
        selection_layout.addLayout(era_layout)
        
        # Faction selection
        faction_layout = QHBoxLayout()
        faction_label = QLabel("Select Faction:")
        faction_label.setStyleSheet("color: #FFCC66; font-weight: bold;")
        self.faction_dropdown = QComboBox()
        self.faction_dropdown.addItems(["STARFLEET", "KLINGON", "ROMULAN", "CARDASSIAN"])
        self.faction_dropdown.setStyleSheet("""
            QComboBox {
                background: #FFCC66;
                color: #000000;
                border: 2px solid #FFAA33;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
        """)
        faction_layout.addWidget(faction_label)
        faction_layout.addWidget(self.faction_dropdown)
        faction_layout.addStretch()
        selection_layout.addLayout(faction_layout)
        
        self.layout.addWidget(selection_panel)
        
        # Test buttons
        button_panel = QFrame()
        button_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #001144, stop:0.5 #002266, stop:1 #001144);
                border: 2px solid #00AAFF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        button_layout = QVBoxLayout(button_panel)
        
        # Launch authentic interface button
        self.launch_button = QPushButton("Launch Authentic Interface")
        self.launch_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFCC66, stop:0.5 #FFAA33, stop:1 #FFCC66);
                color: #000000;
                border: 3px solid #FFAA33;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFAA33, stop:0.5 #FF9900, stop:1 #FFAA33);
                color: #000000;
                border: 3px solid #FFCC66;
            }
        """)
        self.launch_button.clicked.connect(self.launch_authentic_interface)
        button_layout.addWidget(self.launch_button)
        
        # Test theme button
        self.test_theme_button = QPushButton("Test Theme Only")
        self.test_theme_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00AAFF, stop:0.5 #0088CC, stop:1 #00AAFF);
                color: #FFFFFF;
                border: 2px solid #0066AA;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                text-transform: uppercase;
            }
        """)
        self.test_theme_button.clicked.connect(self.test_theme)
        button_layout.addWidget(self.test_theme_button)
        
        # Launch main launcher button
        self.launch_main_button = QPushButton("Launch Main Launcher")
        self.launch_main_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFAA, stop:0.5 #00CC88, stop:1 #00FFAA);
                color: #001144;
                border: 2px solid #00AA88;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                text-transform: uppercase;
            }
        """)
        self.launch_main_button.clicked.connect(self.launch_main_launcher)
        button_layout.addWidget(self.launch_main_button)
        
        self.layout.addWidget(button_panel)
        
        # Output label
        self.output_label = QLabel("Ready to test LCARS interfaces...")
        self.output_label.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                background: #000000;
                border: 2px solid #FFAA33;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }
        """)
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.output_label)
        
        self.layout.addStretch()
        
    def launch_authentic_interface(self):
        """Launch the selected authentic interface"""
        faction = self.faction_dropdown.currentText()
        era = self.era_dropdown.currentText()
        
        if not AUTHENTIC_INTERFACES_AVAILABLE:
            self.output_label.setText("Authentic interfaces not available!")
            return
            
        try:
            # Create new window for the interface
            interface_window = QMainWindow()
            interface_window.setWindowTitle(f"{faction} - {era} Interface")
            interface_window.setGeometry(150, 150, 1000, 700)
            
            # Create appropriate interface
            if faction == "STARFLEET":
                interface_widget = Starfleet24thInterface()
            elif faction == "KLINGON":
                interface_widget = KlingonAuthInterface()
            elif faction == "ROMULAN":
                interface_widget = RomulanQuantumInterface()
            elif faction == "CARDASSIAN":
                interface_widget = CardassianInterface()
            else:
                interface_widget = QLabel("Interface not available")
                
            interface_window.setCentralWidget(interface_widget)
            interface_window.show()
            
            self.output_label.setText(f"Launched {faction} - {era} interface!")
            
        except Exception as e:
            self.output_label.setText(f"Error launching interface: {e}")
            
    def test_theme(self):
        """Test theme application"""
        faction = self.faction_dropdown.currentText()
        era = self.era_dropdown.currentText()
        
        try:
            # Apply faction-specific styling to demo window
            if faction == "STARFLEET":
                stylesheet = """
                    QMainWindow { background: #000000; }
                    QLabel { color: #FFCC66; background: transparent; }
                    QPushButton { 
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #FFCC66, stop:0.5 #FFAA33, stop:1 #FFCC66);
                        color: #000000; border: 2px solid #FFAA33;
                    }
                """
            elif faction == "KLINGON":
                stylesheet = """
                    QMainWindow { background: #1A0000; }
                    QLabel { color: #CC0000; background: transparent; }
                    QPushButton { 
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #CC0000, stop:0.5 #990000, stop:1 #CC0000);
                        color: #FFFF00; border: 2px solid #FF0000;
                    }
                """
            elif faction == "ROMULAN":
                stylesheet = """
                    QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000822, stop:0.5 #001144, stop:1 #000822); }
                    QLabel { color: #00FFAA; background: transparent; }
                    QPushButton { 
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #00FFAA, stop:0.5 #00FFCC, stop:1 #00FFAA);
                        color: #001144; border: 2px solid #00AA88;
                    }
                """
            elif faction == "CARDASSIAN":
                stylesheet = """
                    QMainWindow { background: #2A1810; }
                    QLabel { color: #CC6600; background: transparent; }
                    QPushButton { 
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #CC3300, stop:0.5 #8B0000, stop:1 #CC3300);
                        color: #FFFF00; border: 2px solid #FFAA00;
                    }
                """
            else:
                stylesheet = ""
                
            self.central_widget.setStyleSheet(stylesheet)
            self.output_label.setText(f"Applied {faction} theme to demo window!")
            
        except Exception as e:
            self.output_label.setText(f"Error applying theme: {e}")
            
    def launch_main_launcher(self):
        """Launch the main LCARS launcher"""
        try:
            from lcars.ui.main_launcher import MainInterface
            launcher = MainInterface()
            launcher.show()
            self.output_label.setText("Launched main LCARS launcher!")
        except Exception as e:
            self.output_label.setText(f"Error launching main launcher: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = LCARSInterfaceDemo()
    demo.show()
    sys.exit(app.exec())