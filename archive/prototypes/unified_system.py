#!/usr/bin/env python3
"""
LCARS Unified Master Hub - Premium NX-01 Edition
The central command center for all LCARS prototypes.
Features: Dynamic file scanning, theme management, process output capture.
"""

import sys
import os
import psutil
import time
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTabWidget, 
                           QTextEdit, QListWidget, QProgressBar, QGridLayout,
                           QGroupBox, QFrame, QMessageBox, QStackedWidget,
                           QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess, QSize, QRectF
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor, QPainter, QPainterPath, QBrush, QPen

# Додавання шляху до проекту
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import get_era_palette, LCARSEra

class NXButton(QPushButton):
    """NX-style rectangular button with corner indicator"""
    def __init__(self, text, color="#269EEE", parent=None):
        super().__init__(text, parent)
        self.btn_color = color
        self.setMinimumHeight(40)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        bg_color = QColor(self.btn_color)
        if self.underMouse(): bg_color = bg_color.lighter(120)
        if self.isDown(): bg_color = bg_color.darker(120)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawRect(rect)
        indicator_size = 6
        ind_rect = QRectF(rect.right() - indicator_size - 4, rect.top() + 4, indicator_size, indicator_size)
        painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
        painter.drawRect(ind_rect)
        painter.setPen(QColor("#000000"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def set_color(self, color):
        self.btn_color = color
        self.update()

class NXPillPanel(QFrame):
    """NX-style silver panel with Pill shape"""
    def __init__(self, side="left", color="#CCCCCC", text="", parent=None):
        super().__init__(parent)
        if hasattr(self, 'theme') and self.theme:
            if hasattr(self.theme, 'palette'):
                self.colors = self.theme.palette.copy()
            elif hasattr(self.theme, 'colors'):
                self.colors = self.theme.colors.copy()
            else:
                self.colors = self.theme.copy()
        else:
            self.colors = {}
        self.side = side
        self.panel_color = color
        self.label_text = text
        self.update()

    def set_color(self, color):
        self.panel_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        radius = 20
        if self.side == "left":
            path.moveTo(0, radius)
            path.arcTo(0, 0, rect.width(), radius*2, 180, -180)
            path.lineTo(rect.width(), rect.height())
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
                painter.save()
                painter.translate(rect.width()/2 + 5, 100)
                painter.rotate(90)
                painter.drawText(0, 0, self.label_text)
                painter.restore()

class SystemMonitorThread(QThread):
    data_updated = pyqtSignal(dict)
    def run(self):
        while True:
            try:
                data = {
                    'cpu': psutil.cpu_percent(interval=1),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent,
                    'time': datetime.now().strftime("%H:%M:%S")
                }
                self.data_updated.emit(data)
            except: pass
            self.msleep(1000)

class LCARSUnifiedSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_era = LCARSEra.COMS_22ND
        self.update_palette()
        self.running_processes = {}
        self.setup_window()
        self.init_ui()
        self.start_monitoring()
        self.refresh_prototypes()
        
    def update_palette(self):
        self.palette = get_era_palette(self.current_era)
        self.colors = self.palette
        # Map old keys to new names for compatibility
        self.colors['primary'] = self.colors['button_colors'][0]
        self.colors['secondary'] = self.colors['button_colors'][1]
        self.colors['accent1'] = self.colors['button_colors'][3]
        self.colors['accent2'] = self.colors['button_colors'][7]
        self.colors['panel'] = self.colors.get('panel_color', '#CCCCCC')
        self.colors['border'] = self.colors.get('panel_border', '#444444')
        self.colors['success'] = '#00FF00'
        self.colors['info'] = self.colors['button_colors'][3]
        self.colors['background'] = '#000000'
        self.colors['text'] = '#FFFFFF'

    def setup_window(self):
        self.setWindowTitle("LCARS UNIFIED MASTER HUB")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {self.colors['background']}; color: {self.colors['text']};")

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # --- LEFT NAV ---
        self.nav_pill = NXPillPanel(side="left", text="MASTER HUB COMMAND")
        self.nav_pill.setFixedWidth(220)
        nav_lay = QVBoxLayout(self.nav_pill)
        nav_lay.setContentsMargins(10, 60, 10, 20)
        
        btns = [
            ("LAUNCHER", "#FFE600", 0),
            ("MONITOR", "#269EEE", 1),
            ("LOGS", "#5C5C5C", 2),
            ("THEMES", "#FFBB00", 3)
        ]
        for text, color, idx in btns:
            b = NXButton(text, color)
            b.clicked.connect(lambda checked, i=idx: self.stack.setCurrentIndex(i))
            nav_lay.addWidget(b)
        
        nav_lay.addStretch()
        btn_exit = NXButton("SHUTDOWN", "#CE6363")
        btn_exit.clicked.connect(self.close)
        nav_lay.addWidget(btn_exit)
        self.main_layout.addWidget(self.nav_pill)
        
        # --- CONTENT ---
        self.content_vbox = QVBoxLayout()
        self.main_layout.addLayout(self.content_vbox)
        
        # Header
        self.header_pill = QFrame()
        self.header_pill.setFixedHeight(60)
        self.header_pill.setStyleSheet(f"background: {self.colors['panel']}; border-radius: 5px;")
        h_lay = QHBoxLayout(self.header_pill)
        self.lbl_title = QLabel("UNIFIED SYSTEM HUB v2.0 - NX-01 PROTOCOL")
        self.lbl_title.setStyleSheet("color: #000; font-weight: bold; font-size: 18px;")
        h_lay.addWidget(self.lbl_title)
        h_lay.addStretch()
        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setStyleSheet("color: #000; font-weight: bold; font-size: 18px;")
        h_lay.addWidget(self.lbl_clock)
        self.content_vbox.addWidget(self.header_pill)
        
        # Stack
        self.stack = QStackedWidget()
        self.content_vbox.addWidget(self.stack)
        
        self.init_launcher()
        self.init_monitor()
        self.init_logs()
        self.init_themes()
        
    def init_launcher(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.addWidget(QLabel("AVAILABLE PROTOTYPES"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.proto_container = QWidget()
        self.proto_lay = QVBoxLayout(self.proto_container)
        scroll.setWidget(self.proto_container)
        lay.addWidget(scroll)
        self.stack.addWidget(page)

    def init_monitor(self):
        page = QWidget()
        lay = QGridLayout(page)
        self.mon_cpu = QProgressBar()
        self.mon_ram = QProgressBar()
        self.mon_disk = QProgressBar()
        for i, (pb, label) in enumerate([(self.mon_cpu, "CPU"), (self.mon_ram, "RAM"), (self.mon_disk, "DISK")]):
            lay.addWidget(QLabel(label), i, 0)
            pb.setStyleSheet(f"QProgressBar {{ background: #111; border: 1px solid {self.colors['border']}; }} QProgressBar::chunk {{ background: {self.colors['primary']}; }}")
            lay.addWidget(pb, i, 1)
        self.stack.addWidget(page)

    def init_logs(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background: #000; color: #0F0; font-family: 'Consolas'; font-size: 11pt; border: 1px solid #444;")
        lay.addWidget(self.log_output)
        self.stack.addWidget(page)

    def init_themes(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.addWidget(QLabel("CORE THEME SELECTOR"))
        self.theme_list = QListWidget()
        self.theme_list.setStyleSheet("background: #111; color: #FFF; border: 1px solid #444;")
        for era in LCARSEra:
            self.theme_list.addItem(era.name)
        self.theme_list.itemClicked.connect(self.change_theme)
        lay.addWidget(self.theme_list)
        self.stack.addWidget(page)

    def refresh_prototypes(self):
        # Scan archive/prototypes
        proto_path = Path(__file__).parent
        # Clear existing
        for i in reversed(range(self.proto_lay.count())): 
            self.proto_lay.itemAt(i).widget().setParent(None)
            
        ignore_files = ["LAUNCH_ALL.bat", "diagnose_prototypes.py", "__init__.py", Path(__file__).name]
        
        for item in sorted(proto_path.glob("*.py")):
            if item.name in ignore_files: continue
            self.add_proto_panel(item)
        for item in sorted(proto_path.glob("*.bat")):
            if item.name in ignore_files: continue
            self.add_proto_panel(item)

    def add_proto_panel(self, path):
        f = QFrame()
        f.setStyleSheet(f"background: #111; border: 1px solid {self.colors['border']}; border-radius: 5px;")
        f.setFixedHeight(80)
        l = QHBoxLayout(f)
        l.addWidget(QLabel(path.name))
        btn = NXButton("LAUNCH", "#269EEE")
        btn.clicked.connect(lambda: self.launch_proto(path))
        l.addWidget(btn)
        self.proto_lay.addWidget(f)

    def launch_proto(self, path):
        self.log_output.append(f"[{datetime.now().strftime('%H:%M:%S')}] Launching: {path.name}")
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.readyReadStandardOutput.connect(lambda: self.read_output(process))
        if path.suffix == ".py":
            process.start(sys.executable, [str(path)])
        else:
            process.start(str(path))
        self.running_processes[path.name] = process

    def read_output(self, proc):
        data = proc.readAllStandardOutput().data().decode()
        self.log_output.append(data.strip())

    def change_theme(self, item):
        self.current_era = LCARSEra[item.text()]
        self.update_palette()
        self.apply_styles()
        self.update_all_widgets(self)
        self.log_output.append(f"Theme changed to: {self.current_era.name}")

    def update_all_widgets(self, parent):
        for child in parent.findChildren(QWidget):
            if isinstance(child, NXButton):
                child.set_color(self.colors['primary'])
            elif isinstance(child, NXPillPanel):
                child.set_color(self.colors['panel'])
            elif isinstance(child, QProgressBar):
                child.setStyleSheet(f"QProgressBar {{ background: #111; border: 1px solid {self.colors['border']}; }} QProgressBar::chunk {{ background: {self.colors['primary']}; }}")

    def apply_styles(self):
        self.setStyleSheet(f"background-color: {self.colors['background']}; color: {self.colors['text']};")
        self.header_pill.setStyleSheet(f"background: {self.colors['panel']}; border-radius: 5px;")
        # Need to refresh icons/colors in list but for now just general
        self.lbl_title.setText(f"MASTER HUB - {self.current_era.name} PROTOCOL")

    def start_monitoring(self):
        self.mon_thread = SystemMonitorThread()
        self.mon_thread.data_updated.connect(self.update_stats)
        self.mon_thread.start()
        
    def update_stats(self, data):
        self.mon_cpu.setValue(int(data['cpu']))
        self.mon_ram.setValue(int(data['memory']))
        self.mon_disk.setValue(int(data['disk']))
        self.lbl_clock.setText(data['time'])

def main():
    app = QApplication(sys.argv)
    window = LCARSUnifiedSystem()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()