#!/usr/bin/env python3
"""
TCARS 32nd Century - Authentic LCARS Interface matching reference photo
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout, QComboBox,
                           QFrame, QGridLayout)
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPainterPath
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect
from pathlib import Path

# Ensure project root is on sys.path so `lcars` package is importable
current_file = Path(__file__).resolve()
# Walk up until we find the folder that contains the `lcars` package (robust across locations)
project_root = current_file.parent
found = False
for _ in range(6):
    if (project_root / 'lcars').exists():
        found = True
        break
    if project_root.parent == project_root:
        break
    project_root = project_root.parent
if not found:
    # Fallback to parent (expected layout: <repo>/archive/*)
    project_root = current_file.parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.palette import (
    get_era_palette, LCARSEra, get_random_button_color
)
import logging
logger = logging.getLogger(__name__)

class LCARSDisplay(QFrame):
    """Custom circular display matching the photo"""
    def __init__(self, color="#4BBEBF", size=200):
        super().__init__()
        self.setFixedSize(size, size)
        self.color = color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: black;
                border: 3px solid {color};
                border-radius: {size//2}px;
            }}
        """)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw grid pattern
        pen = QPen(QColor(self.color), 1)
        painter.setPen(pen)
        
        # Draw concentric circles
        center = self.width() // 2
        for i in range(3):
            radius = 20 + i * 25
            painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
        
        # Draw radial lines
        for angle in range(0, 360, 30):
            import math
            rad = math.radians(angle)
            x1 = center + 20 * math.cos(rad)
            y1 = center + 20 * math.sin(rad)
            x2 = center + 65 * math.cos(rad)
            y2 = center + 65 * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

class LCARSElbow(QFrame):
    """LCARS elbow corner piece"""
    def __init__(self, position="top-left", color="#4BBEBF"):
        super().__init__()
        self.position = position
        self.color = color
        self.setFixedSize(180, 80)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 0px;
            }}
        """)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        if self.position == "top-left":
            # Draw rounded corner on top-left
            path = QPainterPath()
            path.moveTo(0, 40)
            path.arcTo(0, 0, 80, 80, 180, -90)
            path.lineTo(180, 0)
            path.lineTo(180, 80)
            path.lineTo(0, 80)
            painter.fillPath(path, QBrush(QColor(self.color)))

class TCARS32ndCentury(QMainWindow):
    """
    32nd Century LCARS Interface - Authentic Photo-Matched Design
    """
    temporal_alert = pyqtSignal(str)
    
    def setup_interface(self):
        """Створення автентичного LCARS інтерфейсу як на фото"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === TOP SECTION ===
        top_section = QHBoxLayout()
        top_section.setContentsMargins(0, 0, 0, 0)
        top_section.setSpacing(0)
        
        # Left elbow
        left_elbow = LCARSElbow("top-left", "#4BBEBF")
        top_section.addWidget(left_elbow)
        
        # Top bar with title
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #99FFFF;
                border: none;
            }}
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 0, 0)
        
        title_label = QLabel("◢ LCARS 32nd CENTURY")
        title_label.setStyleSheet(f"""
            color: black;
            font-size: 28px;
            font-weight: bold;
            font-family: 'LCARS', 'Arial', sans-serif;
        """)
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        
        # Status display
        status_display = QLabel("PLAYLIST 32")
        status_display.setStyleSheet(f"""
            color: black;
            font-size: 24px;
            font-weight: bold;
            font-family: 'LCARS', 'Arial', sans-serif;
            padding: 0px 20px;
        """)
        top_layout.addWidget(status_display)
        
        top_section.addWidget(top_bar, 1)
        
        # Right cap
        right_cap = QFrame()
        right_cap.setFixedSize(40, 80)
        right_cap.setStyleSheet(f"""
            QFrame {{
                background-color: #9EA5BA;
                border-top-right-radius: 30px;
                border-bottom-right-radius: 4px;
            }}
        """)
        top_section.addWidget(right_cap)
        
        main_layout.addLayout(top_section)
        
        # === MIDDLE SECTION ===
        middle_section = QHBoxLayout()
        middle_section.setContentsMargins(0, 0, 0, 0)
        middle_section.setSpacing(0)
        
        # Left sidebar
        left_sidebar = QFrame()
        left_sidebar.setFixedWidth(180)
        left_sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: #2A7193;
                border-bottom-left-radius: 60px;
            }}
        """)
        middle_section.addWidget(left_sidebar)
        
        # Main content area
        content_area = QFrame()
        content_area.setStyleSheet("background-color: black;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Circular displays row
        displays_row = QHBoxLayout()
        displays_row.setSpacing(40)
        
        # Left circular display
        left_display = LCARSDisplay("#4BBEBF", 150)
        displays_row.addWidget(left_display)
        
        displays_row.addStretch()
        
        # Right circular display  
        right_display = LCARSDisplay("#4BBEBF", 150)
        displays_row.addWidget(right_display)
        
        content_layout.addLayout(displays_row)
        
        # Control panels grid
        controls_grid = QGridLayout()
        controls_grid.setSpacing(15)
        
        # Create control buttons matching photo layout
        button_colors = ["#FFCC00", "#FF6B6B", "#4BBEBF", "#99FF99", "#FF9900", "#CC66FF"]
        button_labels = ["SYSTEM", "POWER", "SHIELDS", "COMMS", "SENSORS", "WEAPONS"]
        
        for i, (label, color) in enumerate(zip(button_labels, button_colors)):
            btn = QPushButton(label)
            btn.setFixedSize(120, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'LCARS', 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                }}
            """)
            row = i // 3
            col = i % 3
            controls_grid.addWidget(btn, row, col)
        
        content_layout.addLayout(controls_grid)
        content_layout.addStretch()
        
        middle_section.addWidget(content_area, 1)
        main_layout.addLayout(middle_section, 1)
        
        # === BOTTOM SECTION ===
        bottom_section = QHBoxLayout()
        bottom_section.setContentsMargins(0, 0, 0, 0)
        bottom_section.setSpacing(0)
        
        # Left spacer
        bottom_section.addWidget(QFrame())
        
        # Bottom bar
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(30)
        bottom_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #2A7193;
                border-bottom-right-radius: 20px;
                border-top-right-radius: 4px;
            }}
        """)
        bottom_section.addWidget(bottom_bar, 1)
        
        main_layout.addLayout(bottom_section)
        
        # Apply overall styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
        """)
        
    def start_animations(self):
        """Запуск анімацій для інтерфейсу"""
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(3000)  # Зміна кольорів кожні 3 секунди
        
    def update_colors(self):
        """Оновлення кольорів елементів інтерфейсу"""
        # Get random color from 32nd century palette
        new_color = get_random_button_color(self.era)
        
        # Update circular displays
        for widget in self.findChildren(LCARSDisplay):
            widget.color = new_color
            widget.setStyleSheet(f"""
                QFrame {{
                    background-color: black;
                    border: 3px solid {new_color};
                    border-radius: 75px;
                }}
            """)
            widget.update()
        
        print(f"🔄 Колір змінено на: {new_color}")

def main():
    app = QApplication(sys.argv)
    window = TCARS32ndCentury()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
