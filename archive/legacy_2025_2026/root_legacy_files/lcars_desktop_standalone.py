"""
LCARS Desktop - Standalone Full Version
Complete LCARS interface that works independently
"""
import sys
import random
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QGridLayout, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

class LCARSDesktop(QMainWindow):
    """Complete LCARS System Workstation - Standalone Version"""
    def __init__(self, era_key: str = "25th", faction_key: str = "federation"):
        super().__init__()
        
        # LCARS Theme Configuration
        self.era = era_key
        self.faction = faction_key
        self.setup_theme()
        
        # Window setup
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setStyleSheet(f"background-color: {self.theme['bg']}; color: white;")
        
        self.is_alert = False
        self.init_ui()
        
        # Clock & Stats Timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        self.stat_timer = QTimer(self)
        self.stat_timer.timeout.connect(self._update_meters)
        self.stat_timer.start(2000)
        
        # ESC to exit
        self.shortcut_exit = None

    def setup_theme(self):
        """Setup LCARS theme colors"""
        themes = {
            "22nd": {'bg': '#000000', 'accent': '#FF6B35', 'secondary': '#FF8C42'},
            "23rd": {'bg': '#000000', 'accent': '#00B4D8', 'secondary': '#0077B6'},
            "24th": {'bg': '#000000', 'accent': '#FFAA00', 'secondary': '#FF8800'},
            "25th": {'bg': '#000000', 'accent': '#FFAA00', 'secondary': '#FF8800'},
            "29th": {'bg': '#000000', 'accent': '#00FF41', 'secondary': '#00CC33'}
        }
        
        self.theme = themes.get(self.era, themes["25th"])
        self.accent = self.theme['accent']
        self.secondary = self.theme['secondary']

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # 1. HEADER - Official System Bar
        header = QHBoxLayout()
        header.setSpacing(5)
        
        # Left elbow corner
        self.header_elbow = QFrame()
        self.header_elbow.setFixedSize(180, 80)
        self.header_elbow.setStyleSheet(f"""
            background-color: {self.accent}; 
            border-top-left-radius: 25px;
            border-bottom-right-radius: 15px;
        """)
        header.addWidget(self.header_elbow)

        # Title bar
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet(f"background-color: {self.accent}; border-radius: 5px;")
        t_layout = QHBoxLayout(self.title_bar)
        
        self.lbl_title = QLabel(f"◤ SYSTEM NODE / FEDERATION COMMAND / SECURE SESSION")
        self.lbl_title.setStyleSheet("""
            color: black; 
            font-family: 'Courier New', monospace; 
            font-size: 20px; 
            font-weight: bold;
        """)
        t_layout.addWidget(self.lbl_title)
        t_layout.addStretch()
        
        self.lbl_clock = QLabel("--:--:--")
        self.lbl_clock.setStyleSheet("""
            color: black; 
            font-family: 'Courier New', monospace; 
            font-size: 18px; 
            font-weight: bold;
        """)
        t_layout.addWidget(self.lbl_clock)
        
        header.addWidget(self.title_bar, 1)
        
        # Right cap
        self.header_cap = QFrame()
        self.header_cap.setFixedSize(120, 50)
        self.header_cap.setStyleSheet(f"""
            background-color: {self.secondary}; 
            border-top-right-radius: 20px;
        """)
        header.addWidget(self.header_cap)
        
        main_layout.addLayout(header)

        # 2. WORKSPACE AREA
        content_row = QHBoxLayout()
        content_row.setSpacing(10)

        # Left Sidebar (App Selection)
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(8)
        
        # Connection line
        conn = QFrame()
        conn.setFixedSize(180, 15)
        conn.setStyleSheet(f"""
            background: {self.accent}; 
            border-bottom-left-radius: 15px;
        """)
        self.sidebar.addWidget(conn)

        nav_items = [
            ("DASH", self.show_dashboard, "#FF9900"),
            ("DATA", self.show_projects, "#99CCFF"),
            ("OPS", self.show_engine, "#CC0000"),
            ("TERM", self.show_terminal, "#B1957A"),
            ("STAT", self.show_sensors, "#FFCC66"),
            ("AI", self.show_computer, "#CC99FF")
        ]

        for text, func, color in nav_items:
            btn = self.create_lcars_button(text, color, "left")
            btn.setFixedSize(160, 45)
            btn.clicked.connect(func)
            self.sidebar.addWidget(btn)

        self.sidebar.addStretch()
        
        # Alert button
        self.alert_btn = self.create_lcars_button("ALERT", "#FF0000", "left")
        self.alert_btn.setFixedSize(160, 45)
        self.alert_btn.clicked.connect(self.toggle_alert)
        self.sidebar.addWidget(self.alert_btn)
        
        # Exit button
        off_btn = self.create_lcars_button("EXIT", "#444", "left")
        off_btn.setFixedSize(160, 45)
        off_btn.clicked.connect(self.close)
        self.sidebar.addWidget(off_btn)
        
        content_row.addLayout(self.sidebar)

        # Main Workspace View
        self.view_container = QFrame()
        self.view_container.setStyleSheet(f"""
            border: 2px solid {self.accent}; 
            border-radius: 25px; 
            background: #000;
        """)
        v_layout = QVBoxLayout(self.view_container)
        v_layout.setContentsMargins(10, 10, 10, 10)
        
        self.stack = QStackedWidget()
        v_layout.addWidget(self.stack)
        
        self.dashboard = self._create_dashboard()
        self.stack.addWidget(self.dashboard)
        
        # Create other views
        self.sensors_view = self._create_sensors_view()
        self.stack.addWidget(self.sensors_view)
        
        self.projects_view = self._create_projects_view()
        self.stack.addWidget(self.projects_view)
        
        self.engine_view = self._create_engine_view()
        self.stack.addWidget(self.engine_view)
        
        self.terminal_view = self._create_terminal_view()
        self.stack.addWidget(self.terminal_view)
        
        self.computer_view = self._create_computer_view()
        self.stack.addWidget(self.computer_view)
        
        content_row.addWidget(self.view_container, 1)

        # Right Monitoring Panel
        self.monitor_panel = QFrame()
        self.monitor_panel.setFixedWidth(200)
        self.monitor_panel.setStyleSheet(f"""
            background: #080808; 
            border-left: 2px solid {self.secondary}; 
            border-radius: 10px;
        """)
        m_layout = QVBoxLayout(self.monitor_panel)
        
        m_layout.addWidget(QLabel("◤ NODE METRICS"))
        
        for name, color in [("CPU", "#99CCFF"), ("MEM", "#CC99FF"), ("PWR", "#FFCC66")]:
            m_layout.addWidget(QLabel(name))
            bar = QProgressBar()
            bar.setFixedHeight(12)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{ 
                    background: #111; 
                    border: none; 
                }} 
                QProgressBar::chunk {{ 
                    background: {color}; 
                }}
            """)
            bar.setValue(random.randint(20, 50))
            m_layout.addWidget(bar)
            setattr(self, f"mini_{name.lower()}", bar)
        
        m_layout.addStretch()
        m_layout.addWidget(QLabel("◤ SECURE LOG"))
        self.mini_log = QLabel("AUTH: ADMIRAL\nTHREAT: NOMINAL\nENCR: active_AES")
        self.mini_log.setStyleSheet(f"color: {self.accent}; font-size: 11px; padding: 5px;")
        m_layout.addWidget(self.mini_log)
        
        content_row.addWidget(self.monitor_panel)

        main_layout.addLayout(content_row, 1)

        # 3. FOOTER
        footer = QHBoxLayout()
        self.access_btn = self.create_lcars_button("ACCESS", "#FF9900", "normal")
        self.access_btn.setFixedSize(220, 50)
        self.access_btn.clicked.connect(self.show_start_menu)
        footer.addWidget(self.access_btn)
        
        self.status_line = QFrame()
        self.status_line.setFixedHeight(30)
        self.status_line.setStyleSheet(f"""
            background: {self.accent}; 
            border-bottom-left-radius: 15px; 
            border-bottom-right-radius: 15px;
        """)
        footer.addWidget(self.status_line, 1)
        
        main_layout.addLayout(footer)

    def create_lcars_button(self, text, color, shape="normal"):
        """Create LCARS-style button"""
        btn = QPushButton(text)
        
        if shape == "left":
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    border: none;
                    border-top-right-radius: 25px;
                    border-bottom-right-radius: 25px;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: white;
                }}
                QPushButton:pressed {{
                    background-color: #FFAA00;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    border: 2px solid {color};
                    border-radius: 5px;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background-color: white;
                    border-color: white;
                }}
                QPushButton:pressed {{
                    background-color: #FFAA00;
                    border-color: #FFAA00;
                }}
            """)
        
        return btn

    def update_clock(self):
        self.lbl_clock.setText(datetime.now().strftime("%H:%M:%S"))

    def _update_meters(self):
        try:
            self.mini_cpu.setValue(random.randint(5, 45))
            self.mini_mem.setValue(random.randint(20, 60))
            self.mini_pwr.setValue(random.randint(85, 95))
        except:
            pass

    def _create_dashboard(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        lbl = QLabel("◤ LCARS COMMAND INTERFACE ◤")
        lbl.setStyleSheet(f"""
            color: {self.accent}; 
            font-family: 'Courier New', monospace; 
            font-size: 32px; 
            font-weight: bold;
        """)
        l.addWidget(lbl)
        l.addSpacing(20)
        
        grid = QGridLayout()
        grid.setSpacing(25)
        
        apps = [
            ("MISSION OPERATIONS", self.show_engine, "#CC0000"),
            ("SCIENCE SENSORS", self.show_sensors, "#FFCC66"),
            ("ARCHIVE ACCESS", self.show_projects, "#99CCFF"),
            ("COORD INTERFACE", self.show_terminal, "#B1957A"),
            ("NEURAL LINK", self.show_computer, "#CC99FF"),
            ("FILE SYSTEM", self.show_programs, "#00CC00")
        ]
        
        for i, (name, func, color) in enumerate(apps):
            box = QFrame()
            box.setFixedSize(200, 150)
            box.setStyleSheet(f"""
                background: #111; 
                border: 1px solid {color}; 
                border-radius: 12px;
            """)
            box_l = QVBoxLayout(box)
            
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                background: {color}; 
                color: black; 
                border-radius: 8px; 
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
            """)
            btn.setFixedSize(160, 80)
            btn.clicked.connect(func)
            box_l.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)
            
            grid.addWidget(box, i // 3, i % 3)
            
        l.addLayout(grid)
        l.addStretch()
        return w

    def _create_sensors_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("◤ SCIENCE SENSORS ◤")
        title.setStyleSheet(f"""
            color: {self.accent}; 
            font-family: 'Courier New', monospace; 
            font-size: 28px; 
            font-weight: bold;
        """)
        l.addWidget(title)
        
        # Sensor data grid
        grid = QGridLayout()
        sensors = [
            ("LONG RANGE", "ONLINE", "#00FF00"),
            ("SHORT RANGE", "ONLINE", "#00FF00"),
            ("ASTROMETRICS", "CALIBRATING", "#FFAA00"),
            ("TEMPORAL", "STANDBY", "#FF8800"),
            ("BIOLOGICAL", "SCANNING", "#00AAFF"),
            ("GEOLOGICAL", "ACTIVE", "#00FF00")
        ]
        
        for i, (name, status, color) in enumerate(sensors):
            frame = QFrame()
            frame.setStyleSheet(f"""
                background: #111;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            """)
            layout = QVBoxLayout(frame)
            
            name_label = QLabel(name)
            name_label.setStyleSheet(f"""
                color: {color};
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
            """)
            layout.addWidget(name_label)
            
            status_label = QLabel(status)
            status_label.setStyleSheet(f"""
                color: white;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            """)
            layout.addWidget(status_label)
            
            grid.addWidget(frame, i // 3, i % 3)
        
        l.addLayout(grid)
        l.addStretch()
        return w

    def _create_projects_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("◤ ARCHIVE ACCESS ◤")
        title.setStyleSheet(f"""
            color: {self.accent}; 
            font-family: 'Courier New', monospace; 
            font-size: 28px; 
            font-weight: bold;
        """)
        l.addWidget(title)
        
        # Project list
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            background: #111;
            border: 2px solid #99CCFF;
            border-radius: 10px;
            padding: 20px;
        """)
        list_layout = QVBoxLayout(list_frame)
        
        projects = [
            "STARFLEET DATABASE",
            "MISSION LOGS",
            "TECHNICAL MANUALS",
            "PERSONNEL FILES",
            "SHIP REGISTRY",
            "TACTICAL DATABASE"
        ]
        
        for project in projects:
            btn = QPushButton(project)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #99CCFF;
                    border: 1px solid #99CCFF;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    padding: 8px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #99CCFF;
                    color: black;
                }
            """)
            list_layout.addWidget(btn)
        
        l.addWidget(list_frame)
        l.addStretch()
        return w

    def _create_engine_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("◤ MISSION OPERATIONS ◤")
        title.setStyleSheet(f"""
            color: {self.accent}; 
            font-family: 'Courier New', monospace; 
            font-size: 28px; 
            font-weight: bold;
        """)
        l.addWidget(title)
        
        # Operations grid
        grid = QGridLayout()
        ops = [
            ("WARP DRIVE", "ONLINE", "#00FF00"),
            ("IMPULSE", "STANDBY", "#FFAA00"),
            ("SHIELDS", "100%", "#00FF00"),
            ("PHASERS", "CHARGED", "#FF8800"),
            ("TORPEDOES", "LOADED", "#00FF00"),
            ("TRANSPORTER", "READY", "#00FF00")
        ]
        
        for i, (name, status, color) in enumerate(ops):
            frame = QFrame()
            frame.setStyleSheet(f"""
                background: #111;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            """)
            layout = QVBoxLayout(frame)
            
            name_label = QLabel(name)
            name_label.setStyleSheet(f"""
                color: {color};
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
            """)
            layout.addWidget(name_label)
            
            status_label = QLabel(status)
            status_label.setStyleSheet(f"""
                color: white;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            """)
            layout.addWidget(status_label)
            
            grid.addWidget(frame, i // 3, i % 3)
        
        l.addLayout(grid)
        l.addStretch()
        return w

    def _create_terminal_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("◤ SECURE TERMINAL ◤")
        title.setStyleSheet(f"""
            color: {self.accent}; 
            font-family: 'Courier New', monospace; 
            font-size: 28px; 
            font-weight: bold;
        """)
        l.addWidget(title)
        
        # Terminal display
        terminal = QFrame()
        terminal.setStyleSheet("""
            background: #000;
            border: 2px solid #B1957A;
            border-radius: 10px;
            padding: 20px;
        """)
        term_layout = QVBoxLayout(terminal)
        
        term_output = QLabel("""
STARFLEET COMMAND INTERFACE v4.2
Authentication: ADMIRAL LEVEL 10
Last login: Stardate 47943.2

> System diagnostics running...
> All systems nominal
> Awaiting command...

Type 'help' for available commands
        """)
        term_output.setStyleSheet("""
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        """)
        term_layout.addWidget(term_output)
        
        l.addWidget(terminal)
        l.addStretch()
        return w

    def _create_computer_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("◤ NEURAL LINK INTERFACE ◤")
        title.setStyleSheet(f"""
            color: {self.accent}; 
            font-family: 'Courier New', monospace; 
            font-size: 28px; 
            font-weight: bold;
        """)
        l.addWidget(title)
        
        # AI Interface
        ai_frame = QFrame()
        ai_frame.setStyleSheet("""
            background: #111;
            border: 2px solid #CC99FF;
            border-radius: 10px;
            padding: 20px;
        """)
        ai_layout = QVBoxLayout(ai_frame)
        
        ai_status = QLabel("COMPUTER: Online and ready")
        ai_status.setStyleSheet("""
            color: #CC99FF;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: bold;
        """)
        ai_layout.addWidget(ai_status)
        
        ai_response = QLabel("""
Neural interface active...
Processing capacity: 87%
Quantum core: Stable
Language processors: Online
Ready for interface...
        """)
        ai_response.setStyleSheet("""
            color: white;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        """)
        ai_layout.addWidget(ai_response)
        
        l.addWidget(ai_frame)
        l.addStretch()
        return w

    def show_dashboard(self): 
        self.stack.setCurrentIndex(0)
    
    def show_sensors(self): 
        self.stack.setCurrentIndex(1)

    def show_projects(self): 
        self.stack.setCurrentIndex(2)

    def show_engine(self): 
        self.stack.setCurrentIndex(3)

    def show_terminal(self): 
        self.stack.setCurrentIndex(4)

    def show_computer(self): 
        self.stack.setCurrentIndex(5)

    def show_programs(self):
        print("Programs view - would show file manager")

    def show_start_menu(self):
        print("Start menu - would show full menu overlay")

    def toggle_alert(self):
        self.is_alert = not self.is_alert
        color = "#CC0000" if self.is_alert else self.accent
        
        self.view_container.setStyleSheet(f"""
            border: 2px solid {color}; 
            border-radius: 25px; 
            background: #000;
        """)
        self.header_elbow.setStyleSheet(f"""
            background-color: {color}; 
            border-top-left-radius: 25px;
            border-bottom-right-radius: 15px;
        """)
        self.title_bar.setStyleSheet(f"""
            background-color: {color}; 
            border-radius: 5px;
        """)
        
        self.lbl_title.setText(f"◤ SYSTEM NODE / {'RED ALERT' if self.is_alert else 'FEDERATION'} COMMAND / SECURE SESSION")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

def main():
    """Launch LCARS Desktop"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Parse args
    era = "25th"
    faction = "federation"
    for i, arg in enumerate(sys.argv):
        if arg == "--era" and i+1 < len(sys.argv): 
            era = sys.argv[i+1]
        if arg == "--faction" and i+1 < len(sys.argv): 
            faction = sys.argv[i+1]
        
    window = LCARSDesktop(era, faction)
    window.show()
    
    print(f"[LCARS] Desktop launched - Era: {era}, Faction: {faction}")
    print("[LCARS] Press ESC to exit")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
