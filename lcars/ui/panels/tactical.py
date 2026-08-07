import sys, random, os, math, subprocess
# 1. СИСТЕМНА ІНІЦІАЛІЗАЦІЯ (TACTICAL OPERATION v31.1)
from lcars.base.register import registry
import lcars.base.interface as UI
from lcars.base.interface import LCARSProgramPanel

from lcars.base.type import Matrix, Chassis, Directive, Lore, Primitives
from lcars.core.signal import Signal
from lcars.base.default import TitanPalette, FontSetup as SetupFont, RandomButtonColor

from lcars.engineering.deflector import DeflectorSystem
from lcars.system.alert import ActiveAlerts, AlertLevel

# ── 4. TACTICAL COMPONENTS (ALGORITHMIC) ─────────────────────

class SectorGrid(Matrix):
    def __init__(self, color, parent=None):
        super().__init__(parent); self.setFixedSize(400, 400); self.color = color
        self.targets = [(random.randint(20, 380), random.randint(20, 380)) for _ in range(3)]
        self.sweep = 0; self.timer = Lore.Pulser(self); self.timer.timeout.connect(self.Tick); self.timer.start(50)
    def Tick(self): self.sweep = (self.sweep + 5) % 400; self.update()
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing)
        p.setPen(Primitives.Pen(Primitives.Color(self.color + "44"), 1))
        for i in range(11): p.drawLine(0, i*40, 400, i*40); p.drawLine(i*40, 0, i*40, 400)
        p.setPen(Primitives.Pen(Primitives.Color(self.color), 2)); p.drawLine(0, self.sweep, 400, self.sweep)
        for tx, ty in self.targets:
            p.setBrush(Primitives.Brush(Primitives.Color(TitanPalette.Alert[1] if abs(ty - self.sweep) < 10 else TitanPalette.Scientific[1])))

            p.drawEllipse(Primitives.Point(tx, ty), 4, 4)
        p.end()

class ShieldArcs(Matrix):
    def __init__(self, color, parent=None):
        super().__init__(parent); self.setFixedSize(300, 300); self.color = color; self.power = 100.0; self.alert = False
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing); c_x, c_y = 150, 150
        col = TitanPalette.Alert[1] if self.alert else self.color

        for i in range(3):
            r = 60 + i*25; p.setPen(Primitives.Pen(Primitives.Color(col + "44"), 4))
            p.drawArc(Primitives.RectF(c_x-r, c_y-r, r*2, r*2), 30 * 16, int(self.power * 3.6 * 16))
        p.setBrush(Primitives.Brush(Primitives.Color(255, 255, 255, 100))); p.setPen(Primitives.Pen(Primitives.Color(0,0,0,0)))
        path = Primitives.Path(); path.addEllipse(Primitives.RectF(c_x-30, c_y-50, 60, 80)); p.drawPath(path); p.end()

class TacticalBackbone(Matrix):
    def __init__(self, color, parent=None):
        super().__init__(parent); self.setFixedWidth(240); self.color = color
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing); w, h = self.width(), self.height(); th, r = 50, 80
        p.setBrush(Primitives.Brush(Primitives.Color(self.color))); p.setPen(Primitives.Pen(Primitives.Color(0,0,0,0)))
        path = Primitives.Path(); path.moveTo(0, 0); path.lineTo(w-r, 0); path.arcTo(Primitives.RectF(w-r*2, 0, r*2, r*2), 90, -90); path.lineTo(w, h-r); path.arcTo(Primitives.RectF(w-r*2, h-r*2, r*2, r*2), 0, -90); path.lineTo(0, h); path.lineTo(0, h-th); path.lineTo(w-th-10, h-th); path.arcTo(Primitives.RectF(w-th-20, h-th-20, 20, 20), 270, 90); path.lineTo(w-th, th+10); path.arcTo(Primitives.RectF(w-th-20, th, 20, 20), 0, 90); path.lineTo(0, th); path.closeSubpath(); p.drawPath(path); p.end()

# ── 5. TACTICAL PANEL (V31.1 ALGORITHMIC) ─────────────────────

class TacticalPanel(LCARSProgramPanel):
    def __init__(self, DesktopNodeRef=None, ParentNode=None, *args, **kwargs):
        self.shields = DeflectorSystem(); self.alert_sys = ActiveAlerts()
        kwargs.setdefault('accent_color', TitanPalette.Scientific[1])
        super().__init__(title="TACTICAL COMMAND", DesktopNodeRef=DesktopNodeRef, ParentNode=ParentNode, *args, **kwargs)
        self.update_timer = Lore.Pulser(self.widget); self.update_timer.timeout.connect(self.Sync); self.update_timer.start(1000)

    def BuildUi(self, layout):
        self.setStyleSheet(f"background: {TitanPalette.Background};")

        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        
        # HEADER
        self.cap = UI.Pill(side="none", color=self.accent_color); self.cap.setFixedHeight(60)
        cl = Chassis.Horizontal(self.cap); cl.setContentsMargins(40,0,40,0)
        cl.addWidget(UI.Label("TACTICAL DEFENSE CONSOLE // v31.1 // ALGORITHMIC", size=24, color="black"))

        cl.addStretch(); layout.addWidget(self.cap.Widget)
        
        # MAIN
        self.ws = Matrix(); wl = Chassis.Horizontal(self.ws); wl.setSpacing(10)
        
        # LEFT PILLAR
        self.p1 = Matrix(); self.p1.setFixedWidth(300)
        p1l = Chassis.Vertical(self.p1); p1l.setSpacing(5); p1l.setContentsMargins(10, 40, 0, 0)
        p1l.addWidget(UI.Label("◤ WEAPON CONTROL", size=11, color="#666666"))
        
        for txt in ["PHASERS", "TORPEDOES", "TARGET LOCK", "COUNTERMEASURES", "ORDNANCE", "AUTO-FIRE"]:
            btn = UI.Button(txt, side="left", color=RandomButtonColor()); btn.setFixedHeight(45)

            btn.clicked.Connect(lambda t=txt: self.HandleWpn(t)); p1l.addWidget(btn)
        p1l.addStretch()
        self.log_box = Matrix(); self.log_box.setFixedHeight(200); self.log_box.setStyleSheet(f"border-left: 6px solid {self.accent_color}; background: #100505; padding: 10px;")
        ll = Chassis.Vertical(self.log_box); self.log_txt = UI.Label(">>> TACTICAL READY.\n>>> AWAITING COMMAND.", size=10, color="#88AAFF")
        ll.addWidget(self.log_txt.Widget); p1l.addWidget(self.log_box.Widget); wl.addWidget(self.p1.Widget)
        
        # CENTER
        self.backbone = TacticalBackbone(color=self.accent_color); wl.addWidget(self.backbone.Widget)
        self.hub = Matrix(); hl = Chassis.Vertical(self.hub); hl.setSpacing(20); hl.setAlignment(Directive.Align.AlignCenter)
        grid_row = Chassis.Horizontal(); grid_row.setSpacing(30)
        self.grid = SectorGrid(color=TitanPalette.Buttons[2]); grid_row.addWidget(self.grid.Widget)
        self.sh_display = ShieldArcs(color=TitanPalette.Buttons[2]); grid_row.addWidget(self.sh_display.Widget)

        hl.addLayout(grid_row)
        hl.addWidget(UI.Label("DEFENSE PERIMETER // SECTOR SCAN", size=18, color=self.accent_color))
        self.st_lbl = UI.Label("SCANNING... ALL SYSTEMS NOMINAL", size=14, color="#AAAAAA")
        hl.addWidget(self.st_lbl.Widget); wl.addWidget(self.hub, 1)
        
        # RIGHT PILLAR
        self.p4 = Matrix(); self.p4.setFixedWidth(300)
        p4l = Chassis.Vertical(self.p4); p4l.setSpacing(8); p4l.setContentsMargins(0, 100, 10, 0)
        p4l.addWidget(UI.Label("◢ DEFENSE CONTROL", size=11, color="#666666"))
        
        for name in ["RED ALERT", "YELLOW ALERT", "SHIELDS UP", "RECHARGE", "SCAN ALL"]:
            btn = UI.Button(name, side="right", color=RandomButtonColor()); btn.setFixedHeight(50)
            btn.clicked.Connect(lambda n=name: self.HandleDef(n)); p4l.addWidget(btn)

        
        p4l.addStretch()
        self.stats = UI.Label("SHIELDS: 100%\nTHREATS: 0", size=12, color=TitanPalette.Buttons[2])
        p4l.addWidget(self.stats.Widget); wl.addWidget(self.p4.Widget); layout.addWidget(self.ws, 1)

        
        # FOOTER
        self.footer = UI.Pill(side="none", color="#111111"); self.footer.setFixedHeight(45)
        fl = Chassis.Horizontal(self.footer); fl.setContentsMargins(40,0,40,0)
        fl.addWidget(UI.Label("NCC-1701-E // SECURITY TERMINAL", size=11, color="#555555"))
        fl.addStretch(); btn_x = UI.Button("EXIT", side="both", color=TitanPalette.Alert[1]); btn_x.setFixedSize(120, 36); btn_x.clicked.Connect(sys.exit); fl.addWidget(btn_x)

        layout.addWidget(self.footer.Widget)

    def Sync(self):
        pwr = self.shields.ShieldLevel; self.sh_display.power = pwr; self.sh_display.update()
        self.stats.setText(f"SHIELDS: {pwr}%\nTHREATS: {self.shields.BlockedThreats}")

    def Log(self, text):
        self.log_txt.setText(f"{self.log_txt.text()}\n>> {text}")

    def HandleWpn(self, name):
        self.Log(f"INITIATING {name}...")

    def HandleDef(self, name):
        if "ALERT" in name:
            lvl = AlertLevel.RED if "RED" in name else AlertLevel.YELLOW
            self.alert_sys.set_level(lvl); self.sh_display.alert = (lvl == AlertLevel.RED)

            color = TitanPalette.Alert[1] if lvl == AlertLevel.RED else self.accent_color

            self.cap.setStyleSheet(f"background: {color}; border-radius: 30px;")
            self.Log(f"{name} ACTIVATED.")
        elif name == "SHIELDS UP":
            self.shields.RaiseShields(100.0, "STRATIFIED")
            self.Log("DEFLECTOR SHIELDS: MAXIMUM YIELD")
            self.sh_display.power = 100
        elif name == "RECHARGE":
            self.shields.RechargeShields()
            self.Log("DEFLECTOR SHIELDS: STANDBY")

if __name__ == '__main__':
    app = registry.get("Technical.Application")(sys.argv)
    panel = TacticalPanel(); panel.showFullScreen(); sys.exit(app.exec())

