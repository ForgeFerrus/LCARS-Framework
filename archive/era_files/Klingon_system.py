"""
tlhIngan wo' Battle Station - Black Screen Interface
Simple Klingon Command System
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtGui import QPen, QPainter, QColor, QBrush, QFont, QPainterPath
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QApplication, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRect, pyqtSignal
import math

class KlingonTheme:
    "Independent Klingon theme"
    def __init__(self):
        self.colors = {
            'background': QColor(0, 0, 0),
            'primary': QColor(139, 0, 0),
            'accent': QColor(255, 69, 0),
            'text': QColor(255, 255, 255),
            'success': QColor(0, 255, 0),
            'warning': QColor(255, 215, 0)
        }

class KlingonButton(QFrame):
    """Simple Klingon triangular button"""
    clicked = pyqtSignal()
    
    def __init__(self, text, theme, parent=None):
        super().__init__(parent)
        self.text = text
        self.theme = theme
        self.setFixedSize(150, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Black background
        painter.fillRect(self.rect(), self.theme.colors.get('background', QColor(0, 0, 0)))
        
        # Simple triangle
        path = QPainterPath()
        path.moveTo(w//2, 5)
        path.lineTo(w - 10, h - 5)
        path.lineTo(10, h - 5)
        path.closeSubpath()
        
        # Fill with Klingon red from theme
        painter.fillPath(path, QBrush(self.theme.colors.get('primary', QColor(139, 0, 0))))
        
        # Border with theme accent
        pen = QPen(self.theme.colors.get('accent', QColor(255, 69, 0)), 2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Text with theme color
        painter.setPen(QPen(self.theme.colors.get('text', QColor(255, 255, 255))))
        font = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRect(15, h//2, w - 30, 20), 
                       Qt.AlignmentFlag.AlignCenter, self.text)
    
    def mousePressEvent(self, event):
        self.clicked.emit()

class KlingonInterface(QMainWindow):
    """Simple Klingon Black Screen Interface"""
    
    def __init__(self, root_path: Path, selector=None):
        super().__init__()
        self.selector = selector
        # Use independent Klingon theme - no LCARS
        self.theme = KlingonTheme()
        
        self.setup_window()
        self.create_interface()
        
    def setup_window(self):
        """Setup black Klingon window"""
        self.setWindowTitle("tlhIngan wo'")
        self.setGeometry(100, 100, 1400, 800)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # Black background everywhere
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
                color: white;
            }
            QWidget {
                background-color: black;
                color: white;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QFrame {
                background-color: black;
                border: 1px solid #8B0000;
            }
        """)
        
        # Make window always on top
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    
    def paintEvent(self, event):
        """Draw black background with minimal Klingon elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Pure black background
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Minimal triangular grid
        pen = QPen(QColor(139, 0, 0), 1)
        painter.setPen(pen)
        
        grid_size = 100
        for x in range(0, self.width(), grid_size):
            for y in range(0, self.height(), grid_size):
                # Simple triangle
                painter.drawLine(x, y + grid_size, x + grid_size//2, y)
                painter.drawLine(x + grid_size//2, y, x + grid_size, y + grid_size)
                painter.drawLine(x, y + grid_size, x + grid_size, y + grid_size)
    
    def create_interface(self):
        """Create simple Klingon interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Left panel - commands
        left_panel = self.create_command_panel()
        layout.addWidget(left_panel)
        
        # Center - main display
        center_panel = self.create_center_panel()
        layout.addWidget(center_panel)
        
        # Right panel - status
        right_panel = self.create_status_panel()
        layout.addWidget(right_panel)
    
    def create_command_panel(self):
        """Create command panel"""
        panel = QFrame()
        panel.setFixedWidth(350)
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("COMMAND")
        title.setStyleSheet("color: #FF4500; font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Weapons section
        weapons_frame = QFrame()
        weapons_layout = QVBoxLayout(weapons_frame)
        weapons_title = QLabel("WEAPONS")
        weapons_title.setStyleSheet("color: #FF4500; font-size: 14px; font-weight: bold;")
        weapons_layout.addWidget(weapons_title)
        
        weapons = ["PHASERS", "PHOTONS", "DISRUPTORS", "TORPEDOES"]
        for weapon in weapons:
            btn = KlingonButton(weapon, self.theme)
            btn.clicked.connect(lambda w=weapon: print(f"Weapon: {w}"))
            weapons_layout.addWidget(btn)
        
        layout.addWidget(weapons_frame)
        
        # Tactical section
        tactical_frame = QFrame()
        tactical_layout = QVBoxLayout(tactical_frame)
        tactical_title = QLabel("TACTICAL")
        tactical_title.setStyleSheet("color: #FF4500; font-size: 14px; font-weight: bold;")
        tactical_layout.addWidget(tactical_title)
        
        tactical = ["TARGET", "LOCK", "FIRE", "EVADE"]
        for tac in tactical:
            btn = KlingonButton(tac, self.theme)
            btn.clicked.connect(lambda t=tac: print(f"Tactical: {t}"))
            tactical_layout.addWidget(btn)
        
        layout.addWidget(tactical_frame)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self):
        """Create center display"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Main display area
        display = QLabel("KLINGON BATTLE STATION")
        display.setStyleSheet("""
            color: #FF4500; 
            font-size: 28px; 
            font-weight: bold;
            padding: 60px;
            background-color: black;
            border: 3px solid #8B0000;
        """)
        display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(display)
        
        # Battle status
        battle_frame = QFrame()
        battle_layout = QVBoxLayout(battle_frame)
        battle_title = QLabel("BATTLE STATUS")
        battle_title.setStyleSheet("color: #FF4500; font-size: 16px; font-weight: bold; padding: 10px;")
        battle_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        battle_layout.addWidget(battle_title)
        
        battle_info = QLabel("SYSTEMS ONLINE - READY FOR COMBAT")
        battle_info.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 15px;")
        battle_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        battle_layout.addWidget(battle_info)
        
        layout.addWidget(battle_frame)
        
        # Target display
        target_frame = QFrame()
        target_layout = QVBoxLayout(target_frame)
        target_title = QLabel("TARGET ACQUISITION")
        target_title.setStyleSheet("color: #FF4500; font-size: 16px; font-weight: bold; padding: 10px;")
        target_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_layout.addWidget(target_title)
        
        target_info = QLabel("NO TARGETS LOCKED")
        target_info.setStyleSheet("color: #00FF00; font-size: 16px; font-weight: bold; padding: 10px;")
        target_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_layout.addWidget(target_info)
        
        layout.addWidget(target_frame)
        
        layout.addStretch()
        return panel
    
    def create_status_panel(self):
        """Create status panel"""
        panel = QFrame()
        panel.setFixedWidth(350)
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("STATUS")
        title.setStyleSheet("color: #FF4500; font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Ship systems
        systems_frame = QFrame()
        systems_layout = QVBoxLayout(systems_frame)
        systems_title = QLabel("SHIP SYSTEMS")
        systems_title.setStyleSheet("color: #FF4500; font-size: 14px; font-weight: bold;")
        systems_layout.addWidget(systems_title)
        
        systems = [
            ("SHIELDS", "100%"),
            ("HULL", "100%"),
            ("POWER", "MAX"),
            ("WARP", "ONLINE")
        ]
        
        for system, value in systems:
            status_label = QLabel(f"{system}: {value}")
            status_label.setStyleSheet("color: white; font-weight: bold; padding: 5px; font-size: 14px;")
            systems_layout.addWidget(status_label)
        
        layout.addWidget(systems_frame)
        
        # Combat systems
        combat_frame = QFrame()
        combat_layout = QVBoxLayout(combat_frame)
        combat_title = QLabel("COMBAT SYSTEMS")
        combat_title.setStyleSheet("color: #FF4500; font-size: 14px; font-weight: bold;")
        combat_layout.addWidget(combat_title)
        
        combat = [
            ("WEAPONS", "READY"),
            ("TARGETING", "ACTIVE"),
            ("CLOAK", "OFFLINE"),
            ("HONOR", "HIGH")
        ]
        
        for system, value in combat:
            status_label = QLabel(f"{system}: {value}")
            status_label.setStyleSheet("color: white; font-weight: bold; padding: 5px; font-size: 14px;")
            combat_layout.addWidget(status_label)
        
        layout.addWidget(combat_frame)
        
        layout.addStretch()
        return panel

def main():
    """Main entry point"""
    print("Starting Klingon Battle Station...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    root_path = Path(__file__).parent.parent.parent
    
    try:
        klingon_interface = KlingonInterface(root_path)
        klingon_interface.show()
        print("Battle Station operational")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
