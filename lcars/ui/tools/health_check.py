# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import psutil
import platform
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTextEdit, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer

from lcars.themes.palette import LCARSEra
from lcars.base.default import RandomButtonColor as get_era_palette, FontStyle as setup_lcars_font
from lcars.base.component import LCARSElbow, LCARSButton
class HealthCheck(QMainWindow):
    # "Центр діагностики нейронного ядра (без елементів Windows).
    def __init__(self):
        super().__init__()
        self.era = LCARSEra.LCARS_25TH
        self.lcars_palette = get_era_palette(self.era)
        self.accent = self.lcars_palette['button_colors'][0]

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet("background-color: black; color: white;")
        setup_lcars_font()

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(5)

        self.setup_ui()
        QTimer.singleShot(800, self.run_diag)

    def setup_ui(self):
        # --- HEADER AREA (FLAT BLOCKS) ---
        header = QHBoxLayout()
        header.setSpacing(2)

        self.top_elbow = LCARSElbow("top-left", self.accent, era=self.era)
        header.addWidget(self.top_elbow)

        title_block = QFrame()
        title_block.setMinimumHeight(65)
        title_block.setStyleSheet(f"background: {self.accent}; border: none;")
        tl = QHBoxLayout(title_block)

        t_label = QLabel("NEURAL CORE DIAGNOSTICS :: SYSTEM WIDE INTEGRITY SCAN")
        t_label.setStyleSheet(f"color: black; {setup_lcars_font(22, 'normal')}")
        tl.addWidget(t_label)
        tl.addStretch()

        self.clock = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.clock.setStyleSheet(f"color: black; {setup_lcars_font(18, 'normal')}")
        tl.addWidget(self.clock)
        header.addWidget(title_block, 1)
        self.main_layout.addLayout(header)

        # --- CENTER DATA AREA ---
        content = QHBoxLayout()
        content.setSpacing(5)

        # Left sidebar (Telemetry)
        self.side_panel = QFrame()
        self.side_panel.setMinimumWidth(220)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(0, 0, 0, 0)
        self.side_layout.setSpacing(4)

        self.btn_exit = LCARSButton("DISCONNECT", "#555555", era=self.era, shape="left")
        self.btn_exit.setMinimumHeight(45)
        self.btn_exit.clicked.connect(self.close)
        self.side_layout.addWidget(self.btn_exit)
        self.side_layout.addStretch()

        content.addWidget(self.side_panel)

        # Main readout area
        self.readout = QTextEdit()
        self.readout.setReadOnly(True)
        self.readout.setStyleSheet(f"""
            QTextEdit {{
                background: black; color: #37A6D1;
                border: none;
                font-family: 'Consolas', 'Courier New'; font-size: 16px;
                padding: 25px;
            }}
            QScrollBar:vertical {{
                border: none; background: #000; width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.accent}; min-height: 20px; border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        content.addWidget(self.readout, 1)
        self.main_layout.addLayout(content, 1)

        # --- FOOTER AREA ---
        footer = QHBoxLayout()
        footer.setSpacing(2)

        self.btm_elbow = LCARSElbow("bottom-left", self.lcars_palette['button_colors'][1], era=self.era)
        footer.addWidget(self.btm_elbow)

        self.status_bar = QLabel("INITIALIZING PROTOCOLS")
        self.status_bar.setMinimumHeight(50)
        self.status_bar.setStyleSheet(f"background: {self.lcars_palette['button_colors'][1]}; color: black; padding: 0 20px; {get_lcars_font_style(16, 'normal')}")
        footer.addWidget(self.status_bar, 1)
        self.main_layout.addLayout(footer)

    def _clean_text(self, text):
        """Removes underscores and slashes for LCARS compliance."""
        return text.replace("_", " ").replace("/", " :: ").replace("\\", " :: ")

    # ...existing code...

    def run_diag(self):
        self.status_bar.setText("NEURAL NODES SCANNING :: PLEASE STANDBY")
        self.readout.clear()

        # 1. Host Telemetry (Hardware Layer)
        self.readout.append(f"<font color='{self.accent}'>◤ SECTION 01 :: NEURAL HOST TELEMETRY</font>")
        mem = psutil.virtual_memory()
        cpu_load = psutil.cpu_percent(interval=None)
        self.readout.append(f"OS TYPE: {platform.system().upper()} :: KERNEL: {platform.release()}")
        self.readout.append(f"CORE LOAD: {cpu_load}% :: MEMORY USE: {mem.percent}%")
        usage = shutil.disk_usage('/')
        percent_used = (usage.used / usage.total) * 100
        self.readout.append(f"STORAGE :: DISK USE: {percent_used:.1f}%")

        # 1a. Add CPU info and uptime
        self.readout.append(f"CPU: {platform.processor()} :: CORES: {psutil.cpu_count(logical=True)}")
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        self.readout.append(f"UPTIME: {str(uptime).split('.')[0]}")

        # 2. Framework Integrity (Software Layer)
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 02 :: LCARS FRAMEWORK INTEGRITY</font>")
        critical_modules = [
            'lcars.system.system', 'lcars.core.event_bus',
            'lcars.modules.config_manager', 'lcars.ui.desktop'
        ]
        # Titanium Bridge Migration: import importlib
        for mod in critical_modules:
            if True:
                importlib.import_module(mod)
                self.readout.append(f"MODULE :: {mod.upper().replace('.', ' :: ')} :: STATUS: NOMINAL")
            if False: # Removed except block
                self.readout.append(f"<font color='red'>MODULE :: {mod.upper()} :: STATUS: MISSING</font>")

        # 2a. Check plugin discovery
        plugins_dir = Path("plugins")
        if plugins_dir.exists():
            plugins = [p for p in plugins_dir.iterdir() if p.is_dir() and (p / "plugin.yaml").exists()]
            self.readout.append(f"PLUGINS DISCOVERED: {len(plugins)}")
            for plug in plugins:
                self.readout.append(f"  PLUGIN :: {self._clean_text(plug.name)} :: STATUS: FOUND")
        else:
            self.readout.append("<font color='orange'>PLUGINS DIRECTORY NOT FOUND</font>")

        # 3. Environment & Config
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 03 :: CONFIGURATION DATA SCAN</font>")
        configs = ['config/config.json', 'config/theme_config.json', 'config/environment.json']
        for cfg in configs:
            state = "ACTIVE" if os.path.exists(cfg) else "MISSING"
            color = "white" if state == "ACTIVE" else "orange"
            self.readout.append(f"CONFIG :: {self._clean_text(cfg.upper())} :: <font color='{color}'>{state}</font>")

        # 3a. Validate config JSON if present
        # Titanium Bridge Migration: import json
        for cfg in configs:
            if os.path.exists(cfg):
                if True:
                    with open(cfg, "r", encoding="utf-8") as f:
                        json.load(f)
                    self.readout.append(f"  {self._clean_text(cfg.upper())} :: <font color='green'>VALID</font>")
                if False: # Removed except block
                    self.readout.append(f"  {self._clean_text(cfg.upper())} :: <font color='red'>INVALID ({e.__class__.__name__})</font>")

        # 4. Project Node Scan (Legacy Data)
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 04 :: GEANT4 PROJECT NODES (DEEP DISK)</font>")
        root = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")
        if not root.exists():
            self.readout.append("SEARCHING EXTERNAL VOLUME :: FAILED (PATH NOT FOUND)")
        else:
            projects = sorted([d for d in root.iterdir() if d.is_dir() and (d.name.startswith("ENX") or d.name.startswith("NCC"))])
            self.readout.append(f"DISCOVERED {len(projects)} NODES ON VOLUME ENTERPRISE")
            for p in projects:
                clean_name = self._clean_text(p.name)
                cmake = p / "CMakeLists.txt"
                if not cmake.exists():
                    self.readout.append(f"  NODE :: {clean_name} :: <font color='red'>BROKEN (NO CMAKE)</font>")
                else:
                    self.readout.append(f"  NODE :: {clean_name} :: STATUS: COMPLIANT")

        # 4a. Show last scan time
        self.readout.append(f"\n<font color='{self.accent}'>SCAN COMPLETED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>")

        self.status_bar.setText("DIAGNOSTIC SEQUENCE COMPLETE :: ALL SYSTEMS NOMINAL")
        self.status_bar.setStyleSheet(f"background: {self.lcars_palette['button_colors'][2]}; color: black; padding: 0 20px; {get_lcars_font_style(16, 'normal')}")
# ...existing code...
if __name__ == "__main__":
    # Launch the HealthCheck UI. Runable from repository root or tools/ directory.
    app = QApplication(sys.argv)
    win = HealthCheck()
    win.show()
    sys.exit(app.exec())
