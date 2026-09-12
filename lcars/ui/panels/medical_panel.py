"""
LCARS MEDICAL PANEL - SICKBAY OPERATIONS
SYSTEM MODULE: UI-MED-25
PROTOCOL: BIO-SCAN / NEURAL DIAGNOSTIC
DESCRIPTION: Primary medical and biological scanning interface.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QProgressBar
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme

class MedicalPanel(QWidget):
    """
    Медична панель для моніторингу життєвих показників та стану лазарету.
    КРОК 1: Ініціалізація біо-сканерів та медичних баз даних.
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

        # --- LEFT: SICKBAY CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][5])
        elbow.setFixedSize(180, 60)
        left_ctrl.addWidget(elbow)

        lbl_med = QLabel("◢ MEDICAL OPS")
        lbl_med.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_med)

        # Medical services
        services = ["BIO SCAN", "NEURAL SCAN", "SICKBAY STATUS", "MED DATABASE", "EMERGENCY"]
        for i, svc in enumerate(services):
            btn = LCARSButton(svc, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setFixedHeight(40)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()

        # Alert level
        btn_alert = LCARSButton("MEDICAL ALERT", "#CC0000", shape="left")
        btn_alert.setFixedHeight(50)
        left_ctrl.addWidget(btn_alert)

        layout.addLayout(left_ctrl)

        # --- CENTER: BIO SCAN MONITOR ---
        center_area = QVBoxLayout()
        
        head = LCARSContour(color=self.theme['palette'][6], height=30)
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("◢ BIO-SCAN MONITOR // PATIENT STATUS")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Patient status display
        self.patient_box = QFrame()
        self.patient_box.setStyleSheet(f"border: 2px solid {self.theme['palette'][7]}; background: #051005;")
        p_lay = QVBoxLayout(self.patient_box)
        
        lbl_name = QLabel("◤ CREW MEMBER: LT. COMMANDER DATA")
        lbl_name.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}")
        p_lay.addWidget(lbl_name)
        
        vital_signs = [
            ("HEART RATE", 0, 120, 72),
            ("BLOOD PRESSURE", 0, 200, 120),
            ("OXYGEN LEVEL", 0, 100, 98),
            ("NEURAL ACTIVITY", 0, 100, 45)
        ]
        
        self.bars = {}
        for sign, min_v, max_v, val in vital_signs:
            sl = QLabel(f"◤ {sign}")
            sl.setStyleSheet(f"color: #66FF66; {get_lcars_font_style(12, 'normal')}")
            p_lay.addWidget(sl)
            
            pb = QProgressBar()
            pb.setRange(min_v, max_v)
            pb.setValue(val)
            pb.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid #444; border-radius: 5px; text-align: center; color: black; }}
                QProgressBar::chunk {{ background-color: #00FF00; }}
            """)
            p_lay.addWidget(pb)
            self.bars[sign] = pb

        center_area.addWidget(self.patient_box, 1)

        layout.addLayout(center_area, 1)

        # --- RIGHT: DIAGNOSTIC STATUS ---
        right_panel = QVBoxLayout()
        right_panel.setFixedWidth(200)

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        elbow_r.setFixedSize(180, 60)
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ MED SYSTEMS")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("TRICORDER", "NOMINAL", "#00FF00"),
            ("BIO-BEDS", "3/10 ACTIVE", "#FFCC00"),
            ("STASIS", "READY", "#66CCFF"),
            ("DRUGS", "SUFFICIENT", "#66CCFF")
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

        # Pulse timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._vitals_pulse)
        self.timer.start(1000)

    def _vitals_pulse(self):
        """Імітація пульсації життєвих показників."""
        for sign, pb in self.bars.items():
            delta = random.randint(-2, 2)
            pb.setValue(pb.value() + delta)
