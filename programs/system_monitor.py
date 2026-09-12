"""
System Task Manager (Titan V5.5)
Unified hub for monitoring, scanning, and process management.
Restored to premium high-fidelity standards.
"""

import sys
import os
import psutil
from pathlib import Path

# Bootstrap LCARS environment
proc_root = Path(__file__).resolve().parents[1]
if str(proc_root) not in sys.path:
    sys.path.insert(0, str(proc_root))

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, QTimer

from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.base.components import (
    LCARSButton, LCARSElbow, LCARSSegment
)
from lcars.base.type import LCARS, Matrix, Chassis, Directive
from lcars.base.register import registry
from lcars.modules.config_manager import config_manager
from programs.scanner.engine import ScannerEngine

class SystemTaskManager(LCARSProgramPanel):
    """
    Premium Task Manager.
    Aligned with the 'English Learning' benchmark.
    """

    def __init__(self, era=None, faction=None, parent=None):
        resolved_era = era or LCARSEra.LCARS_25TH
        resolved_faction = faction or config_manager.get("app", "faction")
        
        self.engine = ScannerEngine()
        self.tabs = {}
        
        super().__init__(
            title="SYSTEM TASK MANAGER",
            era=resolved_era,
            faction=resolved_faction,
            accent_color="#FF9900",
            parent=parent,
        )
        
        # Set up periodic updates for metrics
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.update_active_tab)
        self.timer.start()

    def build_ui(self, layout: QVBoxLayout):
        """Build the premium interface structure."""
        main_h = QHBoxLayout()
        main_h.setSpacing(0)
        main_h.setContentsMargins(0, 0, 0, 0)
        
        # --- 1. PREMIUM NAVIGATION SIDEBAR (250px) ---
        nav_panel = QFrame()
        nav_panel.setFixedWidth(250)
        nav_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-right: 2px solid {self.accent};
            }}
        """)
        
        nav_lay = QVBoxLayout(nav_panel)
        nav_lay.setContentsMargins(15, 10, 15, 20)
        nav_lay.setSpacing(12)
        
        # LCARS Elbow at top
        elbow = LCARSElbow("top-left", color="#4BBEBF")
        elbow.setMinimumSize(220, 50)
        nav_lay.addWidget(elbow)
        
        # Sub-title
        title = QLabel("DIAGNOSTIC HUB")
        title.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(16, 'bold')}; padding: 10px 0;")
        nav_lay.addWidget(title)
        
        nav_items = [
            ("MONITOR", "monitor", "#4BBEBF"),
            ("SCANNER", "scanner", "#FF9900"),
            ("SYSTEM", "system", "#9EA5BA"),
        ]
        
        self.sub_nav_buttons = {}
        for name, key, color in nav_items:
            btn = LCARSButton(name, color, shape="left", era=self.era)
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda ch, k=key: self.switch_tab(k))
            nav_lay.addWidget(btn)
            self.sub_nav_buttons[key] = btn
            
        nav_lay.addStretch()
        
        # Power block
        status_lbl = QLabel("◤ NODE: PRIMARY\n◤ AUTH: COMMAND\n◤ CORE: STABLE")
        status_lbl.setStyleSheet(f"color: #5A6070; {get_lcars_font_style(12, 'normal')}; padding: 10px; background: #080808;")
        nav_lay.addWidget(status_lbl)
        
        main_h.addWidget(nav_panel)
        
        # --- 2. MAIN CONTENT STACK ---
        self.stack = QStackedWidget()
        self.init_monitor_tab()
        self.init_scanner_tab()
        self.init_system_tab()
        
        main_h.addWidget(self.stack, 1)
        layout.addLayout(main_h)

    def init_monitor_tab(self):
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(40, 40, 40, 40)
        ly.setSpacing(30)
        
        lbl = QLabel("◢ HARDWARE MONITORING")
        lbl.setStyleSheet(f"color: white; {get_lcars_font_style(24, 'normal')};")
        ly.addWidget(lbl)
        
        self.bars = {
            "cpu": StatBar("PROCESSOR CORE", "#FF9900", parent=self),
            "mem": StatBar("MEMORY MODULES", "#4BBEBF", parent=self),
            "disk": StatBar("DATA STORAGE", "#CC9966", parent=self)
        }
        
        for bar in self.bars.values():
            ly.addWidget(bar)
            
        ly.addStretch()
        self.tabs["monitor"] = self.stack.addWidget(tab)

    def init_scanner_tab(self):
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(40, 40, 40, 40)
        ly.setSpacing(15)
        
        lbl = QLabel("◢ DIAGNOSTIC SCANNER")
        lbl.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(24, 'normal')};")
        ly.addWidget(lbl)
        
        self.scan_bar = ScanningBar("#FF9900", speed=3.0)
        ly.addWidget(self.scan_bar)
        
        self.scan_results = QLabel("◤ WAITING FOR SCAN...")
        self.scan_results.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(16, 'normal')}; padding: 25px; background: #080808; border: 1px solid #1a1a1a;")
        self.scan_results.setWordWrap(True)
        ly.addWidget(self.scan_results, 1)
        
        run_btn = LCARSButton("INITIATE SCAN", "#FF9900", era=self.era)
        run_btn.setMinimumHeight(60)
        run_btn.clicked.connect(self.perform_scan)
        ly.addWidget(run_btn)
        
        self.tabs["scanner"] = self.stack.addWidget(tab)

    def init_system_tab(self):
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(40, 40, 40, 40)
        
        lbl = QLabel("◢ SYSTEM OVERVIEW")
        lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(24, 'normal')};")
        ly.addWidget(lbl)
        
        info = f"◤ OS: {os.name.upper()}\n◤ CORE: TITAN LCARS V5.5\n◤ NODE: {Path.home().name.upper()}\n◤ ACCESS: COMMAND LEVEL"
        info_lbl = QLabel(info)
        info_lbl.setStyleSheet(f"color: #4BBEBF; {get_lcars_font_style(20, 'normal')}; line-height: 1.8;")
        ly.addWidget(info_lbl)
        
        ly.addStretch()
        self.tabs["system"] = self.stack.addWidget(tab)

    def switch_tab(self, key):
        if key in self.tabs:
            self.stack.setCurrentIndex(self.tabs[key])

    def update_active_tab(self):
        idx = self.stack.currentIndex()
        if idx == self.tabs.get("monitor"):
            stats = self.engine.get_system_stats()
            if "cpu" in stats:
                self.bars["cpu"].setValue(int(stats["cpu"]))
                self.bars["mem"].setValue(int(stats["memory"]))
                self.bars["disk"].setValue(int(stats["disk"]))
                
    def perform_scan(self):
        self.scan_results.setText("◤ SCANNING SUBSYSTEMS...")
        QTimer.singleShot(1500, self._show_scan_results)
        
    def _show_scan_results(self):
        net = self.engine.get_network_info()
        res = f"◤ HOST: {net['hostname']}\n◤ LOCAL IP: {net['local_ip']}\n◤ UPLOAD: {net['upload_kb']} KB/S\n◤ DOWNLOAD: {net['download_kb']} KB/S\n\n◤ STATUS: ALL SYSTEMS NOMINAL"
        self.scan_results.setText(res)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = SystemTaskManager()
    win.showFullScreen()
    sys.exit(app.exec())
