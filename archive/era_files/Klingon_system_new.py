"""
batlh DaHjaj - Klingon Honor System
yIH 'ej HoS - Strength and Honor in Battle
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtGui import QPen, QPainter, QColor, QLinearGradient, QBrush, QFont, QPainterPath
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRect
from lcars.themes.lcars_theme import get_faction_era_theme
from lcars.core.analysis import SpectraAnalyzer
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType
from lcars.core.project_manager import ProjectManager, ProjectInfo
import os
import logging

class KlingonInterface(QMainWindow):
    """Authentic Klingon Battle Interface - batlh DaHjaj"""
    
    def __init__(self, root_path: Path, selector=None):
        super().__init__()
        self.selector = selector
        self.project_manager = ProjectManager(root_path)
        self.current_project = None
        
        # Setup window
        self.setup_window()
        self.setup_klingon_theme()
        self.create_battle_interface()
        self.setup_connections()
        
    def setup_window(self):
        """Setup Klingon battle station window"""
        self.setWindowTitle("tlhIngan wo' - Battle Command")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_klingon_theme(self):
        """Setup authentic Klingon color scheme"""
        # Get Klingon theme from existing system
        self.theme = get_faction_era_theme('klingon', '23rd')
        
        # Apply battle station styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.theme.background_color};
                color: {self.theme.text_color};
            }}
            QWidget {{
                background-color: transparent;
                color: {self.theme.text_color};
            }}
            QLabel {{
                color: {self.theme.text_color};
                font-weight: bold;
            }}
        """)
        
    def paintEvent(self, event):
        """Draw enhanced Klingon geometric patterns"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.theme.background_color))
        gradient.setColorAt(1, QColor(self.theme.panel_color))
        painter.fillRect(self.rect(), gradient)

        # Draw triangular patterns with enhanced styling
        pen = QPen(QColor(self.theme.accent_color))
        pen.setWidth(3)
        painter.setPen(pen)

        # Grid size
        grid_size = 80

        # Draw triangular grid with better spacing
        for x in range(0, self.width(), grid_size):
            for y in range(0, self.height(), grid_size):
                # Draw upward triangle with enhanced appearance
                painter.drawLine(x, y + grid_size, x + grid_size//2, y)
                painter.drawLine(x + grid_size//2, y, x + grid_size, y + grid_size)
                painter.drawLine(x, y + grid_size, x + grid_size, y + grid_size)

                # Draw inner triangle for depth
                inner_offset = 10
                painter.drawLine(x + inner_offset, y + grid_size - inner_offset, 
                               x + grid_size//2, y + inner_offset)
                painter.drawLine(x + grid_size//2, y + inner_offset, 
                               x + grid_size - inner_offset, y + grid_size - inner_offset)
                painter.drawLine(x + inner_offset, y + grid_size - inner_offset, 
                               x + grid_size - inner_offset, y + grid_size - inner_offset)

                # Draw Klingon Empire symbol in some cells
                if (x + y) % (grid_size * 2) == 0:
                    self.draw_empire_symbol(painter, x + grid_size//2, y + grid_size//2)

    def draw_empire_symbol(self, painter, x, y):
        """Draw enhanced Klingon Empire symbol"""
        size = 35
        
        # Outer circle
        pen = QPen(QColor(self.theme.accent_color))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(x - size//2, y - size//2, size, size)
        
        # Inner trefoil symbol
        pen.setColor(QColor(self.theme.warning_color))
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw trefoil symbol with better geometry
        for i in range(3):
            angle = i * 120
            rad = angle * 3.14159 / 180
            
            # Calculate trefoil points
            x1 = x + size * 0.4 * (-1 if i == 1 else (0.5 if i == 0 else 0.5))
            y1 = y + size * 0.3 * (1 if i == 1 else -0.5)
            
            x2 = x1 + size * 0.3
            y2 = y1 + (size * 0.4 if i == 1 else -size * 0.4)
            
            # Draw lines with integer coordinates
            painter.drawLine(int(x), int(y), int(x1), int(y1))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
        # Center dot
        painter.setBrush(QBrush(QColor(self.theme.accent_color)))
        painter.setPen(QPen(QColor(self.theme.accent_color), 1))
        painter.drawEllipse(x - 3, y - 3, 6, 6)

    def create_battle_interface(self):
        """Create authentic Klingon battle interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main battle layout
        battle_layout = QHBoxLayout(central_widget)
        
        # Left command panel
        self.create_command_panel(battle_layout)
        
        # Main battle display
        self.create_main_battle_display(battle_layout)
        
        # Right status panel
        self.create_status_panel(battle_layout)
        
    def create_command_panel(self, layout):
        """Create left command panel"""
        panel = QWidget()
        panel.setFixedWidth(200)
        panel_layout = QVBoxLayout(panel)
        layout.addWidget(panel)
        
        # Add command buttons
        buttons_data = [
            "tlhIngan vo'",
            "Qapla'", 
            "ghojmoHwI'",
            "HablI'",
            "tu'ta'",
            "SeHluV'"
        ]
        
        for btn_text in buttons_data:
            btn = self.create_triangular_button(btn_text)
            panel_layout.addWidget(btn)
            
        panel_layout.addStretch()
        
    def create_main_battle_display(self, layout):
        """Create main battle display area"""
        display = QWidget()
        display_layout = QVBoxLayout(display)
        layout.addWidget(display)
        
        # Battle header
        header = QLabel("tlhIngan wo' Battle Command")
        header.setStyleSheet(f"""
            font-size: 24px;
            color: {self.theme.accent_color};
            font-weight: bold;
            padding: 20px;
            background: transparent;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(header)
        
        # Battle status
        status = QLabel("Qapla'! Battle Systems Online")
        status.setStyleSheet(f"""
            font-size: 18px;
            color: {self.theme.text_color};
            font-weight: bold;
            padding: 10px;
            background: transparent;
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(status)
        
        display_layout.addStretch()
        
    def create_status_panel(self, layout):
        """Create right status panel"""
        panel = QWidget()
        panel.setFixedWidth(250)
        panel_layout = QVBoxLayout(panel)
        layout.addWidget(panel)
        
        # Status information
        status_info = [
            "Battle Status: ACTIVE",
            "Weapons: READY",
            "Shields: 100%",
            "Honor: HIGH",
            "Victory: IMMINENT"
        ]
        
        for info in status_info:
            label = QLabel(info)
            label.setStyleSheet(f"""
                color: {self.theme.text_color};
                font-weight: bold;
                padding: 5px;
                background: transparent;
            """)
            panel_layout.addWidget(label)
            
        panel_layout.addStretch()
        
    def create_triangular_button(self, text):
        """Create exact triangular button from image"""
        class TriangleButton(QWidget):
            def __init__(self, text_text, parent_theme):
                super().__init__()
                self.text = text_text
                self.theme = parent_theme  # Pass theme reference
                self.setFixedSize(160, 60)
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                w = self.width()
                h = self.height()
                
                # Triangle pointing up
                path = QPainterPath()
                path.moveTo(w//2, 8)  # Top point
                path.lineTo(w - 12, h - 8)  # Bottom right
                path.lineTo(12, h - 8)  # Bottom left
                path.closeSubpath()
                
                # Use theme colors instead of hardcoded
                painter.fillPath(path, QBrush(QColor(self.theme.primary_color)))
                
                # Theme border
                pen = QPen(QColor(self.theme.accent_color))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)
                
                # Inner triangle
                inner_path = QPainterPath()
                inner_path.moveTo(w//2, 16)
                inner_path.lineTo(w - 20, h - 16)
                inner_path.lineTo(20, h - 16)
                inner_path.closeSubpath()
                
                pen.setColor(QColor(self.theme.text_color))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawPath(inner_path)
                
                # Theme circle in center
                painter.setBrush(QBrush(QColor(self.theme.accent_color)))
                painter.setPen(QPen(QColor(self.theme.accent_color), 1))
                painter.drawEllipse(w//2 - 6, h//2 - 6, 12, 12)
                
                # Text with theme color
                painter.setPen(QPen(QColor(self.theme.text_color)))
                font = QFont("Arial", 8, QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(QRect(15, h//2 - 8, w - 30, 16), 
                               Qt.AlignmentFlag.AlignCenter, self.text)
        
        return TriangleButton(text, self.theme)  # Pass theme to button
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        pass

def main():
    """Main entry point"""
    print("Starting Klingon Interface...")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Get the root path (project directory)
    root_path = Path(__file__).parent.parent.parent
    print(f"Root path: {root_path}")
    
    # Create and show the Klingon interface
    try:
        klingon_interface = KlingonInterface(root_path)
        print("KlingonInterface created successfully")
        klingon_interface.show()
        print("Window shown successfully")
        
        # Run the application
        print("Starting app.exec()...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
