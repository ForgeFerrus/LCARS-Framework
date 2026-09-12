from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
                           QSizePolicy, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPalette, QLinearGradient, QPainter, QPen

class NX01Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NX-01 Systems")
        self.setGeometry(100, 100, 1200, 800)
        
        # System status
        self.systems = {
            'warp': 0.0,
            'impulse': 0.0,
            'shields': 0.0,
            'phasers': 0.0,
            'torpedoes': 0
        }
        
        # Set the main window style
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0a1a;
            }
            QLabel {
                color: #00a2ff;
                font-family: 'Arial';
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                background: #1a1a3a;
                color: #00a2ff;
                border: 1px solid #00a2ff;
                border-radius: 2px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 120px;
                text-align: center;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2a2a5a;
                color: #00c8ff;
                border-color: #00c8ff;
            }
            QPushButton:pressed {
                background: #3a3a7a;
            }
            QFrame {
                background: rgba(0, 20, 40, 0.7);
                border: 1px solid #00a2ff;
            }
        """)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self._build_ui()
        self._setup_timers()
        
    def _build_ui(self):
        # Main container
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background: #0a0a1a;
                border: 2px solid #00a2ff;
            }
        """)
        
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(2, 2, 2, 2)
        
        # Left panel - Systems
        left_panel = QFrame()
        left_panel.setFixedWidth(200)
        left_panel.setStyleSheet("""
            QFrame {
                background: #0a0a1a;
                border-right: 2px solid #00a2ff;
            }
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(10)
        
        # NX-01 Logo
        logo = QLabel("NX-01")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                color: #00a2ff;
                font-size: 32px;
                font-weight: bold;
                padding: 10px;
                border-bottom: 2px solid #00a2ff;
                margin-bottom: 10px;
            }
        """)
        left_layout.addWidget(logo)
        
        # System buttons
        system_buttons = [
            "Warp Drive", "Impulse Engines", "Deflector", 
            "Weapons", "Shields", "Sensors", "Communications",
            "Life Support", "Internal Sensors"
        ]
        
        for btn_text in system_buttons:
            btn = QPushButton(btn_text)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    margin: 2px;
                    border-radius: 0;
                }
                QPushButton:checked {
                    background: #00a2ff;
                    color: #0a0a1a;
                }
            """)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        
        # Right panel - Main display
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background: #0a0a1a;
            }
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QFrame {
                background: #0a0a1a;
                border-bottom: 1px solid #00a2ff;
            }
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 0, 10, 0)
        
        self.status_label = QLabel("SYSTEMS NOMINAL")
        self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        stardate_label = QLabel("STARDATE: 2151.07")
        stardate_label.setStyleSheet("color: #00a2ff;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(stardate_label)
        
        right_layout.addWidget(status_bar)
        
        # Main content area
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 10, 0, 0)
        
        # System status grid
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # System status indicators
        systems = [
            ("Warp Core", "ONLINE", "#00ff00"),
            ("Impulse Engines", "ONLINE", "#00ff00"),
            ("Deflector", "ONLINE", "#00ff00"),
            ("Phasers", "STANDBY", "#ffff00"),
            ("Torpedoes", "READY", "#00ff00"),
            ("Shields", "ACTIVE", "#00ff00"),
            ("Sensors", "ACTIVE", "#00ff00"),
            ("Communications", "ONLINE", "#00ff00")
        ]
        
        for i, (name, status, color) in enumerate(systems):
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #00a2ff;
                    background: rgba(0, 20, 40, 0.5);
                    min-width: 150px;
                }
            """)
            
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(5, 5, 5, 5)
            
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #00a2ff;")
            
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            layout.addWidget(name_label)
            layout.addWidget(status_label)
            
            row = i // 3
            col = i % 3
            grid.addWidget(frame, row, col)
        
        content_layout.addLayout(grid)
        content_layout.addStretch()
        
        # Alert buttons
        alert_frame = QFrame()
        alert_layout = QHBoxLayout(alert_frame)
        alert_layout.setContentsMargins(0, 10, 0, 0)
        
        red_alert = QPushButton("RED ALERT")
        red_alert.setStyleSheet("""
            QPushButton {
                background: #660000;
                color: #ff3333;
                font-weight: bold;
                border: 1px solid #ff3333;
                padding: 10px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: #990000;
            }
        """)
        red_alert.clicked.connect(self.toggle_red_alert)
        
        yellow_alert = QPushButton("YELLOW ALERT")
        yellow_alert.setStyleSheet("""
            QPushButton {
                background: #663300;
                color: #ffcc00;
                font-weight: bold;
                border: 1px solid #ffcc00;
                padding: 10px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: #996600;
            }
        """)
        yellow_alert.clicked.connect(self.toggle_yellow_alert)
        
        alert_layout.addWidget(red_alert)
        alert_layout.addWidget(yellow_alert)
        
        content_layout.addWidget(alert_frame)
        right_layout.addWidget(content)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Set main container as central widget
        self.main_layout.addWidget(main_container)
        
    def toggle_red_alert(self):
        if self.status_label.text() == "RED ALERT":
            self.status_label.setText("SYSTEMS NOMINAL")
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            self.setStyleSheet("""
                QMainWindow {
                    background: #0a0a1a;
                }
            """)
        else:
            self.status_label.setText("RED ALERT")
            self.status_label.setStyleSheet("color: #ff3333; font-weight: bold;")
            self.setStyleSheet("""
                QMainWindow {
                    background: #330000;
                }
            """)
            
    def toggle_yellow_alert(self):
        if self.status_label.text() == "YELLOW ALERT":
            self.status_label.setText("SYSTEMS NOMINAL")
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            self.setStyleSheet("""
                QMainWindow {
                    background: #0a0a1a;
                }
            """)
        else:
            self.status_label.setText("YELLOW ALERT")
            self.status_label.setStyleSheet("color: #ffcc00; font-weight: bold;")
            self.setStyleSheet("""
                QMainWindow {
                    background: #333300;
                }
            """)
    
    def _setup_timers(self):
        # Simulate system status changes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_systems)
        self.timer.start(3000)  # Update every 3 seconds
    
    def update_systems(self):
        # Simulate random system status changes
        import random
        statuses = ["ONLINE", "WARNING", "OFFLINE"]
        colors = ["#00ff00", "#ffff00", "#ff3333"]
        
        # Find all status labels and update them randomly
        for child in self.findChildren(QLabel):
            if child.text() in ["ONLINE", "WARNING", "OFFLINE", "STANDBY", "ACTIVE", "READY"]:
                if random.random() < 0.2:  # 20% chance to change status
                    status_idx = random.randint(0, 2)
                    child.setText(statuses[status_idx])
                    child.setStyleSheet(f"color: {colors[status_idx]}; font-weight: bold;")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Set the application style
    app.setStyle('Fusion')
    
    # Set the application palette
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor('#0a0a1a'))
    palette.setColor(palette.ColorRole.WindowText, QColor('#00a2ff'))
    palette.setColor(palette.ColorRole.Button, QColor('#1a1a3a'))
    palette.setColor(palette.ColorRole.ButtonText, QColor('#00a2ff'))
    palette.setColor(palette.ColorRole.Highlight, QColor('#00a2ff'))
    palette.setColor(palette.ColorRole.HighlightedText, QColor('#0a0a1a'))
    app.setPalette(palette)
    
    launcher = NX01Launcher()
    launcher.show()
    sys.exit(app.exec())