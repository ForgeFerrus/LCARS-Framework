import os
import sys
import psutil
import platform
import shutil
import re
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTextEdit, QFrame, QScrollArea, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer

from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

class DiagnosticsView(QWidget):
    """Refined LCARS Diagnostic Interface (Multi-Panel Layout)."""
    def __init__(self, system=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.system = system
        self.event_bus = system.event_bus if system else None
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        self.init_ui()
        QTimer.singleShot(500, self.run_diag) 

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)
        
        # --- TOP HEADER AREA ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(2)
        
        self.elbow_top = LCARSElbow("top-left", self.theme['accent'], era=self.era)
        top_bar.addWidget(self.elbow_top)
        
        env_panel = QFrame()
        env_panel.setFixedHeight(60)
        env_panel.setStyleSheet(f"background: {self.theme['accent']}; border: none;")
        env_l = QHBoxLayout(env_panel)
        self.lbl_env = QLabel("SYSTEM CORE STATUS: ACTIVE")
        self.lbl_env.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        env_l.addWidget(self.lbl_env)
        env_l.addStretch()
        
        self.lbl_host = QLabel("SCANNING HOST...")
        self.lbl_host.setStyleSheet(f"color: black; {get_lcars_font_style(16, 'normal')}")
        env_l.addWidget(self.lbl_host)
        top_bar.addWidget(env_panel, 3)
        
        self.main_layout.addLayout(top_bar)
        
        # --- MIDDLE WORK AREA ---
        content_box = QHBoxLayout()
        content_box.setSpacing(5)
        
        # Left Panel (Nodes)
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(200)
        self.left_l = QVBoxLayout(self.left_panel)
        self.left_l.setContentsMargins(0, 0, 0, 0)
        self.left_l.setSpacing(4)
        
        # Left bar segment
        bar = QFrame()
        bar.setStyleSheet(f"background: {self.theme['palette'][2]}; min-height: 20px;")
        self.left_l.addWidget(bar)
        
        self.nodes_container = QFrame()
        self.nodes_l = QVBoxLayout(self.nodes_container)
        self.nodes_l.setContentsMargins(0, 0, 0, 0)
        self.nodes_l.addStretch()
        self.left_l.addWidget(self.nodes_container, 1)
        
        content_box.addWidget(self.left_panel)
        
        # Right Panel (Details)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background: black; color: {self.theme['secondary']}; 
                border: none;
                font-family: 'Consolas', 'Courier New';
                font-size: 15px;
                padding: 20px;
            }}
            QScrollBar:vertical {{
                border: none; background: #050505; width: 10px; margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme['accent']}; min-height: 20px; border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        content_box.addWidget(self.log_area, 1)
        
        self.main_layout.addLayout(content_box, 1)
        
        # --- BOTTOM FOOTER ---
        footer = QHBoxLayout()
        footer.setSpacing(5)
        
        self.elbow_btm = LCARSElbow("bottom-left", self.theme['palette'][1], era=self.era)
        footer.addWidget(self.elbow_btm)
        
        rescan_btn = LCARSButton("INIT RESCAN", self.theme['palette'][2], era=self.era, shape="rectangle")
        rescan_btn.setFixedSize(180, 50)
        rescan_btn.clicked.connect(self.run_diag)
        footer.addWidget(rescan_btn)
        
        self.status_bar = QLabel("AUDIT COMPLETE NOMINAL")
        self.status_bar.setFixedHeight(50)
        self.status_bar.setStyleSheet(f"background: {self.theme['palette'][0]}; color: black; padding: 0 20px; {get_lcars_font_style(16, 'normal')}")
        footer.addWidget(self.status_bar, 1)
        
        self.main_layout.addLayout(footer)

    def _check_cmake_consistency(self, project_path: Path) -> list:
        discrepancies = []
        cmake_file = project_path / "CMakeLists.txt"
        if not cmake_file.exists(): return ["CRITICAL: CMAKE MISSING"]
        
        try:
            content = cmake_file.read_text(encoding='utf-8', errors='ignore')
            local_files = [f.name for f in project_path.glob("*.cc")]
            if (project_path / "src").exists():
                local_files += [f"src/{f.name}" for f in (project_path / "src").glob("*.cc")]
            
            for f in local_files:
                if os.path.basename(f) not in content:
                    discrepancies.append(f"UNLINKED: {f} (DISK YES | CMAKE NO)")
            
            refs = re.findall(r'[\w/\-]+\.cc|[\w/\-]+\.hh', content)
            for r in refs:
                if r.lower() in ["cmakelists.txt", "include", "src"]: continue
                if not (project_path / r).exists():
                    discrepancies.append(f"BROKEN LINK: {r} (DISK NO | CMAKE YES)")
            return discrepancies
        except: return ["SCAN ERROR"]

    def run_diag(self):
        self.status_bar.setText("SCANNING NEURAL CORE :: PLEASE STANDBY")
        self.log_area.clear()
        
        # Section 00: Isolinear Core (ODN Bridge)
        self.log_area.append(f"<font color='{self.theme['accent']}'>◤ SECTION 00 :: ISOLINEAR CONTROL MATRIX</font>")
        if self.system and hasattr(self.system, 'nexus'):
            iso = self.system.nexus.isolinear
            for key, val in iso.directives.items():
                status = "ACTIVE" if val else "STANDBY"
                color = "#99CCFF" if val else "#FF9966"
                self.log_area.append(f"CHIP :: {key.upper()} :: STATUS: {status} :: VAL: {val}")
            
            for arr in ["PRIMARY", "SECONDARY", "AUXILIARY"]:
                chips = iso.get_chip_status(arr)
                active = len([c for c in chips if c['status'] == 'NOMINAL'])
                self.log_area.append(f"ARRAY :: {arr} :: LOAD: {active}/{len(chips)} ONLINE")
        else:
            self.log_area.append("ERROR: NEURAL LINK SEVERED")

        # Section 1: Host Telemetry (Hardware Layer)
        self.log_area.append(f"\n<font color='{self.theme['accent']}'>◤ SECTION 01 :: NEURAL HOST TELEMETRY</font>")
        mem = psutil.virtual_memory()
        cpu_load = psutil.cpu_percent()
        self.log_area.append(f"OS TYPE: {platform.system().upper()} :: KERNEL: {platform.release()}")
        self.log_area.append(f"CORE LOAD: {cpu_load}% :: MEMORY USE: {mem.percent}%")
        usage = shutil.disk_usage('/')
        percent = (usage.used / usage.total) * 100
        self.log_area.append(f"STORAGE :: DISK USE: {percent:.1f}%")
        
        # Section 2: Framework Integrity (Software Layer)
        self.log_area.append(f"\n<font color='{self.theme['accent']}'>◤ SECTION 02 :: LCARS FRAMEWORK INTEGRITY</font>")
        self.log_area.append("NODE :: EVENT BUS :: STATUS: NOMINAL")
        self.log_area.append("NODE :: COORDINATOR :: STATUS: ACTIVE")
        self.log_area.append("NODE :: CONFIG MANAGER :: STATUS: READY")

        # Section 3: Project Nodes Scan (Legacy Data)
        self.log_area.append(f"\n<font color='{self.theme['accent']}'>◤ SECTION 03 :: GEANT4 PROJECT NODES (DEEP DISK)</font>")
        root = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")
        if not root.exists():
            self.log_area.append("ERROR :: ENTERPRISE DATA NODE OFFLINE")
            return

        projects = sorted([d for d in root.iterdir() if d.is_dir() and (d.name.startswith("ENX") or d.name.startswith("NCC"))])
        
        # Update sidebar with project buttons
        for i in reversed(range(self.nodes_l.count())): 
            w = self.nodes_l.itemAt(i).widget()
            if w: w.setParent(None)
        self.nodes_l.addStretch()

        for p in projects:
            clean_name = p.name.replace("_", " ").replace("-", " ")
            btn = LCARSButton(clean_name, self.theme['palette'][3], era=self.era, shape="left")
            btn.setFixedHeight(35)
            self.nodes_l.insertWidget(self.nodes_l.count()-1, btn)
            
            self.log_area.append(f"<font color='white'>NODE :: {clean_name}</font>")
            errors = self._check_cmake_consistency(p)
            if not errors:
                self.log_area.append("  STATUS :: SYSTEM COMPLIANT")
            else:
                for e in errors: 
                    clean_error = e.replace("_", " ").replace("|", "::").replace(":", "::")
                    self.log_area.append(f"  <font color='#FFAA00'>! {clean_error}</font>")
            self.log_area.append("")

        self.status_bar.setText("DIAGNOSTIC SEQUENCE COMPLETE")
