"""
LCARS MEDICAL PANEL - SICKBAY OPERATIONS
SYSTEM MODULE: UI-MED-25
PROTOCOL: BIO-SCAN / NEURAL DIAGNOSTIC
DESCRIPTION: Primary medical and biological scanning interface.
"""

import random

from lcars.base.interface import Segment
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar
from lcars.base.default import Palette
from lcars.base.type import LCARS

class MedicalPanel(Segment):
    """
    Медична панель для моніторингу життєвих показників та стану лазарету.
    КРОК 1: Ініціалізація біо-сканерів та медичних баз даних.
    """
    def __init__(self, system=None, DesktopNodeRef=None, ParentNode=None, era=None, faction=None):
        super().__init__(Parent=ParentNode)
        self.system = system
        self.DesktopNode = DesktopNodeRef
        self.era = era
        self.faction = faction
        
        self.widget.setStyleSheet("background-color: black;")
        self.Build()

    def Build(self):
        layout = self.Vertical(0, 0, 0, 0, 0)
        
        # --- TITAN MEDICAL HEADER ---
        header_frame = Segment(Parent=self.widget)
        header_frame.widget.setMinimumHeight(120)
        header_lay = header_frame.Horizontal(0, 5, 20, 0, 20)
        
        self.header_elbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[1], Parent=header_frame.widget)
        self.header_elbow.widget.setMinimumSize(320, 120)
        header_lay.addWidget(self.header_elbow.widget)
        
        title_block = Segment(Parent=header_frame.widget)
        title_lay = title_block.Vertical(0, 0, 0, 0, 5)
        
        self.title_lbl = LCARSLabel("SICKBAY OPERATIONS // PRIMARY BIO-LINK", Color=Palette.Buttons[0], FontSize=32, Parent=title_block.widget)
        title_lay.addWidget(self.title_lbl.widget)
        
        self.status_lbl = LCARSLabel("SCANNER: ACTIVE // NEURAL LINK: STABLE", Color=Palette.Buttons[2], FontSize=18, Parent=title_block.widget)
        title_lay.addWidget(self.status_lbl.widget)
        
        header_lay.addWidget(title_block.widget, 1)
        
        header_bar = LCARSBar(Type="rect", Color=Palette.Buttons[3], Parent=header_frame.widget)
        header_lay.addWidget(header_bar.widget, 1)
        
        layout.addWidget(header_frame.widget)
        
        # --- MAIN ARCHITECTURAL CONTENT ---
        body = Segment(Parent=self.widget)
        body_hbox = body.Horizontal(15, 10, 15, 15, 25)
        
        # LEFT: MEDICAL CONTROLS
        left_col = Segment(Parent=body.widget)
        left_lay = left_col.Vertical(0, 0, 0, 0, 8)
        
        services = ["BIO SCAN", "NEURAL SCAN", "SICKBAY OPS", "MED DB", "EMERGENCY"]
        for i, svc in enumerate(services):
            col = Palette.Buttons[i % len(Palette.Buttons)] if svc != "EMERGENCY" else "#CC3333"
            btn = LCARSButton(svc, Type="rect", Color=col, Width=200, Height=45, Parent=left_col.widget)
            left_lay.addWidget(btn.widget)
            
        left_bar = LCARSBar(Type="rect", Color=Palette.Buttons[1], Parent=left_col.widget)
        left_lay.addWidget(left_bar.widget, 1)
        
        self.left_elbow_bot = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[0], Parent=left_col.widget)
        self.left_elbow_bot.widget.setMinimumHeight(120)
        left_lay.addWidget(self.left_elbow_bot.widget)
        
        body_hbox.addWidget(left_col.widget)
        
        # CENTER: BIO MONITOR
        center_col = Segment(Parent=body.widget)
        center_lay = center_col.Vertical(0, 0, 0, 0, 15)
        
        self.patient_box = Segment(Parent=center_col.widget)
        self.patient_box.widget.setStyleSheet("background: #050505; border: 1px solid #222; border-radius: 8px;")
        p_lay = self.patient_box.Vertical(20, 20, 20, 20, 15)
        
        lbl_name = LCARSLabel("◤ CREW MEMBER: LT. COMMANDER DATA", Color=Palette.Buttons[0], FontSize=20, Parent=self.patient_box.widget)
        p_lay.addWidget(lbl_name.widget)
        
        vital_signs = [
            ("HEART RATE", 0, 120, 72),
            ("BLOOD PRESSURE", 0, 200, 120),
            ("OXYGEN LEVEL", 0, 100, 98),
            ("NEURAL ACTIVITY", 0, 100, 45)
        ]
        
        self.bars = {}
        for sign, min_v, max_v, val in vital_signs:
            sl = LCARSLabel(f"◤ {sign}", Color=Palette.Buttons[2], FontSize=12, Parent=self.patient_box.widget)
            p_lay.addWidget(sl.widget)
            
            pb = LCARS.Interface.Progress()
            pb.setRange(min_v, max_v)
            pb.setValue(val)
            pb.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid #333; height: 12px; border-radius: 6px; text-align: center; color: transparent; background: #111; }}
                QProgressBar::chunk {{ background-color: {Palette.Buttons[1]}; border-radius: 5px; }}
            """)
            p_lay.addWidget(pb)
            self.bars[sign] = pb

        center_lay.addWidget(self.patient_box.widget, 1)
        body_hbox.addWidget(center_col.widget, 2)
        
        # RIGHT: MED SYSTEMS
        right_panel = Segment(Parent=body.widget)
        right_lay = right_panel.Vertical(0, 0, 0, 0, 10)
        
        lbl_stat = LCARSLabel("◤ MED SYSTEMS", Color=Palette.Buttons[2], FontSize=16, Parent=right_panel.widget)
        right_lay.addWidget(lbl_stat.widget)
        
        stats = [
            ("TRICORDER", "NOMINAL"),
            ("BIO-BEDS", "ACTIVE"),
            ("STASIS", "READY"),
            ("MEDICAL LOG", "VERIFIED")
        ]
        for title, val in stats:
            box = Segment(Parent=right_panel.widget)
            box.widget.setStyleSheet(f"border-left: 6px solid {Palette.Buttons[1]}; padding-left: 10px; background: rgba(255,153,0,0.05);")
            bl = box.Vertical(5, 5, 5, 5, 5)
            
            tl = LCARSLabel(title, Color="#FFFFFF", FontSize=10, Parent=box.widget)
            vl = LCARSLabel(val, Color=Palette.Buttons[1], FontSize=14, Parent=box.widget)
            
            bl.addWidget(tl.widget)
            bl.addWidget(vl.widget)
            right_lay.addWidget(box.widget)
            
        right_bar = LCARSBar(Type="rect", Color=Palette.Buttons[3], Parent=right_panel.widget)
        right_lay.addWidget(right_bar.widget, 1)
        
        body_hbox.addWidget(right_panel.widget)
        layout.addWidget(body.widget, 1)

        # Pulse timer
        self.timer = LCARS.Base.Timer(self.widget)
        self.timer.timeout.connect(self.VitalsPulse)
        self.timer.start(1000)

    def VitalsPulse(self):
        """Імітація пульсації життєвих показників."""
        for sign, pb in self.bars.items():
            delta = random.randint(-2, 2)
            pb.setValue(pb.value() + delta)

