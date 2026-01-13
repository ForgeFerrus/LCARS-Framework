"""
NX-01 Enterprise Master Systems Display
Authentic 22nd Century Operating System - Final Edition
Combining advanced logic with premium NX-era aesthetics.
"""

import sys
import os
import random
import time
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QApplication, 
                           QGridLayout, QProgressBar, QStackedWidget)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF, pyqtSignal

# Додавання шляху до проекту для автономного запуску
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import get_era_palette, LCARSEra
from lcars.core.project_manager import ProjectManager
from lcars.core.file_analyzer import FileAnalyzer

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
        self.side = side # left, top, bottom, right
        self.panel_color = color
        self.label_text = text
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        path = QPainterPath()
        radius = 20
        
        if self.side == "left":
            # Cap top, flat bottom
            path.moveTo(0, radius)
            path.arcTo(0, 0, rect.width(), radius*2, 180, -180)
            path.lineTo(rect.width(), rect.height())
            path.lineTo(0, rect.height())
            path.closeSubpath()
        elif self.side == "right":
            path.moveTo(0, 0)
            path.lineTo(rect.width(), 0)
            path.lineTo(rect.width(), rect.height() - radius)
            path.arcTo(0, rect.height() - radius*2, rect.width(), radius*2, 0, -180)
            path.lineTo(0, rect.height())
            path.closeSubpath()
        else:
            path.addRect(QRectF(rect))
            
        painter.setBrush(QBrush(QColor(self.panel_color)))
        painter.setPen(QPen(QColor("#444444"), 2))
        painter.drawPath(path)
        
        if self.label_text:
            painter.setPen(QColor("#000000"))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            if self.side == "left":
                # Vertical text
                painter.save()
                painter.translate(rect.width()/2 + 5, 100)
                painter.rotate(90)
                painter.drawText(0, 0, self.label_text)
                painter.restore()

class NXConsole(QMainWindow):
    """The Master NX-01 Console Interface"""
    
    def __init__(self, root_path: Path):
        super().__init__()
        self.root_path = root_path
        self.palette = get_era_palette(LCARSEra.COMS_22ND)
        self.colors = self.palette
        self.project_manager = ProjectManager(root_path)
        
        self.setup_window()
        self.init_ui()
        self.start_timers()
        
    def setup_window(self):
        self.setWindowTitle("NX-01 OPERATING SYSTEM")
        # Fullscreen for immersive experience
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # --- LEFT NAVIGATION ---
        self.nav_area = QWidget()
        self.nav_area.setFixedWidth(220)
        self.nav_vbox = QVBoxLayout(self.nav_area)
        self.nav_vbox.setContentsMargins(0,0,0,0)
        
        self.nav_pill = NXPillPanel(side="left", text="NX-01 ENTERPRISE COMMAND")
        self.pill_layout = QVBoxLayout(self.nav_pill)
        self.pill_layout.setContentsMargins(10, 50, 10, 20)
        
        # Blue indicator at top
        ind = QLabel()
        ind.setFixedSize(40, 40)
        ind.setStyleSheet("background-color: #269EEE; border-radius: 20px; border: 2px solid #444444;")
        self.pill_layout.addWidget(ind, 0, Qt.AlignmentFlag.AlignCenter)
        self.pill_layout.addSpacing(100) # For vertical text space
        
        # Menu Buttons
        self.btn_projects = NXButton("PROJECTS", "#FFE600")
        self.btn_science = NXButton("SCIENCE", "#269EEE")
        self.btn_eng = NXButton("ENGINEERING", "#5C5C5C")
        self.btn_tactical = NXButton("TACTICAL", "#CE6363")
        
        self.btn_projects.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_science.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_eng.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_tactical.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        for b in [self.btn_projects, self.btn_science, self.btn_eng, self.btn_tactical]:
            self.pill_layout.addWidget(b)
            
        self.pill_layout.addStretch()
        
        # Exit button
        btn_exit = NXButton("SHUTDOWN", "#CE6363")
        btn_exit.clicked.connect(self.close)
        self.pill_layout.addWidget(btn_exit)
        
        self.nav_vbox.addWidget(self.nav_pill)
        self.main_layout.addWidget(self.nav_area)
        
        # --- CENTER/RIGHT CONTENT ---
        self.content_vbox = QVBoxLayout()
        self.main_layout.addLayout(self.content_vbox)
        
        # Header (Stardate / Logo)
        self.header = QHBoxLayout()
        self.content_vbox.addLayout(self.header)
        
        self.sd_box = QFrame()
        self.sd_box.setFixedSize(350, 110)
        self.sd_box.setStyleSheet("border: 2px solid #CCCCCC; background: #000000;")
        sd_lay = QVBoxLayout(self.sd_box)
        sd_title = QLabel("STARDATE")
        sd_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sd_title.setStyleSheet("font-size: 20px; color: #888888; border:none;")
        self.lbl_stardate = QLabel("-0000.00")
        self.lbl_stardate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_stardate.setStyleSheet("font-size: 42px; font-weight: bold; color: #FFFFFF; border:none;")
        sd_lay.addWidget(sd_title)
        sd_lay.addWidget(self.lbl_stardate)
        self.header.addWidget(self.sd_box)
        
        self.header.addStretch()
        
        # Top Bar Pill
        self.top_pill = QFrame()
        self.top_pill.setFixedHeight(60)
        self.top_pill.setFixedWidth(700)
        self.top_pill.setStyleSheet("background-color: #CCCCCC; border-radius: 5px;")
        tp_lay = QHBoxLayout(self.top_pill)
        tp_ind = QLabel()
        tp_ind.setFixedSize(25, 25)
        tp_ind.setStyleSheet("background-color: #27F8FF; border-radius: 12px;")
        tp_lay.addWidget(tp_ind)
        tp_name = QLabel("NX-01 OPERATING SYSTEM v1.02")
        tp_name.setStyleSheet("color: #000000; font-weight: bold; font-size: 18px;")
        tp_lay.addWidget(tp_name)
        tp_lay.addStretch()
        self.header.addWidget(self.top_pill)
        
        # MAIN STACK
        self.stack = QStackedWidget()
        self.content_vbox.addWidget(self.stack)
        
        self.init_projects_tab()
        self.init_science_tab()
        self.init_eng_tab()
        self.init_tactical_tab()
        
        # Footer
        self.footer = QHBoxLayout()
        self.content_vbox.addLayout(self.footer)
        self.lbl_status = QLabel("ALL SYSTEMS NOMINAL - NX-01 BRIDGE")
        self.lbl_status.setStyleSheet("color: #269EEE; font-size: 16px; font-weight: bold;")
        self.footer.addWidget(self.lbl_status)
        self.footer.addStretch()
        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setStyleSheet("font-size: 24px; color: #FFFFFF;")
        self.footer.addWidget(self.lbl_clock)

    def init_projects_tab(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        
        # List
        self.proj_list = QListWidget()
        self.proj_list.setFixedWidth(400)
        self.proj_list.setStyleSheet(self.get_list_style())
        lay.addWidget(self.proj_list)
        
        # Info
        info_w = QWidget()
        info_lay = QVBoxLayout(info_w)
        
        self.proj_title = QLabel("SELECT PROJECT")
        self.proj_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFE600;")
        info_lay.addWidget(self.proj_title)
        
        self.proj_desc = QLabel("Welcome to NX-01 Archive. Select a project from the left to view technical specifications.")
        self.proj_desc.setWordWrap(True)
        self.proj_desc.setStyleSheet("font-size: 18px; color: #CCCCCC;")
        info_lay.addWidget(self.proj_desc)
        
        info_lay.addStretch()
        
        btn_run = NXButton("INITIALIZE SIMULATION", "#269EEE")
        btn_run.clicked.connect(self.run_sim)
        info_lay.addWidget(btn_run)
        
        lay.addWidget(info_w)
        self.proj_list.itemClicked.connect(self.load_project)
        self.refresh_projects()
        
        self.stack.addWidget(page)

    def init_science_tab(self):
        page = QWidget()
        lay = QGridLayout(page)
        # Random data blocks
        for i in range(12):
            f = QFrame()
            f.setStyleSheet(f"background: {random.choice(['#112233', '#113322', '#332211'])}; border: 1px solid #444444;")
            lay.addWidget(f, i//4, i%4)
            l = QLabel(f"SENSOR NODE {i+100}\nSCANNING...")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QVBoxLayout(f)
            v.addWidget(l)
        self.stack.addWidget(page)

    def init_eng_tab(self):
        page = QWidget()
        vlay = QVBoxLayout(page)
        vlay.addWidget(QLabel("WARP CORE MONITORING"))
        for s in ["EPS GRID", "DILITHIUM MATRIX", "INJECTORS", "PLASMA RESONANCE"]:
            h = QHBoxLayout()
            h.addWidget(QLabel(s))
            pb = QProgressBar()
            pb.setValue(random.randint(40, 95))
            pb.setStyleSheet("QProgressBar { background: #111; border: 1px solid #5C5C5C; border-radius: 5px; color: #000; } QProgressBar::chunk { background: #5C5C5C; }")
            h.addWidget(pb)
            vlay.addLayout(h)
        vlay.addStretch()
        self.stack.addWidget(page)

    def init_tactical_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.addWidget(QLabel("TACTICAL SENSORS - LONG RANGE SCAN"))
        img = QLabel()
        # Path to ship image if exists, else generic
        lay.addWidget(img, 1, Qt.AlignmentFlag.AlignCenter)
        lay.addStretch()
        self.stack.addWidget(page)

    def get_list_style(self):
        return """
            QListWidget { background: #000; border: 2px solid #555; border-radius: 5px; color: #FFF; font-size: 16px; padding: 10px; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #333; }
            QListWidget::item:selected { background: #269EEE; color: #000; }
        """

    def refresh_projects(self):
        """Update the list of Geant4 projects"""
        try:
            self.proj_list.clear() # Changed from self.list_projects.clear() to self.proj_list.clear() to match original variable name
            projects = self.project_manager.get_all_projects()
            for project in projects:
                self.proj_list.addItem(project.name) # Changed from self.list_projects.addItem(project.name) to self.proj_list.addItem(project.name)
        except Exception as e:
            print(f"Error refreshing projects: {e}")

    def load_project(self, item):
        name = item.text()
        info = self.project_manager.get_project(name)
        self.proj_title.setText(name.upper())
        if info:
            self.proj_desc.setText(info.description or 'No detailed description available.')
        else:
            self.proj_desc.setText('Project info not found.')

    def run_sim(self):
        QMessageBox.information(self, "NX-01 SIM", "Initializing Enterprise Simulation Environment...\nMapping chroniton flux levels.")

    def start_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_displays)
        self.timer.start(1000)
        
    def update_displays(self):
        # Update Stardate (fake but consistent)
        now = time.time()
        stardate = -3755.53 + (now % 10000) / 1000
        self.lbl_stardate.setText(f"{stardate:02.5f}")
        
        # Update Clock
        self.lbl_clock.setText(time.strftime("%H:%M:%S"))
        
        # Random status flicker
        if random.random() > 0.9:
            self.lbl_status.setText("UPDATING SENSOR BUFFER... OK")
        else:
            self.lbl_status.setText("ALL SYSTEMS NOMINAL - NX-01 BRIDGE")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    current_file = Path(__file__).resolve()
    root_path = current_file.parents[2]
    
    window = NXConsole(root_path)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()