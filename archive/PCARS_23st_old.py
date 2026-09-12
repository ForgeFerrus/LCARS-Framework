"""
LCARS PCARS 23st Interface - Late 23rd Century
Clean PCARS design based on your photos
"""

import sys
import os
from pathlib import Path

# Add project path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, 
                            QHBoxLayout, QListWidget, QTableWidget, 
                            QTableWidgetItem, QTreeView, QApplication)
from PyQt6.QtGui import (QFont, QPainter, QColor, QPen, QFileSystemModel)
from PyQt6.QtCore import Qt, QTimer


    # Fallback colors
def get_palette_by_name(name): 
        return {"background": "#000000", "accent1": "#FFE600", "accent2": "#FF0000", "accent3": "#00FF00"}
def get_random_button_color(era=None): return "#FFE600"
class LCARSEra: pass

class PCARS23stButton(QWidget):
    """PCARS 23st button - refined design from your photos"""
    
    def __init__(self, color, text=None, width=80, height=40, parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.setFixedSize(width, height)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle with PCARS style
        painter.setPen(QPen(QColor("#000"), 2))
        painter.setBrush(QColor(self.color))
        painter.drawRoundedRect(2, 2, self.width()-4, self.height()-4, 4, 4)
        
        # Draw text
        if self.text:
            painter.setPen(QColor("#000"))
            font = QFont("Arial", 11, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)


class PCARS23stCircle(QWidget):
    """PCARS 23st circle indicator - from your photos"""
    
    def __init__(self, color, text=None, size=30, parent=None):
        super().__init__(parent)
        self.color = color
        self.text = text
        self.setFixedSize(size, size)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        painter.setPen(QPen(QColor("#000"), 2))
        painter.setBrush(QColor(self.color))
        radius = min(self.width(), self.height()) // 2 - 2
        center = self.rect().center()
        painter.drawEllipse(center, radius, radius)
        
        # Draw text
        if self.text:
            painter.setPen(QColor("#000"))
            font = QFont("Arial", 9, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)


class PCARS23stFullButton(QWidget):
    """PCARS 23st full button with dynamic colors"""
    
    def __init__(self, label='NAME', number='00-23ST', width=180, height=54, color=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.label = label
        self.number = number
        
        # Dynamic color from algorithm
        self.dynamic_color = color or get_random_button_color()
        
        # Color change timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(3000)
        
        # Create components
        self.bg = PCARS23stButton(self.dynamic_color, number, width, height, self)
        self.bg.move(0, 0)
        
        self.text_label = QLabel(label, self)
        self.text_label.setStyleSheet("color: #000; font-size: 13px; font-weight: bold; background: transparent;")
        self.text_label.setGeometry(0, int(height*0.7), width, int(height*0.3))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.setStyleSheet("background: transparent;")
    
    def update_color(self):
        self.dynamic_color = get_random_button_color()
        self.bg.color = self.dynamic_color
        self.bg.update()


class PCARS23stMiniButton(QWidget):
    """PCARS 23st mini button"""
    
    def __init__(self, label='MINI', size=48, color=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.label = label
        
        # Dynamic color from algorithm
        self.dynamic_color = color or get_random_button_color()
        
        # Color change timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(3000)
        
        # Create components
        self.bg = PCARS23stButton(self.dynamic_color, '', size, size, self)
        self.bg.move(0, 0)
        
        self.text_label = QLabel(label, self)
        self.text_label.setStyleSheet("color: #000; font-size: 9px; font-weight: bold; background: transparent;")
        self.text_label.setGeometry(0, int(size*0.6), size, int(size*0.4))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.setStyleSheet("background: transparent;")
    
    def update_color(self):
        self.dynamic_color = get_random_button_color()
        self.bg.color = self.dynamic_color
        self.bg.update()


class PCARS23stPanel(QWidget):
    """PCARS 23st panel - design from your photos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000000;")
        self.setMinimumSize(1200, 800)
        
        # Create components based on your photos
        self._create_components()
        # Set positions
        self.resizeEvent(None)
    
    def _create_components(self):
        # Top row of circles (from your photos)
        self.circles_top = []
        top_colors = ["#FFE600", "#FFE600", "#FFE600", "#319319", "#319319", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        top_texts = ["756", "305", "353", "319", "319", "234", "234", "234", "234"]
        for color, text in zip(top_colors, top_texts):
            self.circles_top.append(PCARS23stCircle(color, text, 25, self))
        
        # Red line (characteristic PCARS element)
        self.red_line = QWidget(self)
        self.red_line.setStyleSheet("background:#D80000;")
        
        # Top buttons row (STD, DAT, MOD, etc.)
        self.buttons_top = []
        button_colors = ["#FFE600", "#FFE600", "#FFE600", "#319319", "#319319", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        button_texts = ["STD", "DAT", "MOD", "ANA", "VIS", "REP", "FIL", "DIR", "SRC"]
        for color, text in zip(button_colors, button_texts):
            self.buttons_top.append(PCARS23stButton(color, text, 50, 30, self))
        
        # Labels (from your photos)
        self.label_top = QLabel("DISTRIBUTION RESERVE SUPPLIES", self)
        self.label_top.setStyleSheet("color:#D80000;font-size:16px;font-family:'Arial';font-weight:bold;background:transparent;")
        
        self.label_bottom = QLabel("OPERATIONAL PRIORITY ALLOCATIONS", self)
        self.label_bottom.setStyleSheet("color:#D80000;font-size:16px;font-family:'Arial';font-weight:bold;background:transparent;")
        
        # Middle buttons row (longer buttons with numbers)
        self.buttons_mid = []
        mid_colors = ["#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        mid_texts = ["234931", "45631", "998931", "734731", "0-0731", "76631", "676731", "45631"]
        for color, text in zip(mid_colors, mid_texts):
            self.buttons_mid.append(PCARS23stButton(color, text, 80, 35, self))
        
        # Bottom circles row
        self.circles_bottom = []
        bot_colors = ["#234", "#432", "#234", "#453", "#319", "#319", "#319", "#302"]
        bot_texts = ["234", "432", "234", "453", "319", "319", "319", "302"]
        for color, text in zip(bot_colors, bot_texts):
            self.circles_bottom.append(PCARS23stCircle(color, text, 25, self))
    
    def resizeEvent(self, event):
        # Layout based on your photos
        x_start = 50
        y_start = 50
        spacing = 35
        
        # Top circles
        for i, circle in enumerate(self.circles_top):
            circle.move(x_start + i*spacing, y_start - 35)
        
        # Red line
        self.red_line.setGeometry(x_start, y_start, 400, 4)
        
        # Top buttons
        for i, button in enumerate(self.buttons_top):
            button.move(x_start + i*60, y_start + 15)
        
        # Top label
        self.label_top.move(x_start, y_start + 55)
        
        # Middle buttons
        for i, button in enumerate(self.buttons_mid):
            button.move(x_start + i*90, y_start + 100)
        
        # Bottom label
        self.label_bottom.move(x_start, y_start + 200)
        
        # Bottom circles
        for i, circle in enumerate(self.circles_bottom):
            circle.move(x_start + i*spacing, y_start + 240)


class PCARS23st(QMainWindow):
    """Main PCARS 23st interface - late 23rd century design"""
    
    def __init__(self, root_path=None):
        super().__init__()
        self.setWindowTitle("PCARS 23st Control System")
        self.showFullScreen()
        self.root_path = Path(root_path) if root_path else Path('.')
        
        # Era selection
        self.current_era = "23st"
        self.eras = {
            "22nd": {"name": "22nd Century"},
            "23rd": {"name": "23rd Century"},
            "23st": {"name": "23rd PCARS"},
            "24th": {"name": "24th Century"},
            "25th": {"name": "25th Century"},
            "29th": {"name": "29th Century"}
        }
        
        # Load colors
        self.colors = get_palette_by_name(self.eras[self.current_era].get("palette", "23st"))
        
        # Create UI
        self._create_ui()
        
        # Color timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(3000)
    
    def _create_ui(self):
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left menu
        self._create_menu(main_layout)
        
        # Center content
        self._create_content(main_layout)
        
        self.setCentralWidget(main_widget)
    
    def _create_menu(self, main_layout):
        menu_panel = PCARS23stPanel()
        menu_panel.setFixedWidth(200)
        menu_layout = QVBoxLayout(menu_panel)
        menu_layout.setContentsMargins(16, 32, 8, 32)
        menu_layout.setSpacing(18)
        
        self.menu_buttons = []
        
        # Era selection
        era_label = QLabel("ERA SELECT")
        era_label.setStyleSheet("color: #FFE600; font-size: 16px; font-weight: bold; background: transparent;")
        menu_layout.addWidget(era_label)
        
        for era_key, era_info in self.eras.items():
            btn = PCARS23stFullButton(label=era_info['name'], number="", width=180, height=40)
            btn.mousePressEvent = lambda e, key=era_key: self.change_era(key)
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        menu_layout.addSpacing(20)
        
        # Main menu
        tab_names = ["Projects", "Data Analysis", "Files", "Simulation", "Settings"]
        for i, name in enumerate(tab_names):
            btn = PCARS23stFullButton(label=name.upper(), number=f"{i+1:02}-23ST")
            btn.setMinimumHeight(54)
            btn.mousePressEvent = lambda e, idx=i: self.switch_tab(idx)
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        menu_layout.addStretch()
        menu_layout.addWidget(PCARS23stMiniButton(label="EXIT"))
        main_layout.addWidget(menu_panel)
    
    def _create_content(self, main_layout):
        content_panel = PCARS23stPanel()
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)
        
        # Header
        header_label = QLabel("PCARS 23st Control System")
        header_label.setStyleSheet("color: #00FF00; font-size: 38px; font-weight: bold; background: transparent;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        content_layout.addWidget(header_label)
        
        # Tabs area
        tabs_area = PCARS23stPanel()
        self.tabs_layout = QVBoxLayout(tabs_area)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = []
        self._create_projects_tab()
        self._create_analysis_tab()
        self._create_files_tab()
        self._create_simulation_tab()
        self._create_settings_tab()
        
        content_layout.addWidget(tabs_area, 1)
        main_layout.addWidget(content_panel, 1)
    
    def _create_projects_tab(self):
        tab = PCARS23stPanel()
        layout = QVBoxLayout(tab)
        
        # Header buttons (PCARS style)
        header_row = QHBoxLayout()
        header_row.addWidget(PCARS23stFullButton(label="STD", number="01-STD"))
        header_row.addWidget(PCARS23stFullButton(label="DAT", number="02-DAT"))
        header_row.addWidget(PCARS23stFullButton(label="MOD", number="03-MOD"))
        layout.addLayout(header_row)
        
        # Title
        title = QLabel("Discovered Projects (ENX*/NCC-*)")
        title.setStyleSheet("color: #FFE600; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        # Status
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23stMiniButton(label="SCAN"))
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet("color: #FF0000; font-size: 18px; background: transparent;")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        layout.addLayout(status_row)
        
        # Project list
        self.project_list = QListWidget()
        self._scan_projects()
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        layout.addWidget(self.project_list, 1)
        
        # Action buttons
        action_row = QHBoxLayout()
        self.open_btn = PCARS23stFullButton(label="Open Project", number="01-OPEN")
        self.open_btn.mousePressEvent = lambda e: self.open_project()
        action_row.addWidget(self.open_btn)
        action_row.addWidget(PCARS23stMiniButton(label="REFRESH"))
        action_row.addStretch()
        layout.addLayout(action_row)
        
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)
    
    def _create_analysis_tab(self):
        tab = PCARS23stPanel()
        layout = QVBoxLayout(tab)
        
        # Header buttons
        header_row = QHBoxLayout()
        header_row.addWidget(PCARS23stFullButton(label="ANA", number="04-ANA"))
        header_row.addWidget(PCARS23stFullButton(label="VIS", number="05-VIS"))
        header_row.addWidget(PCARS23stFullButton(label="REP", number="06-REP"))
        layout.addLayout(header_row)
        
        # Title
        title = QLabel("Data Analysis")
        title.setStyleSheet("color: #FFE600; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        # Status
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23stMiniButton(label="ANALYZE"))
        self.analysis_status = QLabel("WAITING")
        self.analysis_status.setStyleSheet("color: #FF0000; font-size: 18px; background: transparent;")
        status_row.addWidget(self.analysis_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        
        # Data table
        self.analysis_table = QTableWidget(0, 3)
        self.analysis_table.setHorizontalHeaderLabels(["File", "Size (KB)", "Type"])
        layout.addWidget(self.analysis_table, 1)
        
        # Action buttons
        action_row = QHBoxLayout()
        self.analyze_btn = PCARS23stFullButton(label="Analyze Selected Project", number="02-ANALYZE")
        self.analyze_btn.mousePressEvent = lambda e: self.analyze_project()
        action_row.addWidget(self.analyze_btn)
        action_row.addWidget(PCARS23stMiniButton(label="EXPORT"))
        action_row.addStretch()
        layout.addLayout(action_row)
        
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)
    
    def _create_files_tab(self):
        tab = PCARS23stPanel()
        layout = QVBoxLayout(tab)
        
        # Header buttons
        header_row = QHBoxLayout()
        header_row.addWidget(PCARS23stFullButton(label="FIL", number="07-FIL"))
        header_row.addWidget(PCARS23stFullButton(label="DIR", number="08-DIR"))
        header_row.addWidget(PCARS23stFullButton(label="SRC", number="09-SRC"))
        layout.addLayout(header_row)
        
        # Title
        title = QLabel("Project Files")
        title.setStyleSheet("color: #FFE600; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        # Status
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23stMiniButton(label="FILES"))
        self.files_status = QLabel("READY")
        self.files_status.setStyleSheet("color: #FF0000; font-size: 18px; background: transparent;")
        status_row.addWidget(self.files_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        
        # File tree
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_view = QTreeView()
        self.file_view.setModel(self.file_model)
        layout.addWidget(self.file_view, 1)
        
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)
    
    def _create_simulation_tab(self):
        tab = PCARS23stPanel()
        layout = QVBoxLayout(tab)
        
        # Header buttons
        header_row = QHBoxLayout()
        header_row.addWidget(PCARS23stFullButton(label="SIM", number="10-SIM"))
        header_row.addWidget(PCARS23stFullButton(label="RUN", number="11-RUN"))
        header_row.addWidget(PCARS23stFullButton(label="LOG", number="12-LOG"))
        layout.addLayout(header_row)
        
        # Title
        title = QLabel("Simulation")
        title.setStyleSheet("color: #FFE600; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        # Status
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23stMiniButton(label="SIM"))
        self.sim_status = QLabel("IDLE")
        self.sim_status.setStyleSheet("color: #FF0000; font-size: 18px; background: transparent;")
        status_row.addWidget(self.sim_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)
    
    def _create_settings_tab(self):
        tab = PCARS23stPanel()
        layout = QVBoxLayout(tab)
        
        # Header buttons
        header_row = QHBoxLayout()
        header_row.addWidget(PCARS23stFullButton(label="CFG", number="13-CFG"))
        header_row.addWidget(PCARS23stFullButton(label="USR", number="14-USR"))
        header_row.addWidget(PCARS23stFullButton(label="THE", number="15-THE"))
        layout.addLayout(header_row)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("color: #FFE600; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        # Status
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23stMiniButton(label="SETTINGS"))
        self.settings_status = QLabel("READY")
        self.settings_status.setStyleSheet("color: #FF0000; font-size: 18px; background: transparent;")
        status_row.addWidget(self.settings_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)
    
    def change_era(self, era_name):
        """Change era and update interface"""
        if era_name in self.eras:
            self.current_era = era_name
            self.setWindowTitle(f"PCARS 23st Control System ({self.eras[era_name]['name']})")
            self.colors = get_palette_by_name(self.eras[era_name].get("palette", "23st"))
            self.update_colors()
            print(f"Switched to {self.eras[era_name]['name']}")
    
    def update_colors(self):
        """Update all button colors"""
        if hasattr(self, 'menu_buttons'):
            for btn in self.menu_buttons:
                btn.update_color()
        if hasattr(self, 'open_btn'):
            self.open_btn.update_color()
        if hasattr(self, 'analyze_btn'):
            self.analyze_btn.update_color()
    
    def switch_tab(self, index):
        """Switch to specific tab"""
        for i, tab in enumerate(self.tabs):
            tab.setVisible(i == index)
    
    def _scan_projects(self):
        """Scan for projects"""
        self.project_list.clear()
        for root, dirs, files in os.walk(self.root_path):
            for d in dirs:
                if d.startswith("ENX") or d.startswith("NCC-"):
                    self.project_list.addItem(str(Path(root) / d))
        if self.project_list.count() > 0:
            self.project_list.setCurrentRow(0)
    
    def on_project_selected(self, current, previous):
        """Handle project selection"""
        if current:
            self.selected_project = Path(current.text())
        else:
            self.selected_project = None
    
    def open_project(self):
        """Open selected project"""
        if self.selected_project:
            self.file_model.setRootPath(str(self.selected_project))
            self.file_view.setRootIndex(self.file_model.index(str(self.selected_project)))
    
    def analyze_project(self):
        """Analyze selected project"""
        if not self.selected_project:
            return
        self._load_analysis_data(self.selected_project)
    
    def _load_analysis_data(self, project_path):
        """Load analysis data for project"""
        self.analysis_table.setRowCount(0)
        for root, dirs, files in os.walk(project_path):
            for f in files:
                fpath = Path(root) / f
                size_kb = round(fpath.stat().st_size / 1024, 2)
                ext = fpath.suffix
                row = self.analysis_table.rowCount()
                self.analysis_table.insertRow(row)
                self.analysis_table.setItem(row, 0, QTableWidgetItem(str(fpath.relative_to(project_path))))
                self.analysis_table.setItem(row, 1, QTableWidgetItem(str(size_kb)))
                self.analysis_table.setItem(row, 2, QTableWidgetItem(ext))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PCARS23st(root_path=Path("."))
    window.show()
    sys.exit(app.exec())
