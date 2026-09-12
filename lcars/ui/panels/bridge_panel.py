"""
LCARS BRIDGE PANEL - COMMAND & CONTROL
SYSTEM MODULE: UI-BRD-25
PROTOCOL: STARFLEET TACTICAL / COMMAND
DESCRIPTION: Primary bridge operations and command interface.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QProgressBar
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme

class BridgePanel(QWidget):
    """
    Місток корабля для управління тактичними та командними функціями.
    КРОК 1: Ініціалізація командного центру та тактичного огляду.
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

        # --- LEFT: COMMAND CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][7])
        elbow.setFixedSize(180, 60)
        left_ctrl.addWidget(elbow)

        lbl_cmd = QLabel("◢ COMMAND OPS")
        lbl_cmd.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_cmd)

        # Command actions
        actions = ["RED ALERT", "YELLOW ALERT", "TACTICAL VIEW", "FLEET STATUS", "LOGS"]
        for i, act in enumerate(actions):
            btn = LCARSButton(act, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setFixedHeight(40)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()

        # Shutdown button
        btn_off = LCARSButton("SYSTEM LOCK", "#666", shape="left")
        btn_off.setFixedHeight(50)
        left_ctrl.addWidget(btn_off)

        layout.addLayout(left_ctrl)

        # --- CENTER: TACTICAL OVERVIEW ---
        center_area = QVBoxLayout()
        
        head = LCARSContour(color=self.theme['palette'][8], height=30)
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("◢ TACTICAL OVERVIEW // MISSION TIMELINE")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Tactical map display
        self.map_box = QFrame()
        self.map_box.setStyleSheet(f"border: 2px solid {self.theme['palette'][9]}; background: #100505;")
        m_lay = QVBoxLayout(self.map_box)
        m_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_obj = QLabel("◤ OBJECTIVE: NEUTRALIZE BORG CUBE")
        lbl_obj.setStyleSheet(f"color: #FF6666; {get_lcars_font_style(20, 'normal')}")
        m_lay.addWidget(lbl_obj)
        
        # Shield status
        sl = QLabel("◤ SHIELD STATUS")
        sl.setStyleSheet(f"color: #66CCFF; {get_lcars_font_style(12, 'normal')}")
        m_lay.addWidget(sl)
        
        self.shield_bar = QProgressBar()
        self.shield_bar.setRange(0, 100)
        self.shield_bar.setValue(100)
        self.shield_bar.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid #444; border-radius: 5px; text-align: center; color: black; }}
            QProgressBar::chunk {{ background-color: #3366CC; }}
        """)
        m_lay.addWidget(self.shield_bar)

        center_area.addWidget(self.map_box, 1)

        layout.addLayout(center_area, 1)

        # --- RIGHT: SYSTEM STATUS ---
        right_panel = QVBoxLayout()
        right_panel.setFixedWidth(200)

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        elbow_r.setFixedSize(180, 60)
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ SHIP SYSTEMS")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("PHASERS", "READY", "#00FF00"),
            ("SHIELDS", "CHARGED", "#00FF00"),
            ("SENSORS", "ONLINE", "#FFCC00"),
            ("TRANSPORTER", "READY", "#66CCFF")
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

        # Alert pulse timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._alert_pulse)
        self.timer.start(1000)

    def _alert_pulse(self):
        """Імітація пульсації тривоги."""
        # Simple random logic for shield fluctuation
        if self.shield_bar.value() < 20:
             self.shield_bar.setValue(100)
        else:
             self.shield_bar.setValue(self.shield_bar.value() - random.randint(0, 2))
