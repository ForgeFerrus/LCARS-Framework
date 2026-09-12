"""
LCARS PROGRAMS PANEL - SYSTEM PROCESSOR
SYSTEM MODULE: UI-PRG-25
PROTOCOL: LCARS / ODYSSEY CORE
DESCRIPTION: System resource management and program orchestration.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QListWidget, QProgressBar
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.base.component import LCARSButton, LCARSElbow
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme

class ProgramsPanel(QWidget):
    """
    Програмна панель для управління процесами та системними ресурсами.
    КРОК 1: Ініціалізація диспетчера завдань та моніторингу процесів.
    """
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: black;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # --- LEFT: PROC CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][1])
        elbow.setFixedSize(180, 60)
        left_ctrl.addWidget(elbow)

        lbl_prg = QLabel("◢ PROGRAM OPS")
        lbl_prg.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_prg)

        # Actions
        actions = ["TASKS", "RESOURCES", "NETWORK", "COMPUTE", "KILL"]
        for i, act in enumerate(actions):
            btn = LCARSButton(act, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setFixedHeight(40)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()

        # Shutdown button
        btn_off = LCARSButton("CORE RESET", "#CC0000", shape="left")
        btn_off.setFixedHeight(50)
        left_ctrl.addWidget(btn_off)

        layout.addLayout(left_ctrl)

        # --- CENTER: PROCESS LIST ---
        center_area = QVBoxLayout()
        
        h_lay = QHBoxLayout()
        lbl_head = QLabel("◢ TASK MANAGER // ACTIVE PROCESSES")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addLayout(h_lay)

        # Process list
        self.proc_list = QListWidget()
        self.proc_list.setStyleSheet(f"""
            QListWidget {{
                background: #000; color: {self.theme['palette'][3]}; border: 1px solid {self.theme['palette'][4]};
                border-radius: 10px; padding: 10px; {get_lcars_font_style(12, 'normal')}
            }}
            QListWidget::item {{ border-bottom: 1px solid #222; padding: 5px; }}
        """)
        center_area.addWidget(self.proc_list, 1)

        layout.addLayout(center_area, 1)

        # --- RIGHT: RESOURCE STATS ---
        right_panel = QVBoxLayout()
        right_panel.setFixedWidth(200)

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        elbow_r.setFixedSize(180, 60)
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ SYSTEM LOAD")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("CPU", 0, 100, 12),
            ("RAM", 0, 100, 45),
            ("GPU", 0, 100, 8),
            ("NET", 0, 100, 2)
        ]
        
        self.bars = {}
        for title, min_v, max_v, val in stats:
            sl = QLabel(f"◤ {title}")
            sl.setStyleSheet(f"color: white; {get_lcars_font_style(10, 'normal')}")
            right_panel.addWidget(sl)
            
            pb = QProgressBar()
            pb.setRange(min_v, max_v)
            pb.setValue(val)
            pb.setFixedHeight(12)
            pb.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid #444; border-radius: 2px; text-align: center; color: black; }}
                QProgressBar::chunk {{ background-color: {self.theme['palette'][5]}; }}
            """)
            right_panel.addWidget(pb)
            self.bars[title] = pb

        right_panel.addStretch()
        layout.addLayout(right_panel)

        # Pulse timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._proc_pulse)
        self.timer.start(2000)
        
        # Initial processes
        self.proc_list.addItems(["lcars.system.system", "lcars.ui.desktop", "geant4.sim.batch", "linguistic.matrix", "neural.link"])

    def _proc_pulse(self):
        """Імітація пульсації системного завантаження."""
        for sign, pb in self.bars.items():
            delta = random.randint(-5, 5)
            val = max(0, min(100, pb.value() + delta))
            pb.setValue(val)
