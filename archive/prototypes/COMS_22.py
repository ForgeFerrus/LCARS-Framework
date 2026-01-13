"""
LCARS Interface - 22nd Century Edition
Early LCARS interface with wireframe design from 22nd century
"""

import sys
from pathlib import Path

# Додавання шляху до проекту для автономного запуску
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QGridLayout, QTreeWidget,
                           QTreeWidgetItem, QApplication, QSizePolicy)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QResizeEvent
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF
import os
import logging
from pathlib import Path
from lcars.core.project_manager import ProjectManager
from lcars.core.file_analyzer import FileAnalyzer

# --- Merged Classes from 22nd.py ---

# --- Простий прямокутник (LCARSRect) ---
class LCARSRect(QWidget):
    def __init__(self, color="#BFC2C4", border_color="#FFF", border=4, parent=None):
        super().__init__(parent)
        self.color = color
        self.border_color = border_color
        self.border = border
        self.setStyleSheet("background: transparent;")
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(self.border_color), self.border))
        painter.setBrush(QColor(self.color))
        painter.drawRect(self.border//2, self.border//2, w-self.border, h-self.border)

# --- Простий круг (LCARSCircle) ---
class LCARSCircle(QWidget):
    def __init__(self, color="#1A3AFF", border_color="#FFF", border=4, parent=None):
        super().__init__(parent)
        self.color = color
        self.border_color = border_color
        self.border = border
        self.setStyleSheet("background: transparent;")
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        d = min(w, h) - self.border
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(self.border_color), self.border))
        painter.setBrush(QColor(self.color))
        painter.drawEllipse((w-d)//2, (h-d)//2, d, d)

# --- PCARSButton: інтерактивна кнопка ---
class PCARSButton(QPushButton):
    """Інтерактивна LCARS-кнопка: прямокутник з тонким контуром, сіра смуга знизу, квадрат з кругом у правому верхньому куті."""
    def __init__(self, number='00-0000', label='NAME', color='#3399FF', bar_color='#CCCCCC', border_color='#222', parent=None):
        super().__init__(parent)
        self._number = number
        self._label = label
        self._color = color
        self._bar_color = bar_color
        self._border_color = border_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(100, 60)
        self._hover = False
        self._pressed = False
        self.setCheckable(True)
        self.setStyleSheet("background: transparent; border: none;")

    def leaveEvent(self, a0):
        self._hover = False
        self.update()
    def mousePressEvent(self, e):
        self._pressed = True
        self.update()
        super().mousePressEvent(e)
    def mouseReleaseEvent(self, e):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(e)
    def resizeEvent(self, a0):
        self.update()
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        bar_h = int(h * 0.28)
        square_size = int(h * 0.38)
        circle_d = int(square_size * 0.62)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        pen_width = 2 if not self._hover else 4
        
        # Main rect
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._color))
        painter.drawRect(0, 0, w, h-bar_h)
        
        # Bottom bar
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(0, h-bar_h, w, bar_h)
        
        # Square top-right
        sq_x = w - square_size - pen_width
        sq_y = pen_width
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(sq_x, sq_y, square_size, square_size)
        
        # Circle in square
        circ_x = sq_x + (square_size - circle_d)//2
        circ_y = sq_y + (square_size - circle_d)//2
        painter.setPen(QPen(QColor(self._bar_color), pen_width))
        painter.setBrush(QColor('#FFF'))
        painter.drawEllipse(circ_x, circ_y, circle_d, circle_d)
        
        # Number centered
        painter.setPen(QPen(QColor('#111'), 2))
        font = QFont('Arial', max(10, int((h-bar_h)*0.32)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, int((h-bar_h)*0.18), w, int((h-bar_h)*0.32), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._number)
        
        # Label in bar
        font.setPointSize(max(8, int(bar_h*0.5)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, h-bar_h, w, bar_h, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._label)
        
        if self._pressed:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0,0,0,40))
            painter.drawRect(0, 0, w, h)

# --- PCARSPanel: набір drag-and-drop примітивів ---
class PCARSPanel(QWidget):
    def __init__(self, parent=None, label="WARP FIELD ANL", circle_color="#1A3AFF", squares=None, square_labels=None, grid_rows=10, grid_cols=16):
        super().__init__(parent)
        self.label = label
        self.circle_color = circle_color
        self.squares = squares if squares is not None else ["#00F6FF", "#FFE600", "#888888"]
        self.setStyleSheet("background: transparent;")
        self.rect_base = LCARSRect(color="#BFC2C4", border_color="#FFF", border=6, parent=self)
        self.rect_screen = LCARSRect(color="#000", border_color="#FFF", border=4, parent=self)
        self.circle = LCARSCircle(color=self.circle_color, border_color="#FFF", border=4, parent=self)
        self.buttons = [LCARSRect(color=c, border_color="#FFF", border=3, parent=self) for c in self.squares]
        self.layout_state = {
            'rect_base': [30, 30, 500, 350],
            'rect_screen': [80, 60, 380, 120],
            'circle': [30, 30, 56, 56],
            'buttons': [[40, 200, 52, 52], [40, 260, 52, 52], [40, 320, 52, 52]]
        }
        self.update_layout()

    def update_layout(self):
        self.rect_base.setGeometry(*self.layout_state['rect_base'])
        self.rect_screen.setGeometry(*self.layout_state['rect_screen'])
        self.circle.setGeometry(*self.layout_state['circle'])
        for i, btn in enumerate(self.buttons):
            if i < len(self.layout_state['buttons']):
                btn.setGeometry(*self.layout_state['buttons'][i])

# --- Універсальне полотно (LCARSCanvas) ---
class LCARSCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000000;")
        self.elements = []
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#BFC2C4", border_color="#FFF", border=6, parent=self), 'geom': [100, 100, 500, 350]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#000", border_color="#FFF", border=4, parent=self), 'geom': [180, 140, 380, 120]})
        self.elements.append({'type': 'circle', 'widget': LCARSCircle(color="#1A3AFF", border_color="#FFF", border=4, parent=self), 'geom': [100, 100, 56, 56]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#00F6FF", border_color="#FFF", border=3, parent=self), 'geom': [120, 320, 52, 52]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#FFE600", border_color="#FFF", border=3, parent=self), 'geom': [120, 380, 52, 52]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#888888", border_color="#FFF", border=3, parent=self), 'geom': [120, 440, 52, 52]})
        
        self._drag = None
        self._resize = None
        self._drag_offset = (0,0)
        self._resize_offset = (0,0)
        self.update_layout()
        
        self.save_btn = PCARSButton(number='SAVE', label='ЗБЕРЕГТИ', color='#3399FF', bar_color='#CCCCCC', border_color='#222', parent=self)
        self.save_btn.setGeometry(20, 20, 160, 60)
        self.save_btn.clicked.connect(self.save_layout)

    def update_layout(self):
        for el in self.elements:
            el['widget'].setGeometry(*el['geom'])

    def mousePressEvent(self, a0):
        if a0 is None: return
        px, py = int(a0.pos().x()), int(a0.pos().y())
        margin = 8
        for idx, el in enumerate(reversed(self.elements)):
            x, y, w, h = el['geom']
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = len(self.elements)-1-idx
                self._resize_offset = (x+w-px, y+h-py)
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = len(self.elements)-1-idx
                self._drag_offset = (px-x, py-y)
                return

    def mouseMoveEvent(self, a0):
        if a0 is None: return
        px, py = int(a0.pos().x()), int(a0.pos().y())
        if self._resize is not None:
            x, y, w, h = self.elements[self._resize]['geom']
            dx, dy = self._resize_offset
            self.elements[self._resize]['geom'] = [x, y, max(16, px-x+dx), max(16, py-y+dy)]
            self.update_layout()
        elif self._drag is not None:
            x, y, w, h = self.elements[self._drag]['geom']
            dx, dy = self._drag_offset
            self.elements[self._drag]['geom'] = [px-dx, py-dy, w, h]
            self.update_layout()

    def mouseReleaseEvent(self, a0):
        self._drag = None
        self._resize = None

    def resizeEvent(self, a0):
        self.update_layout()
        self.save_btn.setGeometry(20, 20, 160, 60)

    def save_layout(self):
        import json
        layout = [dict(type=el['type'], geom=el['geom']) for el in self.elements]
        try:
            with open('lcars_layout.json', 'w', encoding='utf-8') as f:
                json.dump(layout, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Saved", "Layout saved to lcars_layout.json")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))



class PCARS22ndCentury(QMainWindow):
    """22nd Century LCARS Interface with wireframe aesthetics"""
    
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        # Determine project root
        self.root_path = root_path or Path(__file__).resolve().parents[2]
        self.selector = selector
        
        # Ensure `self.colors` exists for static analysis and fallback usage
        # Ensure `self.colors` exists for static analysis and fallback usage
        self.colors = {
            'background': '#000000', 'text': '#FFFFFF', 'panel': '#111111', 'grid': '#444444',
            'blue': '#0066CC', 'yellow': '#FFFF00', 'white': '#FFFFFF', 'gray': '#888888',
            'success': '#00FF00', 'error': '#FF0000', 'primary': '#FF9900', 'tertiary': '#4477DD'
        }
        
        # Initialize managers
        self.project_manager = ProjectManager(root_path or Path("."))
        self.current_project = None
        self.FileAnalyzer = FileAnalyzer
        
        # Set up window
        self.setup_window()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window properties"""
        self.setWindowTitle("LCARS Framework - 22nd Century")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                font-family: 'Courier New', monospace;
            }}
            QListWidget, QTreeWidget, QTableWidget {{
                border: 1px solid {self.colors['gray']};
                background-color: {self.colors['background']};
                alternate-background-color: #111111;
            }}
            QHeaderView::section {{
                background-color: {self.colors['blue']};
                color: {self.colors['white']};
                border: 1px solid {self.colors['gray']};
                padding: 4px;
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['gray']};
                background-color: {self.colors['background']};
            }}
            QTabBar::tab {{
                background: {self.colors['blue']};
                color: {self.colors['white']};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {self.colors['primary']};
                color: {self.colors['background']};
            }}
        """)
        
    def create_layouts(self):
        """Create main layout structure"""
        # Left panel (navigation) - standard width for clean look
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(300)
        self.left_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_layout)
        
        # Main content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        
        # Add to main layout
        self.main_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.content_area)
        
    def create_widgets(self):
        """Create and set up all widgets"""
        self.create_left_panel()
        self.create_header()
        self.create_project_list()
        self.create_content_area()
        self.create_footer()
        
    def create_left_panel(self):
        """Create 22nd century LCARS navigation panel"""
        # Top status section - wireframe style
        status_widget = QWidget()
        status_widget.setFixedHeight(200)
        status_widget.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        
        status_layout = QVBoxLayout()
        
        # Create status display
        status_header = QLabel("PCARS 22ND")
        status_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 24px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        status_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_text = QLabel("SYSTEM ONLINE")
        status_text.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 20px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background: transparent;
        """)
        status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(status_header)
        status_layout.addWidget(status_text)
        status_widget.setLayout(status_layout)
        self.left_layout.addWidget(status_widget)
        
        # Characteristic LCARS buttons - proper 22nd century style
        self.create_lcars_button("PROJECTS", self.show_projects, self.colors['blue'])
        self.create_lcars_button("SIMULATION", self.show_simulation, self.colors['blue'])
        self.create_lcars_button("ANALYSIS", self.show_analysis, self.colors['yellow'])
        self.create_lcars_button("VISUAL EDITOR", self.show_canvas, self.colors['tertiary'])
        self.create_lcars_button("SETTINGS", self.show_settings, self.colors['gray'])
        
        # Add spacer at bottom
        self.left_layout.addStretch()
        
    def create_lcars_button(self, text, slot, color):
        """Create characteristic LCARS button for 22nd century"""
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {self.colors['background']};
                border: 2px solid {self.colors['gray']};
                text-align: left;
                padding: 10px 20px;
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['text']};
                color: {color};
                border-color: {self.colors['white']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['gray']};
                color: {self.colors['text']};
            }}
        """)
        btn.clicked.connect(slot)
        self.left_layout.addWidget(btn)
        
    def create_nav_button(self, text, slot):
        """Create a wireframe LCARS navigation button"""
        btn = QPushButton(text)
        btn.setFixedHeight(60)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                border: 2px solid {self.colors['blue']};
                text-align: left;
                padding: 5px 15px;
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['blue']};
                color: {self.colors['background']};
                border-color: {self.colors['yellow']};
            }}
        """)
        btn.clicked.connect(slot)
        self.left_layout.addWidget(btn)
        
        # Monitor header
        monitor_header = QLabel("SYSTEM MONITOR")
        monitor_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 16px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        monitor_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # System status indicators
        status_grid = QGridLayout()
        
        # CPU, Memory, Power indicators
        indicators = [
            ("CPU", "87%", self.colors['blue']),
            ("MEM", "64%", self.colors['yellow']),
            ("PWR", "92%", self.colors['success']),
            ("NET", "ON", self.colors['blue'])
        ]
        
        for i, (label, value, color) in enumerate(indicators):
            row, col = i // 2, i % 2
            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"""
                color: {self.colors['text']};
                font-size: 12px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 2px;
                border: 1px solid {self.colors['gray']};
                background: transparent;
            """)
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"""
                color: {color};
                font-size: 14px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 2px;
                border: 1px solid {self.colors['gray']};
                background: transparent;
            """)
            value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_grid.addWidget(label_widget, row, col*2)
            status_grid.addWidget(value_widget, row, col*2+1)
        
        monitor_layout.addWidget(monitor_header)
        monitor_layout.addLayout(status_grid)
        monitor_widget.setLayout(monitor_layout)
        self.left_layout.addWidget(monitor_widget)
        
    def create_comm_panel(self):
        """Create communication panel for 22nd century"""
        comm_widget = QWidget()
        comm_widget.setFixedHeight(120)
        comm_widget.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        
        comm_layout = QVBoxLayout()
        
        # Comm header
        comm_header = QLabel("COMM SYSTEMS")
        comm_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 16px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        comm_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Comm status
        comm_status = QLabel("SUBSPACE: ACTIVE")
        comm_status.setStyleSheet(f"""
            color: {self.colors['success']};
            font-size: 14px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background: transparent;
        """)
        comm_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        comm_layout.addWidget(comm_header)
        comm_layout.addWidget(comm_status)
        comm_widget.setLayout(comm_layout)
        self.left_layout.addWidget(comm_widget)
        
    def create_power_systems(self):
        """Create power systems panel for 22nd century"""
        power_widget = QWidget()
        power_widget.setFixedHeight(100)
        power_widget.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        
        power_layout = QVBoxLayout()
        
        # Power header
        power_header = QLabel("POWER SYSTEMS")
        power_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 16px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        power_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Power status
        power_status = QLabel("REACTOR: STABLE")
        power_status.setStyleSheet(f"""
            color: {self.colors['success']};
            font-size: 14px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background: transparent;
        """)
        power_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        power_layout.addWidget(power_header)
        power_layout.addWidget(power_status)
        power_widget.setLayout(power_layout)
        self.left_layout.addWidget(power_widget)
        
    def create_right_panel(self):
        """Create right panel for additional 22nd century systems"""
        # Sensor systems
        self.create_sensor_panel()
        
        # Navigation systems
        self.create_nav_systems()
        
        # Tactical systems
        self.create_tactical_panel()
        
        # Add spacer at bottom
        self.right_layout.addStretch()
        
    def create_sensor_panel(self):
        """Create sensor systems panel"""
        sensor_widget = QWidget()
        sensor_widget.setFixedHeight(180)
        sensor_widget.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        
        sensor_layout = QVBoxLayout()
        
        # Sensor header
        sensor_header = QLabel("SENSORS")
        sensor_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 16px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        sensor_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Sensor readings
        sensor_readings = [
            ("LONG RANGE", "ACTIVE", self.colors['success']),
            ("SHORT RANGE", "ACTIVE", self.colors['success']),
            ("ASTROMETRICS", "STANDBY", self.colors['yellow']),
            ("TACTICAL", "ACTIVE", self.colors['blue'])
        ]
        
        for label, status, color in sensor_readings:
            sensor_item = QLabel(f"{label}: {status}")
            sensor_item.setStyleSheet(f"""
                color: {color};
                font-size: 12px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 3px;
                border: 1px solid {self.colors['gray']};
                background: transparent;
            """)
            sensor_item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sensor_layout.addWidget(sensor_item)
        
        sensor_layout.addWidget(sensor_header)
        sensor_widget.setLayout(sensor_layout)
        self.right_layout.addWidget(sensor_widget)
        
    def create_nav_systems(self):
        """Create navigation systems panel"""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(150)
        nav_widget.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        
        nav_layout = QVBoxLayout()
        
        # Nav header
        nav_header = QLabel("NAVIGATION")
        nav_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 16px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        nav_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Nav status
        nav_status = QLabel("WARP: OFFLINE")
        nav_status.setStyleSheet(f"""
            color: {self.colors['yellow']};
            font-size: 14px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background: transparent;
        """)
        nav_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        imp_status = QLabel("IMPULSE: READY")
        imp_status.setStyleSheet(f"""
            color: {self.colors['success']};
            font-size: 14px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background: transparent;
        """)
        imp_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_layout.addWidget(nav_header)
        nav_layout.addWidget(nav_status)
        nav_layout.addWidget(imp_status)
        nav_widget.setLayout(nav_layout)
        self.right_layout.addWidget(nav_widget)
        
    def create_tactical_panel(self):
        """Create tactical systems panel"""
        tactical_widget = QWidget()
        tactical_widget.setFixedHeight(120)
        tactical_widget.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        
        tactical_layout = QVBoxLayout()
        
        # Tactical header
        tactical_header = QLabel("TACTICAL")
        tactical_header.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 16px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        tactical_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tactical status
        tactical_status = QLabel("PHASERS: READY")
        tactical_status.setStyleSheet(f"""
            color: {self.colors['success']};
            font-size: 14px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background: transparent;
        """)
        tactical_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tactical_layout.addWidget(tactical_header)
        tactical_layout.addWidget(tactical_status)
        tactical_widget.setLayout(tactical_layout)
        self.right_layout.addWidget(tactical_widget)
        
#    def create_nav_button(self, text, slot): # DUPLICATE REMOVED
#        btn = QPushButton(text)
#        btn.setFixedHeight(60)
#        btn.setStyleSheet(f"""
#            QPushButton {{
#                background-color: {self.colors['background']};
#                color: {self.colors['text']};
#                border: 2px solid {self.colors['blue']};
#                text-align: left;
#                padding: 5px 15px;
#                font-family: 'Courier New', monospace;
#                font-size: 16px;
#                font-weight: bold;
#            }}
#            QPushButton:hover {{
#                background-color: {self.colors['blue']};
#                color: {self.colors['background']};
#                border-color: {self.colors['yellow']};
#            }}
#        """)
#        btn.clicked.connect(slot)
#        self.left_layout.addWidget(btn)
        
    def create_header(self):
        """Create wireframe LCARS header"""
        header = QFrame()
        header.setFixedHeight(100)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Create left corner element - wireframe
        corner = QWidget()
        corner.setFixedWidth(150)
        corner.setStyleSheet(f"""
            background-color: {self.colors['background']};
            border: 2px solid {self.colors['gray']};
        """)
        header_layout.addWidget(corner)
        
        # Create title
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            color: {self.colors['text']};
            padding: 10px;
            border: none;
        """)
        header_layout.addWidget(title)
        
        # Create right status panel
        status_panel = QWidget()
        status_layout = QVBoxLayout()
        
        # Add time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            color: {self.colors['text']};
            padding: 5px;
            border: 1px solid {self.colors['gray']};
            background-color: {self.colors['background']};
        """)
        status_layout.addWidget(self.time_label)
        
        # Add system status
        system_status = QLabel("SYSTEMS OPERATIONAL")
        system_status.setStyleSheet(f"""
            font-size: 16px;
            font-family: 'Courier New', monospace;
            color: {self.colors['text']};
            border: none;
        """)
        status_layout.addWidget(system_status)
        
        status_panel.setLayout(status_layout)
        header_layout.addWidget(status_panel)
        
        # Add header buttons
        header_buttons = self.create_header_buttons()
        header_layout.addLayout(header_buttons)
        
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
        
        # Set up timer to update time
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
        return header
        
    def create_project_list(self):
        """Create project list with file browser"""
        # Project list
        self.project_list = QListWidget()
        self.update_project_list()
        
        # Project details
        self.project_info = QWidget()
        info_layout = QVBoxLayout()
        
        # Header
        self.project_title = QLabel("No Project Selected")
        self.project_title.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors['text']};
            padding: 10px;
            border-bottom: 2px solid {self.colors['blue']};
        """)
        info_layout.addWidget(self.project_title)
        
        # Path
        path_widget = QWidget()
        path_layout = QHBoxLayout()
        path_label = QLabel("Location:")
        path_label.setStyleSheet(f"color: {self.colors['yellow']};")
        self.project_path = QLabel()
        self.project_path.setStyleSheet(f"color: {self.colors['text']};")
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.project_path)
        path_widget.setLayout(path_layout)
        info_layout.addWidget(path_widget)
        
        # Description
        desc_scroll = QScrollArea()
        desc_scroll.setWidgetResizable(True)
        desc_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {self.colors['gray']};
                background: {self.colors['background']};
            }}
        """)
        self.project_description = QLabel()
        self.project_description.setWordWrap(True)
        self.project_description.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                padding: 10px;
                background: transparent;
            }}
        """)
        desc_scroll.setWidget(self.project_description)
        info_layout.addWidget(desc_scroll)
        
        # File browser
        self.create_file_browser()
        info_layout.addWidget(self.file_browser)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Project")
        self.run_button.clicked.connect(self.run_selected_project)
        self.run_button.setEnabled(False)
        button_layout.addWidget(self.run_button)
        
        self.analyze_button = QPushButton("Analyze Data")
        self.analyze_button.clicked.connect(self.analyze_selected_project)
        self.analyze_button.setEnabled(False)
        button_layout.addWidget(self.analyze_button)
        
        info_layout.addLayout(button_layout)
        self.project_info.setLayout(info_layout)
        
    def create_content_area(self):
        """Create main content area"""
        self.content_stack = QTabWidget()
        
        # Add tabs
        self.setup_project_tab()
        self.setup_simulation_tab()
        self.setup_analysis_tab()
        self.setup_canvas_tab()  # New tab for Visual Editor
        
        self.content_layout.addWidget(self.content_stack)
        
    def create_footer(self):
        """Create footer with status information"""
        footer = QFrame()
        footer.setFixedHeight(40)
        footer_layout = QHBoxLayout()
        
        self.status_label = QLabel("System Status: Online")
        self.status_label.setStyleSheet(f"color: {self.colors['success']};")
        footer_layout.addWidget(self.status_label)
        
        footer.setLayout(footer_layout)
        self.content_layout.addWidget(footer)
        return footer
        
    def setup_project_tab(self):
        """Set up project management tab"""
        project_tab = QWidget()
        layout = QHBoxLayout()
        
        # Add project list and info
        list_container = QWidget()
        list_layout = QVBoxLayout()
        header_label = QLabel("Available Projects")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        list_layout.addWidget(header_label)
        list_layout.addWidget(self.project_list)
        list_container.setLayout(list_layout)
        
        layout.addWidget(list_container)
        layout.addWidget(self.project_info)
        
        project_tab.setLayout(layout)
        self.content_stack.addTab(project_tab, "Projects")
        
    def setup_simulation_tab(self):
        """Set up simulation control tab"""
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        
        # Add simulation controls
        self.simulation_status = QLabel("No simulation running")
        layout.addWidget(self.simulation_status)
        
        simulation_tab.setLayout(layout)
        self.content_stack.addTab(simulation_tab, "Simulation")
        
    def setup_analysis_tab(self):
        """Set up data analysis tab"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()
        
        # Add analysis tools
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Energy", "Counts", "Particle"])
        layout.addWidget(self.results_table)
        
        analysis_tab.setLayout(layout)
        self.content_stack.addTab(analysis_tab, "Analysis")

    def setup_canvas_tab(self):
        """Set up visual editor tab with LCARSCanvas"""
        canvas_tab = QWidget()
        layout = QVBoxLayout()
        # Ensure canvas fills the space
        self.canvas_widget = LCARSCanvas()
        layout.addWidget(self.canvas_widget)
        canvas_tab.setLayout(layout)
        self.content_stack.addTab(canvas_tab, "Visual Editor")
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def update_project_list(self):
        """Update list of available projects"""
        self.project_list.clear()
        for project_name in self.project_manager.get_project_names():
            self.project_list.addItem(project_name)
            
    def on_project_selected(self, current, previous):
        """Handle project selection"""
        if not current:
            return
            
        project_name = current.text()
        self.current_project = self.project_manager.get_project(project_name)
        
        if self.current_project:
            # Create file analyzer
            self.current_analyzer = self.FileAnalyzer(self.current_project.path)
            
            # Update project info
            self.project_title.setText(self.current_project.name)
            self.project_path.setText(str(self.current_project.path))
            
            # Get and display README
            readme_content = self.current_analyzer.get_readme_content()
            self.project_description.setText(readme_content)
            
            # Get project files
            source_files = self.current_analyzer.get_source_files()
            data_files = self.current_analyzer.get_data_files()
            macro_files = self.current_analyzer.get_macro_files()
            
            # Update file lists
            self.update_file_lists(source_files, data_files, macro_files)
            
            # Enable buttons based on capabilities
            has_exe = self.current_project.executable is not None
            self.run_button.setEnabled(has_exe)
            self.analyze_button.setEnabled(bool(data_files))
            
    def create_file_browser(self):
        """Create file browser"""
        self.file_browser = QWidget()
        layout = QVBoxLayout()
        
        # Create tree structure
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type", "Size"])
        layout.addWidget(self.file_tree)
        
        self.file_browser.setLayout(layout)
        
    def update_file_lists(self, source_files, data_files, macro_files):
        """Update file lists"""
        # Clear existing items
        self.file_tree.clear()
        
        # Add source files
        for file in source_files:
            item = QTreeWidgetItem([file.name, "Source", str(file.stat().st_size)])
            self.file_tree.addTopLevelItem(item)
            
        # Add data files
        for file in data_files:
            item = QTreeWidgetItem([file.name, "Data", str(file.stat().st_size)])
            self.file_tree.addTopLevelItem(item)
            
        # Add macro files
        for file in macro_files:
            item = QTreeWidgetItem([file.name, "Macro", str(file.stat().st_size)])
            self.file_tree.addTopLevelItem(item)
            
    def run_selected_project(self):
        """Run selected project"""
        if not self.current_project:
            return
            
        try:
            self.status_label.setText(f"Running {self.current_project.name}...")
            # Add actual project execution logic here
            QMessageBox.information(self, "Project Run", 
                                  f"Project '{self.current_project.name}' would be executed here.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run project: {str(e)}")
            
    def analyze_selected_project(self):
        """Analyze selected project's data"""
        if not self.current_project:
            return
            
        try:
            # Get analysis configuration
            config = self.current_analyzer.get_analysis_configuration()
            
            # Process data files
            data_files = self.current_analyzer.get_data_files()
            if not data_files:
                self.status_label.setText("No data files found")
                self.status_label.setStyleSheet(f"color: {self.colors['error']};")
                return
                
            # Switch to analysis tab
            self.content_stack.setCurrentIndex(2)
            
        except Exception as e:
            self.status_label.setText(f"Analysis error: {str(e)}")
            self.status_label.setStyleSheet(f"color: {self.colors['error']};")

    def show_projects(self):
        """Switch to projects tab"""
        self.content_stack.setCurrentIndex(0)
        
    def show_simulation(self):
        """Switch to simulation tab"""
        self.content_stack.setCurrentIndex(1)
        
    def show_analysis(self):
        """Switch to analysis tab"""
        self.content_stack.setCurrentIndex(2)

    def show_canvas(self):
        """Switch to visual editor tab"""
        self.content_stack.setCurrentIndex(3)
        
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", 
                              "Settings module not yet implemented.")
                              
    def create_header_buttons(self):
        """Create header action buttons"""
        button_layout = QHBoxLayout()
        
        # Back button (plain text - no emoji)
        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors['background']};
                background-color: {self.colors['blue']};
                border: 2px solid {self.colors['gray']};
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 8px 16px;
            }}
        """)
        back_btn.clicked.connect(self.return_to_selector)
        button_layout.addWidget(back_btn)

        # Lock button (plain text)
        lock_btn = QPushButton("LOCK")
        lock_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors['background']};
                background-color: {self.colors['error']};
                border: 2px solid {self.colors['gray']};
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 8px 16px;
            }}
        """)
        lock_btn.clicked.connect(self.lock_interface)
        button_layout.addWidget(lock_btn)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        return button_layout
            
    def return_to_selector(self):
        """Return to interface selector"""
        if self.selector:
            self.selector.show()
            self.close()
            
    def lock_interface(self):
        """Lock interface (simplified)"""
        QMessageBox.information(self, "Lock", "Interface lock not yet implemented.")

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        margin = 24
        block_h = 140
        # --- Верхній блок (хронометр + дисплей) ---
        chrono_rect = QRectF(margin, margin, 60, block_h)
        painter.setPen(QPen(QColor(self.colors['gray']), 4))
        painter.setBrush(QColor(self.colors['background']))
        painter.drawRect(chrono_rect)
        # Кнопки (SWT, CNV, DSP, SET)
        btn_h = 32
        btn_w = 48
        btn_margin = 10
        btn_labels = ["SWT", "CNV", "DSP", "SET"]
        btn_colors = [self.colors['blue'], self.colors['blue'], self.colors['yellow'], self.colors['gray']]
        for i, (lbl, col) in enumerate(zip(btn_labels, btn_colors)):
            y = margin + 10 + i*(btn_h+btn_margin)
            btn_rect = QRectF(margin+6, y, btn_w, btn_h)
            painter.setPen(QPen(QColor(self.colors['gray']), 2))
            painter.setBrush(QColor(col))
            painter.drawRect(btn_rect)
            painter.setPen(QColor(self.colors['white']))
            painter.setFont(QFont('Courier New', 12, QFont.Weight.Bold))
            painter.drawText(btn_rect, Qt.AlignmentFlag.AlignCenter, lbl)
        # Вертикальний напис CHRONOMETER
        painter.save()
        painter.setPen(QColor(self.colors['white']))
        painter.setFont(QFont('Courier New', 11, QFont.Weight.Bold))
        painter.translate(margin+chrono_rect.width()/2, margin+block_h/2)
        painter.rotate(-90)
        painter.drawText(QRectF(-block_h/2, -30, block_h, 20), Qt.AlignmentFlag.AlignCenter, "CHRONOMETER")
        painter.restore()
        # Дисплей (праворуч)
        disp_rect = QRectF(margin+chrono_rect.width()+20, margin, w-margin*2-chrono_rect.width()-20, block_h)
        painter.setPen(QPen(QColor(self.colors['gray']), 4))
        painter.setBrush(QColor(self.colors['background']))
        painter.drawRect(disp_rect)
        # Текст дисплея
        painter.setPen(QColor(self.colors['white']))
        painter.setFont(QFont('Courier New', 28, QFont.Weight.Bold))
        painter.drawText(disp_rect.adjusted(0,10,0,-60), Qt.AlignmentFlag.AlignHCenter, "STARDATE:")
        painter.setFont(QFont('Courier New', 32, QFont.Weight.Bold))
        painter.drawText(disp_rect.adjusted(0,40,0,-20), Qt.AlignmentFlag.AlignHCenter, "-37555.53415")
        painter.setFont(QFont('Courier New', 18, QFont.Weight.Bold))
        painter.drawText(disp_rect.adjusted(0,90,0,0), Qt.AlignmentFlag.AlignHCenter, "EPOCH: -1")

        # --- Нижній блок (панель конвертації + grid) ---
        grid_top = margin+block_h+30
        conv_rect = QRectF(margin, grid_top, 120, h-grid_top-margin)
        painter.setPen(QPen(QColor(self.colors['gray']), 4))
        painter.setBrush(QColor(self.colors['background']))
        painter.drawRect(conv_rect)
        # Convert LED
        painter.setBrush(QColor(self.colors.get('success', '#00FF00')))
        painter.setPen(QPen(QColor(self.colors['gray']), 2))
        painter.drawEllipse(int(conv_rect.left()+10), int(conv_rect.top()+10), 16, 16)
        # Convert label
        painter.setPen(QColor(self.colors['white']))
        painter.setFont(QFont('Courier New', 12, QFont.Weight.Bold))
        painter.drawText(QRectF(conv_rect.left(), conv_rect.top()+30, conv_rect.width(), 30), Qt.AlignmentFlag.AlignHCenter, "Convert:")
        painter.setFont(QFont('Courier New', 11, QFont.Weight.Normal))
        painter.drawText(QRectF(conv_rect.left(), conv_rect.top()+55, conv_rect.width(), 20), Qt.AlignmentFlag.AlignHCenter, "UTC +0.0")

        # --- GRID ---
        grid_rect = QRectF(conv_rect.right()+20, grid_top, w-margin-conv_rect.width()-margin-20, h-grid_top-margin)
        painter.setPen(QPen(QColor(self.colors['gray']), 4))
        painter.setBrush(QColor(self.colors['background']))
        painter.drawRect(grid_rect)
        # Grid lines (3 rows x 4 cols)
        rows, cols = 3, 4
        cell_w = grid_rect.width()/cols
        cell_h = grid_rect.height()/rows
        painter.setPen(QPen(QColor(self.colors['grid']), 2))
        for i in range(1, cols):
            x = grid_rect.left() + i*cell_w
            painter.drawLine(int(x), int(grid_rect.top()), int(x), int(grid_rect.bottom()))
        for j in range(1, rows):
            y = grid_rect.top() + j*cell_h
            painter.drawLine(int(grid_rect.left()), int(y), int(grid_rect.right()), int(y))
        # Заповнення блоків (жовтий/блакитний)
        block_data = [
            (0,0,"2161","YEAR",self.colors['yellow']),
            (0,1,"1","MONTH",self.colors['yellow']),
            (0,2,"1","DAY",self.colors['yellow']),
            (0,3,"03-452","CNV TIME",self.colors['blue']),
            (1,0,"00","HOUR",self.colors['yellow']),
            (1,1,"00","MINUTE",self.colors['yellow']),
            (1,2,"00","SECONDS",self.colors['yellow']),
            (1,3,"05-254","CNV STRDT",self.colors['blue']),
            (2,0,"0","STARDATE",self.colors['blue']),
            (2,1,"0","EPOCH",self.colors['blue']),
        ]
        for row, col, val, label, color in block_data:
            cell = QRectF(grid_rect.left()+col*cell_w+2, grid_rect.top()+row*cell_h+2, cell_w-4, cell_h-4)
            painter.setPen(QPen(QColor(self.colors['gray']), 2))
            painter.setBrush(QColor(color))
            painter.drawRect(cell)
            painter.setPen(QColor(self.colors['background'] if color==self.colors['yellow'] else self.colors['white']))
            painter.setFont(QFont('Courier New', 18, QFont.Weight.Bold))
            painter.drawText(cell.adjusted(0,8,0,-24), Qt.AlignmentFlag.AlignHCenter, val)
            painter.setFont(QFont('Courier New', 10, QFont.Weight.Normal))
            painter.drawText(cell.adjusted(0,30,0,0), Qt.AlignmentFlag.AlignHCenter, label)

def main():
    app = QApplication(sys.argv)
    
    # Generic root path
    current_file = Path(__file__).resolve()
    root_path = current_file.parents[2]
    
    interface = PCARS22ndCentury(root_path)
    interface.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
