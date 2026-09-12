from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame, QScrollArea, QProgressBar, QApplication
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.core.event_bus import EventType, Event
from typing import Optional

class OperationsView(QWidget):
    """High-fidelity LCARS Operations Panel."""
    def __init__(self, event_bus, task_executor, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.event_bus = event_bus
        self.task_executor = task_executor
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Left Column: Controls
        left_panel = QFrame()
        left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        header = QLabel("MISSION OPS")
        header.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(28, 'normal')}")
        left_layout.addWidget(header)

        self.btn_run = LCARSButton("INITIATE TASK", "#FFCC66", era=self.era)
        self.btn_run.clicked.connect(self._on_run_clicked)
        left_layout.addWidget(self.btn_run)

        self.btn_abort = LCARSButton("ABORT ALL", "#CC0000", era=self.era)
        self.btn_abort.clicked.connect(self._on_abort_clicked)
        left_layout.addWidget(self.btn_abort)

        left_layout.addStretch()
        
        # System Status in left panel
        status_box = QFrame()
        status_box.setStyleSheet(f"border-top: 2px solid {self.theme['secondary']}; padding-top: 10px;")
        status_layout = QVBoxLayout(status_box)
        
        status_label = QLabel("TASK PROGRESS")
        status_label.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(14, 'normal')}")
        status_layout.addWidget(status_label)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid {self.theme['accent']}; border-radius: 5px; text-align: center; color: black; }}
            QProgressBar::chunk {{ background-color: {self.theme['accent']}; }}
        """)
        self.progress.setValue(0)
        status_layout.addWidget(self.progress)
        
        left_layout.addWidget(status_box)

        # Right Column: Terminal/Logs
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        log_header = QLabel("◤ SYSTEM LOG -实时监测")
        log_header.setStyleSheet(f"color: {self.theme['secondary']}; {get_lcars_font_style(18, 'normal')}")
        right_layout.addWidget(log_header)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: black; color: {self.theme['accent']};
                border: 2px solid {self.theme['secondary']};
                border-radius: 10px;
                padding: 10px;
                {get_lcars_font_style(14, 'normal')}
            }}
        """)
        self.log_display.append("<font color='#AAAAAA'>SYSTEM READY. STANDING BY FOR COMMANDS.</font>")
        
        right_layout.addWidget(self.log_display)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

    def _on_run_clicked(self):
        self._append("<font color='#FFCC66'>[CMD]</font> INITIATING SAMPLE TASK: GEANT4 BATCH...")
        self.progress.setValue(10)
        # Mock task execution
        QTimer.singleShot(1000, lambda: self._append("<font color='#99CCFF'>[SYS]</font> SCANNING FOR NEUTRINO SIGNATURES..."))
        QTimer.singleShot(2000, lambda: self.progress.setValue(45))
        QTimer.singleShot(2500, lambda: self._append("<font color='#99CCFF'>[SYS]</font> DATA STREAM ESTABLISHED at 1024 kbps."))
        QTimer.singleShot(3500, lambda: self._append("<font color='#00FF00'>[OK]</font> NEUTRINO FLOW STABILIZED."))
        QTimer.singleShot(4000, lambda: self.progress.setValue(100))

    def _append(self, text):
        self.log_display.append(text)

    def _on_abort_clicked(self):
        self._append("<font color='#CC0000'>[ALERT]</font> ABORTING ALL OPERATIONS.")
        self.progress.setValue(0)
        try:
            self.task_executor.abort_all()
        except:
             pass
