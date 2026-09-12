"""
LCARS 24th Century Desktop Interface  
Authentic TNG/DS9/VOY Era Full Desktop Environment
Based on original LCARS prototypes
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

if True:
    from lcars.themes.lcars_palette import get_era_palette, get_random_button_color, LCARSEra
if False: # Removed except block
    print("Could not import LCARS palette system")

class LCARSButton(QPushButton):
    """Authentic LCARS button with proper styling"""
    def __init__(self, text, color="#FFCC66", parent=None):
        super().__init__(text, parent)
        self.lcars_color = color
        self.setMinimumHeight(40)
        self.setFont(QFont("Antonio", 12, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # LCARS rounded rectangle
        bg_color = QColor(self.lcars_color)
        if self.underMouse():
            bg_color = bg_color.lighter(120)
        if self.isDown():
            bg_color = bg_color.darker(120)
            
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawRoundedRect(rect, 20, 20)
        
        # Draw text
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Antonio", 12, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class LCARSStatusPanel(QFrame):
    """LCARS-style status display panel"""
    def __init__(self, title="STATUS", color="#FFCC66", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.panel_color = color
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold;
            color: #000000; 
            border: none;
        """)
        
        self.value_label = QLabel("NOMINAL")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #000000; 
            border: none;
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        
    def update_value(self, value):
        self.value_label.setText(value)
        
    def update_color(self, color):
        self.panel_color = color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 20px;
            }}
        """)

class LCARS24thDesktop(QMainWindow):
    """24th Century LCARS Desktop Interface - Full Implementation"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_lcars_desktop()
        
        # Get LCARS colors
        if True:
            self.colors = get_era_palette(LCARSEra.LCARS_24TH)
        if False: # Removed except block
            self.colors = {
                'bg': '#000000',
                'txt': '#FFFFFF', 
                'btn1': '#FFCC66',
                'btn2': '#FF9900',
                'btn3': '#CC6666',
                'btn4': '#664466',
                'btn5': '#66CCFF'
            }
        
        # Update timer for dynamic colors and displays
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Current stardate
        self.current_stardate = 47315.6
        
    def setup_lcars_desktop(self):
        """Setup full LCARS desktop interface"""
        self.setWindowTitle("LCARS - Library Computer Access/Retrieval System")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # LCARS styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors.get('bg', '#000000')};
                color: {self.colors.get('txt', '#FFFFFF')};
            }}
            QLabel {{
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Antonio', 'Swiss 911', 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # LCARS HEADER
        self.setup_header()
        
        # MAIN CONTENT AREA
        content_widget = QWidget()
        self.content_layout = QHBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # LEFT NAVIGATION PANEL
        self.setup_navigation()
        
        # CENTER DISPLAY
        self.setup_center_display()
        
        # RIGHT PANEL
        self.setup_right_panel()
        
        self.main_layout.addWidget(content_widget)
        
        # LCARS FOOTER
        self.setup_footer()
        
    def setup_header(self):
        """Setup LCARS header with title and status"""
        self.header_panel = QFrame()
        self.header_panel.setFixedHeight(100)
        self.header_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border-bottom: 4px solid {self.colors.get('btn1', '#FFCC66')};
            }}
        """)
        
        header_layout = QHBoxLayout(self.header_panel)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # LCARS Title
        lcars_title = QLabel("LCARS")
        lcars_title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: #000000;
            background-color: {self.colors.get('btn1', '#FFCC66')};
            padding: 10px 20px;
            border-radius: 25px;
        """)
        header_layout.addWidget(lcars_title)
        
        # Center title
        center_title = QLabel("STARFLEET COMMAND INTERFACE")
        center_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)
        header_layout.addWidget(center_title)
        
        # Stardate display
        self.stardate_display = LCARSStatusPanel("STARDATE", self.colors.get('btn2', '#FF9900'))
        header_layout.addWidget(self.stardate_display)
        
        self.main_layout.addWidget(self.header_panel)
        
    def setup_navigation(self):
        """Setup left LCARS navigation panel"""
        self.nav_panel = QFrame()
        self.nav_panel.setFixedWidth(250)
        self.nav_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border-right: 2px solid {self.colors.get('btn1', '#FFCC66')};
            }}
        """)
        
        nav_layout = QVBoxLayout(self.nav_panel)
        nav_layout.setContentsMargins(20, 20, 20, 20)
        nav_layout.setSpacing(15)
        
        # Navigation title
        nav_title = QLabel("NAVIGATION")
        nav_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {self.colors.get('btn1', '#FFCC66')};
            padding: 10px;
            border: 2px solid {self.colors.get('btn1', '#FFCC66')};
            border-radius: 10px;
        """)
        nav_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(nav_title)
        
        # Main navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("COMMAND", self.colors.get('btn1', '#FFCC66')),
            ("OPERATIONS", self.colors.get('btn2', '#FF9900')),
            ("SCIENCE", self.colors.get('btn5', '#66CCFF')),
            ("ENGINEERING", self.colors.get('btn3', '#CC6666')),
            ("TACTICAL", self.colors.get('btn4', '#664466')),
            ("COMMUNICATIONS", self.colors.get('btn1', '#FFCC66'))
        ]
        
        for i, (label, color) in enumerate(nav_items):
            btn = LCARSButton(label, color)
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, idx=i: self.switch_panel(idx))
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
            
        nav_layout.addStretch()
        
        # System status panels
        self.warp_status = LCARSStatusPanel("WARP CORE", self.colors.get('btn5', '#66CCFF'))
        self.shields_status = LCARSStatusPanel("SHIELDS", self.colors.get('btn3', '#CC6666'))
        
        nav_layout.addWidget(self.warp_status)
        nav_layout.addWidget(self.shields_status)
        
        # Logout button
        logout_btn = LCARSButton("LOGOUT", "#CE6363")
        logout_btn.setMinimumHeight(60)
        logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(logout_btn)
        
        self.content_layout.addWidget(self.nav_panel)
        
    def setup_center_display(self):
        """Setup center main display area"""
        self.center_panel = QFrame()
        self.center_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border: 2px solid {self.colors.get('btn1', '#FFCC66')};
                border-radius: 10px;
                margin: 10px;
            }}
        """)
        
        center_layout = QVBoxLayout(self.center_panel)
        center_layout.setContentsMargins(20, 20, 20, 20)
        
        # Content stack for different panels
        self.content_stack = QStackedWidget()
        
        # Create different interface panels
        self.setup_command_panel()
        self.setup_operations_panel()
        self.setup_science_panel()
        self.setup_engineering_panel()
        self.setup_tactical_panel()
        self.setup_communications_panel()
        
        center_layout.addWidget(self.content_stack)
        self.content_layout.addWidget(self.center_panel)
        
        # Start with command panel
        self.content_stack.setCurrentIndex(0)
        
    def setup_right_panel(self):
        """Setup right LCARS status panel"""
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(200)
        self.right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border-left: 2px solid {self.colors.get('btn1', '#FFCC66')};
            }}
        """)
        
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(15, 20, 15, 20)
        right_layout.setSpacing(15)
        
        # Status title
        status_title = QLabel("STATUS")
        status_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {self.colors.get('btn1', '#FFCC66')};
            padding: 10px;
            border: 2px solid {self.colors.get('btn1', '#FFCC66')};
            border-radius: 10px;
        """)
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(status_title)
        
        # Status panels
        self.life_support = LCARSStatusPanel("LIFE SUPPORT", self.colors.get('btn5', '#66CCFF'))
        self.power_status = LCARSStatusPanel("MAIN POWER", self.colors.get('btn1', '#FFCC66'))
        self.sensors_status = LCARSStatusPanel("SENSORS", self.colors.get('btn2', '#FF9900'))
        self.comms_status = LCARSStatusPanel("COMMS", self.colors.get('btn4', '#664466'))
        
        for panel in [self.life_support, self.power_status, self.sensors_status, self.comms_status]:
            right_layout.addWidget(panel)
            
        right_layout.addStretch()
        self.content_layout.addWidget(self.right_panel)
        
    def setup_footer(self):
        """Setup LCARS footer"""
        self.footer_panel = QFrame()
        self.footer_panel.setFixedHeight(80)
        self.footer_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border-top: 4px solid {self.colors.get('btn1', '#FFCC66')};
            }}
        """)
        
        footer_layout = QHBoxLayout(self.footer_panel)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        # System info
        system_info = QLabel("USS ENTERPRISE NCC-1701-D • GALAXY CLASS STARSHIP")
        system_info.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)
        footer_layout.addWidget(system_info)
        
        footer_layout.addStretch()
        
        # Quick access buttons
        quick_buttons = [
            ("RED ALERT", "#CE6363"),
            ("YELLOW ALERT", "#FFE600"),
            ("ALL STOP", "#888888")
        ]
        
        for label, color in quick_buttons:
            btn = LCARSButton(label, color)
            btn.setMinimumHeight(40)
            footer_layout.addWidget(btn)
            
        self.main_layout.addWidget(self.footer_panel)
        
    def setup_command_panel(self):
        """Setup command interface panel"""
        command_widget = QFrame()
        layout = QVBoxLayout(command_widget)
        
        title = QLabel("BRIDGE COMMAND INTERFACE")
        title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: bold; 
            color: {self.colors.get('btn1', '#FFCC66')}; 
            padding: 15px;
            border: 2px solid {self.colors.get('btn1', '#FFCC66')};
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Command grid
        command_grid = QGridLayout()
        commands = [
            ("MAIN VIEWER", self.colors.get('btn1', '#FFCC66')),
            ("HELM CONTROL", self.colors.get('btn2', '#FF9900')),
            ("TACTICAL STATUS", self.colors.get('btn3', '#CC6666')),
            ("SHIP'S LOGS", self.colors.get('btn4', '#664466')),
            ("CREW REPORTS", self.colors.get('btn5', '#66CCFF')),
            ("MISSION BRIEF", self.colors.get('btn1', '#FFCC66'))
        ]
        
        row, col = 0, 0
        for cmd, color in commands:
            btn = LCARSButton(cmd, color)
            btn.setMinimumHeight(80)
            command_grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(command_grid)
        layout.addStretch()
        self.content_stack.addWidget(command_widget)
        
    def setup_operations_panel(self):
        """Setup operations panel"""
        ops_widget = QFrame()
        layout = QVBoxLayout(ops_widget)
        
        title = QLabel("OPERATIONS MANAGEMENT")
        title.setStyleSheet(f"""
            font-size: 28px; 
            color: {self.colors.get('btn2', '#FF9900')}; 
            padding: 15px;
            border: 2px solid {self.colors.get('btn2', '#FF9900')};
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        ops_list = QListWidget()
        ops_list.setStyleSheet(f"""
            QListWidget {{
                background-color: rgba(0, 0, 0, 0.8);
                border: 2px solid {self.colors.get('btn2', '#FF9900')};
                color: {self.colors.get('txt', '#FFFFFF')};
                font-size: 16px;
                padding: 10px;
            }}
        """)
        
        operations = [
            "• Duty Shift Alpha - Active",
            "• Replicator Systems - Online",
            "• Transporters 1-6 - Operational", 
            "• Holodeck 1-4 - Available",
            "• Shuttle Bay Operations - Normal",
            "• Environmental Systems - Nominal"
        ]
        
        for op in operations:
            ops_list.addItem(op)
            
        layout.addWidget(ops_list)
        self.content_stack.addWidget(ops_widget)
        
    def setup_science_panel(self):
        """Setup science panel"""
        sci_widget = QFrame()
        layout = QVBoxLayout(sci_widget)
        
        title = QLabel("SCIENCE & RESEARCH")
        title.setStyleSheet(f"""
            font-size: 28px; 
            color: {self.colors.get('btn5', '#66CCFF')}; 
            padding: 15px;
            border: 2px solid {self.colors.get('btn5', '#66CCFF')};
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Science controls grid
        sci_grid = QGridLayout()
        systems = [
            ("LONG RANGE SENSORS", self.colors.get('btn5', '#66CCFF')),
            ("STELLAR CARTOGRAPHY", self.colors.get('btn1', '#FFCC66')),
            ("ASTROMETRICS", self.colors.get('btn2', '#FF9900')),
            ("LABORATORY ACCESS", self.colors.get('btn4', '#664466'))
        ]
        
        row, col = 0, 0
        for system, color in systems:
            btn = LCARSButton(system, color)
            btn.setMinimumHeight(100)
            sci_grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(sci_grid)
        layout.addStretch()
        self.content_stack.addWidget(sci_widget)
        
    def setup_engineering_panel(self):
        """Setup engineering panel"""
        eng_widget = QFrame()
        layout = QVBoxLayout(eng_widget)
        
        title = QLabel("ENGINEERING SYSTEMS")
        title.setStyleSheet(f"""
            font-size: 28px; 
            color: {self.colors.get('btn3', '#CC6666')}; 
            padding: 15px;
            border: 2px solid {self.colors.get('btn3', '#CC6666')};
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Engineering status display
        eng_status = QHBoxLayout()
        
        warp_panel = LCARSStatusPanel("WARP CORE", self.colors.get('btn5', '#66CCFF'))
        warp_panel.update_value("ONLINE")
        eng_status.addWidget(warp_panel)
        
        impulse_panel = LCARSStatusPanel("IMPULSE", self.colors.get('btn1', '#FFCC66'))
        impulse_panel.update_value("READY")
        eng_status.addWidget(impulse_panel)
        
        layout.addLayout(eng_status)
        layout.addStretch()
        self.content_stack.addWidget(eng_widget)
        
    def setup_tactical_panel(self):
        """Setup tactical panel"""
        tac_widget = QFrame()
        layout = QVBoxLayout(tac_widget)
        
        title = QLabel("TACTICAL SYSTEMS")
        title.setStyleSheet(f"""
            font-size: 28px; 
            color: {self.colors.get('btn4', '#664466')}; 
            padding: 15px;
            border: 2px solid {self.colors.get('btn4', '#664466')};
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tactical controls
        tac_grid = QGridLayout()
        systems = [
            ("PHASER ARRAYS", self.colors.get('btn3', '#CC6666')),
            ("PHOTON TORPEDOES", self.colors.get('btn1', '#FFCC66')),
            ("DEFLECTOR SHIELDS", self.colors.get('btn5', '#66CCFF')),
            ("THREAT ASSESSMENT", self.colors.get('btn4', '#664466'))
        ]
        
        row, col = 0, 0
        for system, color in systems:
            btn = LCARSButton(system, color)
            btn.setMinimumHeight(100)
            tac_grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(tac_grid)
        layout.addStretch()
        self.content_stack.addWidget(tac_widget)
        
    def setup_communications_panel(self):
        """Setup communications panel"""
        comm_widget = QFrame()
        layout = QVBoxLayout(comm_widget)
        
        title = QLabel("COMMUNICATIONS")
        title.setStyleSheet(f"""
            font-size: 28px; 
            color: {self.colors.get('btn1', '#FFCC66')}; 
            padding: 15px;
            border: 2px solid {self.colors.get('btn1', '#FFCC66')};
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Communications controls
        comm_grid = QGridLayout()
        systems = [
            ("SUBSPACE RADIO", self.colors.get('btn1', '#FFCC66')),
            ("HAIL FREQUENCIES", self.colors.get('btn2', '#FF9900')),
            ("EMERGENCY CHANNELS", self.colors.get('btn3', '#CC6666')),
            ("STARFLEET COMMAND", self.colors.get('btn5', '#66CCFF'))
        ]
        
        row, col = 0, 0
        for system, color in systems:
            btn = LCARSButton(system, color)
            btn.setMinimumHeight(100)
            comm_grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(comm_grid)
        layout.addStretch()
        self.content_stack.addWidget(comm_widget)
        
    def switch_panel(self, index):
        """Switch to specified content panel"""
        self.content_stack.setCurrentIndex(index)
        
        # Update navigation button states
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                # Keep original color for active button
                pass
            else:
                btn.lcars_color = "#888888"  # Dimmed when not active
            btn.update()
            
    def update_displays(self):
        """Update dynamic displays and colors"""
        # Update stardate
        self.current_stardate += 0.1
        self.stardate_display.update_value(f"{self.current_stardate:.1f}")
        
        # Update status panels with random colors from palette
        if True:
            colors = ['#FFCC66', '#FF9900', '#CC6666', '#664466', '#66CCFF', '#99CC99']
            
            # Randomly update some status panels
            if random.random() < 0.3:  # 30% chance
                self.warp_status.update_color(random.choice(colors))
            if random.random() < 0.3:
                self.shields_status.update_color(random.choice(colors))
            if random.random() < 0.2:
                self.life_support.update_color(random.choice(colors))
                
        if False: # Removed except block
            pass  # Fallback if color system fails
            
        # Update system status values
        status_values = ["NOMINAL", "OPTIMAL", "ONLINE", "READY", "ACTIVE"]
        self.warp_status.update_value(random.choice(status_values))
        self.shields_status.update_value(f"{random.randint(95, 100)}%")
        self.life_support.update_value(random.choice(status_values))
        self.power_status.update_value(f"{random.randint(98, 100)}%")
        
    def logout(self):
        """Logout and return to authentication"""
        print("🚪 Logging out of LCARS system...")
        self.authentication_success.emit()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    desktop = LCARS24thDesktop()
    desktop.show()
    sys.exit(app.exec())
