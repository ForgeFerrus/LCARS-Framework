
import sys
import os
import psutil
import platform
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QTextEdit, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.ui.base.widgets import LCARSElbow, LCARSButton
from lcars.themes.palette import LCARSEra, get_era_palette, get_random_button_color, get_lcars_font_style
from lcars.modules.config_manager import config_manager
from lcars.system.localization import LOCALIZATION as Language
import shutil
import socket
try:
    import GPUtil
except ImportError:
    GPUtil = None

class HealthCheck(QMainWindow):
    """Standalone High-Fidelity LCARS Diagnostic Hub (No Windows Elements), розширена версія."""
    # Сигнал для підключення до системи (наприклад, для зовнішнього моніторингу)
    diagnosticsCompleted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.era = LCARSEra.LCARS_25TH
        # palette should be the full era palette (not a single color)
        self.palette = get_era_palette(self.era)
        self.accent = self.palette.get('button_colors', ["#FF9900"])[0]
        # Read config for paths and behavior
        try:
            geant_cfg = config_manager.get('ui', 'geant4_root')
        except Exception:
            geant_cfg = None
        self.geant_root = Path(geant_cfg) if geant_cfg else Path(os.environ.get('GEANT4_ROOT', Path.home() / 'Geant4' / 'Enterprise'))

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet("background-color: black; color: white;")

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(5)

        self._auto_refresh_timer = QTimer(self)
        self._auto_refresh_timer.timeout.connect(self.run_diag)
        self._auto_refresh_timer.setInterval(60000)  # 1 хвилина

        self.setup_ui()
        QTimer.singleShot(800, self.run_diag)

    def setup_ui(self):
        # --- HEADER AREA (FLAT BLOCKS) ---
        header = QHBoxLayout()
        header.setSpacing(2)
        
        self.top_elbow = LCARSElbow("top-left", self.accent, era=self.era)
        header.addWidget(self.top_elbow)
        
        title_block = QFrame()
        title_block.setFixedHeight(65)
        title_block.setStyleSheet(f"background: {self.accent}; border: none;")
        tl = QHBoxLayout(title_block)
        
        title_text = Language.translate('DIAGNOSTICS') + " :: SYSTEM WIDE INTEGRITY SCAN"
        t_label = QLabel(title_text)
        t_label.setStyleSheet(f"color: black; {get_lcars_font_style(22, 'normal')}")
        tl.addWidget(t_label)
        tl.addStretch()
        
        self.clock = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.clock.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        tl.addWidget(self.clock)
        header.addWidget(title_block, 1)
        self.main_layout.addLayout(header)

        # --- CENTER DATA AREA ---
        content = QHBoxLayout()
        content.setSpacing(5)
        
        # Left sidebar (Telemetry)
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(220)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(0, 0, 0, 0)
        self.side_layout.setSpacing(4)
        

        # Кнопка оновлення
        self.btn_refresh = LCARSButton("UPDATE", self.accent, era=self.era, shape="left")
        self.btn_refresh.setFixedHeight(45)
        self.btn_refresh.clicked.connect(self.run_diag)
        self.side_layout.addWidget(self.btn_refresh)

        # Кнопка автопоновлення
        self.btn_auto = LCARSButton("AUTO :: OFF", "#888888", era=self.era, shape="left")
        self.btn_auto.setFixedHeight(45)
        self.btn_auto.setCheckable(True)
        self.btn_auto.toggled.connect(self.toggle_auto_refresh)
        self.side_layout.addWidget(self.btn_auto)

        self.btn_exit = LCARSButton("DISCONNECT", "#555555", era=self.era, shape="left")
        self.btn_exit.setFixedHeight(45)
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
        
        self.btm_elbow = LCARSElbow("bottom-left", self.palette['button_colors'][1], era=self.era)
        footer.addWidget(self.btm_elbow)
        
        self.status_bar = QLabel("INITIALIZING PROTOCOLS")
        self.status_bar.setFixedHeight(50)
        self.status_bar.setStyleSheet(f"background: {self.palette['button_colors'][1]}; color: black; padding: 0 20px; {get_lcars_font_style(16, 'normal')}")
        footer.addWidget(self.status_bar, 1)
        self.main_layout.addLayout(footer)

    def _clean_text(self, text):
        """Removes underscores and slashes for LCARS compliance."""
        return text.replace("_", " ").replace("/", " :: ").replace("\\", " :: ")


    def run_diag(self):
        self.status_bar.setText("NEURAL NODES SCANNING :: PLEASE STANDBY")
        self.readout.clear()
        diag_data = {}

        # 1. Host Telemetry (Hardware Layer)
        self.readout.append(f"<font color='{self.accent}'>◤ SECTION 01 :: NEURAL HOST TELEMETRY</font>")
        mem = psutil.virtual_memory()
        cpu_load = psutil.cpu_percent(interval=None)
        os_type = platform.system().upper()
        kernel = platform.release()
        # determine disk root from config or environment
        try:
            root_path = self.geant_root if self.geant_root and self.geant_root.exists() else Path('/' if os.name != 'nt' else Path(Path.cwd()).anchor)
            usage = shutil.disk_usage(str(root_path))
            disk_usage_percent = (usage.used / usage.total) * 100 if usage.total else 0
        except Exception:
            try:
                usage = shutil.disk_usage('.')
                disk_usage_percent = (usage.used / usage.total) * 100 if usage.total else 0
            except Exception:
                disk_usage_percent = 0
        self.readout.append(f"OS TYPE: {os_type} :: KERNEL: {kernel}")
        self.readout.append(f"CORE LOAD: {cpu_load}% :: MEMORY USE: {mem.percent}%")
        self.readout.append(f"STORAGE :: DISK USE: {disk_usage_percent:.2f}%")
        diag_data['host'] = {
            'os': os_type,
            'kernel': kernel,
            'cpu_load': cpu_load,
            'mem_percent': mem.percent,
            'disk_percent': disk_usage_percent
        }

        # 1.1 Network
        self.readout.append(f"NETWORK :: HOSTNAME: {socket.gethostname()} :: IP: {self._get_ip()}")
        diag_data['host']['hostname'] = socket.gethostname()
        diag_data['host']['ip'] = self._get_ip()

        # 1.2 GPU
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    for i, gpu in enumerate(gpus):
                        self.readout.append(f"GPU-{i}: {gpu.name} :: LOAD: {gpu.load*100:.1f}% :: MEM: {getattr(gpu,'memoryUsed',0)}/{getattr(gpu,'memoryTotal',0)}MB")
                else:
                    self.readout.append("GPU: NOT DETECTED")
            except Exception:
                self.readout.append("GPU: GPUtil ERROR")
        else:
            self.readout.append("GPU: GPUtil NOT INSTALLED")

        # 2. Framework Integrity (Software Layer)
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 02 :: LCARS FRAMEWORK INTEGRITY</font>")
        critical_modules = [
            'lcars.core.system', 'lcars.core.event_bus',
            'lcars.modules.config_manager', 'lcars.ui.desktop'
        ]
        import importlib
        diag_data['modules'] = {}
        for mod in critical_modules:
            try:
                importlib.import_module(mod)
                self.readout.append(f"MODULE :: {mod.upper().replace('.', ' :: ')} :: STATUS: NOMINAL")
                diag_data['modules'][mod] = True
            except ImportError:
                self.readout.append(f"<font color='red'>MODULE :: {mod.upper()} :: STATUS: MISSING</font>")
                diag_data['modules'][mod] = False

        # 3. Environment & Config
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 03 :: CONFIGURATION DATA SCAN</font>")
        configs = [
            config_manager.default_config_path or Path('config/config.json'),
            Path('config/theme_config.json'),
            Path('config/environment.json'),
        ]
        diag_data['configs'] = {}
        for cfg in configs:
            try:
                cfg_path = Path(cfg)
            except Exception:
                cfg_path = Path(cfg)
            state = "ACTIVE" if cfg_path.exists() else "MISSING"
            color = "white" if state == "ACTIVE" else "orange"
            self.readout.append(f"CONFIG :: {self._clean_text(str(cfg_path).upper())} :: <font color='{color}'>{state}</font>")
            diag_data['configs'][str(cfg_path)] = state

        # 4. Project Node Scan (Legacy Data)
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 04 :: GEANT4 PROJECT NODES (DEEP DISK)</font>")
        root = self.geant_root
        diag_data['geant4_nodes'] = []
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
                    diag_data['geant4_nodes'].append({'name': clean_name, 'status': 'BROKEN'})
                else:
                    self.readout.append(f"  NODE :: {clean_name} :: STATUS: COMPLIANT")
                    diag_data['geant4_nodes'].append({'name': clean_name, 'status': 'COMPLIANT'})

        # 5. Python Environment
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 05 :: PYTHON ENVIRONMENT</font>")
        py_ver = sys.version.replace('\n', ' ')
        self.readout.append(f"PYTHON VERSION: {py_ver}")
        self.readout.append(f"PYTHON EXECUTABLE: {sys.executable}")
        diag_data['python'] = {'version': py_ver, 'executable': sys.executable}

        # 6. User/Session
        self.readout.append(f"\n<font color='{self.accent}'>◤ SECTION 06 :: USER SESSION</font>")
        user = os.environ.get('USERNAME') or os.environ.get('USER') or os.environ.get('LOGNAME') or 'UNKNOWN'
        self.readout.append(f"USER: {user}")
        diag_data['user'] = user

        self.status_bar.setText("DIAGNOSTIC SEQUENCE COMPLETE :: ALL SYSTEMS NOMINAL")
        self.status_bar.setStyleSheet(f"background: {self.palette['button_colors'][2]}; color: black; padding: 0 20px; {get_lcars_font_style(16, 'normal')}")

        # Сигнал для інтеграції з системою
        self.diagnosticsCompleted.emit(diag_data)

    def _get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "N/A"

    def toggle_auto_refresh(self, checked):
        if checked:
            self.btn_auto.setText("АВТО :: ON")
            self.btn_auto.setStyleSheet(f"background: {self.accent}; color: black;")
            self._auto_refresh_timer.start()
        else:
            self.btn_auto.setText("АВТО :: OFF")
            self.btn_auto.setStyleSheet("background: #888888; color: black;")
            self._auto_refresh_timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HealthCheck()
    win.show()
    sys.exit(app.exec())
