"""
LCARS COMMUNICATIONS PANEL - COMMAND CENTER
SYSTEM MODULE: UI-COM-25
PROTOCOL: SUBSPACE / LINGUISTIC MATRIX
DESCRIPTION: Integrated communication and translation interface.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme

class CommunicationPanel(QWidget):
    """
    Комунікаційна панель для управління підпросторовими частотами та перекладачем.
    КРОК 1: Ініціалізація інтерфейсу зв'язку та мовних матриць.
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

        # --- LEFT: COMMS CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][3])
        elbow.setFixedSize(180, 60)
        left_ctrl.addWidget(elbow)

        lbl_comms = QLabel("◢ SUBSPACE FREQ")
        lbl_comms.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_comms)

        # Frequency channels
        channels = ["CMD FREQ", "TAC FREQ", "ENG FREQ", "MED FREQ", "HAIL ALL"]
        for i, ch in enumerate(channels):
            btn = LCARSButton(ch, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setFixedHeight(40)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()

        # Alert level
        btn_alert = LCARSButton("EMERGENCY HAIL", "#CC0000", shape="left")
        btn_alert.setFixedHeight(50)
        left_ctrl.addWidget(btn_alert)

        layout.addLayout(left_ctrl)

        # --- CENTER: SIGNAL MONITOR ---
        center_area = QVBoxLayout()
        
        head = LCARSContour(color=self.theme['palette'][4], height=30)
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("◢ SIGNAL MONITOR // LINGUISTIC DECODER")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Comms log area
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setStyleSheet(f"""
            background: #000; color: #FFF; border: 2px solid {self.theme['palette'][5]};
            border-radius: 10px; padding: 10px; {get_lcars_font_style(12, 'normal')}
        """)
        self.logs.setText("◤ SYSTEM: COMMS READY\n◤ AWAITING SIGNAL...\n")
        center_area.addWidget(self.logs, 1)

        layout.addLayout(center_area, 1)

        # --- RIGHT: LINGUISTIC STATUS ---
        right_panel = QVBoxLayout()
        right_panel.setFixedWidth(200)

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        elbow_r.setFixedSize(180, 60)
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ MATRIX STATUS")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("UNIVERSAL TX", "ENGAGED", "#00FF00"),
            ("ENCRYPTION", "LEVEL 10", "#FFCC00"),
            ("BUFFER", "99.9%", "#66CCFF"),
            ("LATENCY", "0.002ms", "#66CCFF")
        ]

        for title, val, color in stats:
            box = QFrame()
            box.setStyleSheet(f"background: #111; border-left: 5px solid {color}; border-radius: 4px;")
            bl = QVBoxLayout(box)
            tl = QLabel(title)
            tl.setStyleSheet(f"color: white; {get_lcars_font_style(10, 'normal')}")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {color}; {get_lcars_font_style(12, 'normal')}")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)

        right_panel.addStretch()
        layout.addLayout(right_panel)

        # Random log timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._add_log)
        self.timer.start(5000)

    def _add_log(self):
        msgs = [
            "[SYS] Subspace beacon detected in Sector 001",
            "[MSG] Incoming message from Starbase 1",
            "[TX] Outgoing transmission to USS Enterprise",
            "[LING] Metric analysis: Klingon dialect detected",
            "[SEC] Encryption layer updated to Level 11"
        ]
        self.logs.append(f"◤ {random.choice(msgs)}")
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())
