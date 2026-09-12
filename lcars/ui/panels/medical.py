"""
LCARS MEDICAL PANEL - SICKBAY OPERATIONS
SYSTEM MODULE: UI-MED-25
PROTOCOL: BIO-SCAN / NEURAL DIAGNOSTIC
DESCRIPTION: Primary medical and biological scanning interface.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QProgressBar
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.base.types import LCARSButton
from lcars.themes.palette import get_lcars_font_style, get_theme

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
        from lcars.base.types import LCARSElbow, LCARSSegment, LCARSButton
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- TITAN MEDICAL HEADER ---
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)
        header_lay = QHBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 5, 20, 0)
        header_lay.setSpacing(20)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        self.header_elbow = LCARSElbow("top-left", palette[1], era=self.era)
        self.header_elbow.setMinimumSize(320, 120)
        header_lay.addWidget(self.header_elbow)
        
        title_lay = QVBoxLayout()
        self.title_lbl = QLabel("SICKBAY OPERATIONS // PRIMARY BIO-LINK")
        self.title_lbl.setStyleSheet(f"color: {palette[0]}; {get_lcars_font_style(32, 'bold')}; letter-spacing: 2px;")
        title_lay.addWidget(self.title_lbl)
        
        self.status_lbl = QLabel("SCANNER: ACTIVE // NEURAL LINK: STABLE")
        self.status_lbl.setStyleSheet(f"color: {palette[2]}; {get_lcars_font_style(18, 'normal')};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)
        
        header_lay.addWidget(LCARSSegment(palette[3], direction="horizontal", era=self.era), 1)
        layout.addWidget(header_frame)
        
        # --- MAIN ARCHITECTURAL CONTENT ---
        body_hbox = QHBoxLayout()
        body_hbox.setContentsMargins(15, 10, 15, 15)
        body_hbox.setSpacing(25)
        
        # LEFT: MEDICAL CONTROLS
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        
        services = ["BIO SCAN", "NEURAL SCAN", "SICKBAY OPS", "MED DB", "EMERGENCY"]
        for i, svc in enumerate(services):
            col = palette[i % len(palette)] if svc != "EMERGENCY" else "#CC3333"
            btn = LCARSButton(svc, col, era=self.era, shape="rect")
            btn.setFixedSize(200, 45)
            left_col.addWidget(btn)
            
        left_col.addWidget(LCARSSegment(palette[1], direction="vertical", era=self.era), 1)
        
        self.left_elbow_bot = LCARSElbow("bottom-left", palette[0], era=self.era)
        self.left_elbow_bot.setMinimumHeight(120)
        left_col.addWidget(self.left_elbow_bot)
        
        body_hbox.addLayout(left_col)
        
        # CENTER: BIO MONITOR
        center_col = QVBoxLayout()
        center_col.setSpacing(15)
        
        self.patient_box = QFrame()
        self.patient_box.setStyleSheet("background: #050505; border: 1px solid #222; border-radius: 8px;")
        p_lay = QVBoxLayout(self.patient_box)
        p_lay.setContentsMargins(20, 20, 20, 20)
        
        lbl_name = QLabel("◤ CREW MEMBER: LT. COMMANDER DATA")
        lbl_name.setStyleSheet(f"color: {palette[0]}; {get_lcars_font_style(20, 'bold')}")
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
            sl.setStyleSheet(f"color: {palette[2]}; {get_lcars_font_style(12, 'normal')}")
            p_lay.addWidget(sl)
            
            pb = QProgressBar()
            pb.setRange(min_v, max_v)
            pb.setValue(val)
            pb.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid #333; height: 12px; border-radius: 6px; text-align: center; color: transparent; background: #111; }}
                QProgressBar::chunk {{ background-color: {palette[1]}; border-radius: 5px; }}
            """)
            p_lay.addWidget(pb)
            self.bars[sign] = pb

        center_col.addWidget(self.patient_box, 1)
        body_hbox.addLayout(center_col, 2)
        
        # RIGHT: MED SYSTEMS
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        lbl_stat = QLabel("◤ MED SYSTEMS")
        lbl_stat.setStyleSheet(f"color: {palette[2]}; {get_lcars_font_style(16, 'bold')}")
        right_panel.addWidget(lbl_stat)
        
        stats = [
            ("TRICORDER", "NOMINAL"),
            ("BIO-BEDS", "ACTIVE"),
            ("STASIS", "READY"),
            ("MEDICAL LOG", "VERIFIED")
        ]
        for title, val in stats:
            box = QFrame()
            box.setStyleSheet(f"border-left: 6px solid {palette[1]}; padding-left: 10px; background: rgba(255,153,0,0.05);")
            bl = QVBoxLayout(box)
            tl = QLabel(title)
            tl.setStyleSheet(f"color: white; {get_lcars_font_style(10, 'normal')}")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {palette[1]}; {get_lcars_font_style(14, 'bold')}")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)
            
        right_panel.addWidget(LCARSSegment(palette[3], era=self.era), 1)
        layout.addLayout(body_hbox, 1)

        # Pulse timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._vitals_pulse)
        self.timer.start(1000)

    def _vitals_pulse(self):
        """Імітація пульсації життєвих показників."""
        for sign, pb in self.bars.items():
            delta = random.randint(-2, 2)
            pb.setValue(pb.value() + delta)
