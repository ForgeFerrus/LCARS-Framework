"""
NX-01 Enterprise Desktop Interface
Authentic 22nd Century Full Desktop Environment
Based on original NX-01 Master Systems Display
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import random
import time
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, 
                           QApplication, QGridLayout, QProgressBar, QStackedWidget)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF, pyqtSignal

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class NXButton(QPushButton):
    """NX-style rectangular button with corner indicator and specific color"""
    def __init__(self, text, color="#269EEE", parent=None):
        super().__init__(text, parent)
        self.btn_color = color
        self.setMinimumHeight(35)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Hover effect
        bg_color = QColor(self.btn_color)
        if self.underMouse():
            bg_color = bg_color.lighter(120)
        if self.isDown():
            bg_color = bg_color.darker(120)
            
        # Draw main button
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawRect(rect)
        
        # Indicator Square
        indicator_size = 6
        ind_rect = QRectF(rect.right() - indicator_size - 4, rect.top() + 4, indicator_size, indicator_size)
        painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
        painter.drawRect(ind_rect)
        
        # Text
        painter.setPen(QColor("#000000"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class NXPillPanel(QFrame):
    """NX-style silver panel with CAP ends (pill geometry)"""
    def __init__(self, side="left", color="#CCCCCC", text="", parent=None):
        super().__init__(parent)
        self.side = side  # left, top, bottom, right
        self.panel_color = color
        self.label_text = text
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        path = QPainterPath()
        radius = 20
        
        if self.side == "left":
            # Left rounded
            path.moveTo(radius, 0)
            path.lineTo(rect.width(), 0)
            path.lineTo(rect.width(), rect.height())
            path.lineTo(radius, rect.height())
            path.quadTo(0, rect.height(), 0, rect.height() - radius)
            path.lineTo(0, radius)
            path.quadTo(0, 0, radius, 0)
        else:
            # Regular rectangle for now
            path.addRect(rect)
            
        painter.fillPath(path, QBrush(QColor(self.panel_color)))
        painter.setPen(QPen(QColor("#444444"), 2))
        painter.drawPath(path)
        
        # Draw text vertically if provided
        if self.label_text:
            painter.save()
            painter.setPen(QColor("#000000"))
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            if self.side == "left":
                painter.translate(rect.width() // 2, rect.height() // 2)
                painter.rotate(-90)
                painter.drawText(-100, 0, self.label_text)
            painter.restore()

class NXStatusPanel(QFrame):
    """NX-style status display panel"""
    def __init__(self, title="STATUS", parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 110)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #CCCCCC;
                background: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; 
            color: #888888; 
            border: none;
        """)
        
        self.value_label = QLabel("NOMINAL")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            font-size: 42px; 
            font-weight: bold; 
            color: #FFFFFF; 
            border: none;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        
    def update_value(self, value):
        self.value_label.setText(value)

class NX01Desktop(QMainWindow):
    """NX-01 Enterprise Desktop Interface - Full Implementation"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_nx_desktop()
        
        # Update timer for stardate and system status
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(1000)  # Update every second
        
    def setup_nx_desktop(self):
        """Setup full NX-01 Enterprise desktop interface"""
        self.setWindowTitle("NX-01 Enterprise Master Systems Display")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # NX-01 styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A1A;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Arial', sans-serif;
            }
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # LEFT NAVIGATION PANEL
        self.setup_navigation()
        
        # CENTER/RIGHT CONTENT
        self.setup_content_area()
        
        # Initialize current stardate
        self.current_stardate = -2151.5
        
    def setup_navigation(self):
        """Setup left navigation with NX-style pill panel"""
        self.nav_area = QWidget()
        self.nav_area.setFixedWidth(220)
        nav_layout = QVBoxLayout(self.nav_area)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main navigation pill
        self.nav_pill = NXPillPanel(side="left", color="#CCCCCC", text="NX-01 ENTERPRISE COMMAND")
        pill_layout = QVBoxLayout(self.nav_pill)
        pill_layout.setContentsMargins(10, 50, 10, 20)
        
        # Blue status indicator at top
        indicator = QLabel()
        indicator.setFixedSize(40, 40)
        indicator.setStyleSheet("""
            background-color: #269EEE; 
            border-radius: 20px; 
            border: 2px solid #444444;
        """)
        pill_layout.addWidget(indicator, 0, Qt.AlignmentFlag.AlignCenter)
        pill_layout.addSpacing(100)  # Space for vertical text
        
        # Main navigation buttons
        self.btn_projects = NXButton("PROJECTS", "#FFE600")
        self.btn_science = NXButton("SCIENCE", "#269EEE") 
        self.btn_engineering = NXButton("ENGINEERING", "#5C5C5C")
        self.btn_tactical = NXButton("TACTICAL", "#CE6363")
        
        # Connect navigation
        self.btn_projects.clicked.connect(lambda: self.switch_panel(0))
        self.btn_science.clicked.connect(lambda: self.switch_panel(1))
        self.btn_engineering.clicked.connect(lambda: self.switch_panel(2))
        self.btn_tactical.clicked.connect(lambda: self.switch_panel(3))
        
        for btn in [self.btn_projects, self.btn_science, self.btn_engineering, self.btn_tactical]:
            pill_layout.addWidget(btn)
            
        pill_layout.addStretch()
        
        # System controls at bottom
        btn_logout = NXButton("LOGOUT", "#CE6363")
        btn_logout.clicked.connect(self.logout)
        btn_shutdown = NXButton("SHUTDOWN", "#CE6363")
        btn_shutdown.clicked.connect(self.close)
        
        pill_layout.addWidget(btn_logout)
        pill_layout.addWidget(btn_shutdown)
        
        nav_layout.addWidget(self.nav_pill)
        self.main_layout.addWidget(self.nav_area)
        
    def setup_content_area(self):
        """Setup main content area with header and panels"""
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # HEADER with status displays
        header_layout = QHBoxLayout()
        
        # Stardate display
        self.stardate_panel = NXStatusPanel("STARDATE")
        header_layout.addWidget(self.stardate_panel)
        
        header_layout.addStretch()
        
        # Ship status display
        self.status_panel = NXStatusPanel("SHIP STATUS")
        header_layout.addWidget(self.status_panel)
        
        # System alerts display
        self.alerts_panel = NXStatusPanel("ALERTS")
        header_layout.addWidget(self.alerts_panel)
        
        self.content_layout.addLayout(header_layout)
        
        # MAIN CONTENT STACK
        self.content_stack = QStackedWidget()
        
        # Create different panels
        self.setup_projects_panel()
        self.setup_science_panel() 
        self.setup_engineering_panel()
        self.setup_tactical_panel()
        
        self.content_layout.addWidget(self.content_stack)
        self.main_layout.addWidget(content_widget)
        
        # Start with projects panel
        self.content_stack.setCurrentIndex(0)
        
    def setup_projects_panel(self):
        """Setup projects management panel"""
        projects_widget = QFrame()
        projects_widget.setStyleSheet("""
            QFrame {
                border: 2px solid #269EEE;
                background: rgba(38, 158, 238, 0.1);
            }
        """)
        
        layout = QVBoxLayout(projects_widget)
        
        title = QLabel("ENTERPRISE PROJECT MANAGEMENT")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #269EEE; 
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Project list
        project_frame = QFrame()
        project_frame.setStyleSheet("""
            QFrame { 
                border: 1px solid #444; 
                background: #000; 
                padding: 10px; 
            }
        """)
        project_layout = QVBoxLayout(project_frame)
        
        projects = [
            "Deep Space Exploration Mission Alpha-7",
            "Warp Engine Efficiency Analysis", 
            "First Contact Protocol Development",
            "Xenobiology Research Initiative",
            "Subspace Communication Array"
        ]
        
        for project in projects:
            proj_btn = NXButton(project, "#FFE600")
            proj_btn.setMinimumHeight(40)
            project_layout.addWidget(proj_btn)
            
        layout.addWidget(project_frame)
        self.content_stack.addWidget(projects_widget)
        
    def setup_science_panel(self):
        """Setup science systems panel"""
        science_widget = QFrame()
        science_widget.setStyleSheet("""
            QFrame {
                border: 2px solid #269EEE;
                background: rgba(38, 158, 238, 0.1);
            }
        """)
        
        layout = QVBoxLayout(science_widget)
        
        title = QLabel("SCIENCE & SENSOR SYSTEMS")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #269EEE; 
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Science controls grid
        controls_frame = QFrame()
        controls_layout = QGridLayout(controls_frame)
        
        science_systems = [
            ("LONG RANGE SENSORS", "#269EEE"),
            ("STELLAR CARTOGRAPHY", "#5C5C5C"), 
            ("ASTROMETRICS", "#FFE600"),
            ("BIOLOGICAL SCANS", "#CE6363"),
            ("SUBSPACE ANALYSIS", "#269EEE"),
            ("TEMPORAL STUDIES", "#5C5C5C")
        ]
        
        row, col = 0, 0
        for system, color in science_systems:
            btn = NXButton(system, color)
            btn.setMinimumHeight(60)
            controls_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addWidget(controls_frame)
        self.content_stack.addWidget(science_widget)
        
    def setup_engineering_panel(self):
        """Setup engineering systems panel"""
        eng_widget = QFrame()
        eng_widget.setStyleSheet("""
            QFrame {
                border: 2px solid #CE6363;
                background: rgba(206, 99, 99, 0.1);
            }
        """)
        
        layout = QVBoxLayout(eng_widget)
        
        title = QLabel("ENGINEERING & PROPULSION")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #CE6363; 
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Engineering status
        status_layout = QHBoxLayout()
        
        warp_status = NXStatusPanel("WARP CORE")
        warp_status.update_value("ONLINE")
        status_layout.addWidget(warp_status)
        
        impulse_status = NXStatusPanel("IMPULSE")  
        impulse_status.update_value("READY")
        status_layout.addWidget(impulse_status)
        
        layout.addLayout(status_layout)
        self.content_stack.addWidget(eng_widget)
        
    def setup_tactical_panel(self):
        """Setup tactical systems panel"""
        tac_widget = QFrame()
        tac_widget.setStyleSheet("""
            QFrame {
                border: 2px solid #CE6363;
                background: rgba(206, 99, 99, 0.1);
            }
        """)
        
        layout = QVBoxLayout(tac_widget)
        
        title = QLabel("TACTICAL & DEFENSE SYSTEMS")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #CE6363; 
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tactical controls
        tac_controls = QGridLayout()
        
        systems = [
            ("PHASE CANNONS", "#CE6363"),
            ("PHOTONIC TORPEDOES", "#FFE600"),
            ("POLARIZED HULL PLATING", "#269EEE"),
            ("DEFLECTOR ARRAY", "#5C5C5C")
        ]
        
        row, col = 0, 0
        for system, color in systems:
            btn = NXButton(system, color)
            btn.setMinimumHeight(80)
            tac_controls.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(tac_controls)
        self.content_stack.addWidget(tac_widget)
        
    def switch_panel(self, index):
        """Switch to specified content panel"""
        self.content_stack.setCurrentIndex(index)
        
        # Update button states
        buttons = [self.btn_projects, self.btn_science, self.btn_engineering, self.btn_tactical]
        colors = ["#FFE600", "#269EEE", "#5C5C5C", "#CE6363"]
        
        for i, (btn, color) in enumerate(zip(buttons, colors)):
            if i == index:
                btn.btn_color = color
            else:
                btn.btn_color = "#888888"  # Dimmed when not active
            btn.update()
            
    def update_displays(self):
        """Update stardate and system displays"""
        # Update stardate
        self.current_stardate += 0.001
        self.stardate_panel.update_value(f"{self.current_stardate:.2f}")
        
        # Update ship status
        status_options = ["NOMINAL", "OPTIMAL", "GREEN", "READY"]
        self.status_panel.update_value(random.choice(status_options))
        
        # Update alerts
        alert_options = ["NONE", "LOW", "MINIMAL", "CLEAR"]
        self.alerts_panel.update_value(random.choice(alert_options))
        
    def logout(self):
        """Logout and return to faction selection"""
        print("🚪 Logging out of NX-01 Enterprise system...")
        self.authentication_success.emit()  # Signal logout
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    desktop = NX01Desktop()
    desktop.show()
    sys.exit(app.exec())
