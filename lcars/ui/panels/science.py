# Titanium Bridge Migration: import sys, random, math
# Наукова станція LCARS — астрометрія, квантова аналітика, запуск трикордера
import lcars.base.interface as UI
from lcars.modules.ui_manager import LCARSProgramPanel

from lcars.base.type import Matrix, Chassis, Directive, Lore, Primitives
from lcars.base.default import TitanPalette, SetupFont, RandomButtonColor

# ── 4. ASTROMETRIC MAP (VECTOR HUB) ──────────────────────────

class AstrometricMap(Matrix):
    def __init__(self, color, parent=None):
        super().__init__(parent); self.color = color; self.stars = []
        for _ in range(50): self.stars.append((random.randint(20, 780), random.randint(20, 380), random.uniform(1, 3)))
        self.pulse = 0; self.timer = Lore.Pulser(self); self.timer.timeout.connect(self._tick); self.timer.start(100)
    def _tick(self): self.pulse += 0.05; self.update()
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing); p.fillRect(self.rect(), Primitives.Color(0,0,0,255))
        p.setPen(Primitives.Pen(Primitives.Color(self.color + "44"), 1))
        for x in range(0, 800, 100): p.drawLine(x, 0, x, 400)
        for y in range(0, 400, 100): p.drawLine(0, y, 800, y)
        for x, y, size in self.stars:
            op = int(150 + 100 * math.sin(self.pulse + x)); p.setBrush(Primitives.Brush(Primitives.Color(255, 255, 255, op))); p.setPen(Primitives.Pen(Primitives.Color(0,0,0,0))); p.drawEllipse(Primitives.RectF(x, y, size, size))
        p.setPen(Primitives.Pen(Primitives.Color(TitanPalette.Scientific[0] + "88"), 2))

        if len(self.stars) > 5:
            for i in range(4): p.drawLine(int(self.stars[i][0]), int(self.stars[i][1]), int(self.stars[i+1][0]), int(self.stars[i+1][1]))
        p.end()

# ── 5. QUANTUM WAVEFORM ─────────────────────────────────────

class QuantumVisualizer(Matrix):
    def __init__(self, color, parent=None):
        super().__init__(parent); self.color = color; self.phase = 0
        self.timer = Lore.Pulser(self); self.timer.timeout.connect(self._tick); self.timer.start(50)
    def _tick(self): self.phase += 0.2; self.update()
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing); w, h = self.width(), self.height()
        p.setPen(Primitives.Pen(Primitives.Color(self.color), 3))
        path = Primitives.Path(); path.moveTo(0, h/2)
        for x in range(0, w, 5):
            y = h/2 + math.sin(self.phase + x/50) * 40 * math.cos(self.phase*0.3); path.lineTo(x, y)
        p.drawPath(path); p.end()

# ── 6. HQBACKBONE (ALGORITHMIC) ──────────────────────────────

class HQBackbone(Matrix):
    def __init__(self, color, parent=None):
        super().__init__(parent); self.setFixedWidth(260); self.color = color
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing)
        w, h = self.width(), self.height(); th, r = 55, 100
        p.setBrush(Primitives.Brush(Primitives.Color(self.color))); p.setPen(Primitives.Pen(Primitives.Color(0,0,0,0)))
        path = Primitives.Path(); path.moveTo(0, 40); path.lineTo(w-r, 40); path.arcTo(Primitives.RectF(w-r*2, 40, r*2, r*2), 90, -90); path.lineTo(w, h-40-r); path.arcTo(Primitives.RectF(w-r*2, h-40-r*2, r*2, r*2), 0, -90); path.lineTo(0, h-40); path.lineTo(0, h-40-th); path.lineTo(w-r, h-40-th); path.arcTo(Primitives.RectF(w-r-th, h-40-th-(r-th)*2, (r-th)*2, (r-th)*2), 270, 90); path.lineTo(w-th, 40+r); path.arcTo(Primitives.RectF(w-r-th, 40+th, (r-th)*2, (r-th)*2), 0, 90); path.lineTo(0, 40+th); path.closeSubpath()
        p.drawPath(path); p.end()

# ── 7. SCIENCE PANEL (V31.0 ALGORITHMIC) ─────────────────────

class SciencePanel(LCARSProgramPanel):
    def __init__(self, *args, **kwargs):
        SetupFont()
        self.AllCycleButtons = []
        # Акцентний колір панелі — науковий (синьо-блакитний)
        kwargs.setdefault('accent_color', TitanPalette.Scientific[0])
        super().__init__(title="LCARS SCIENCE & ASTROMETRICS", *args, **kwargs)

    def build_ui(self, layout):
        self.setStyleSheet(f"background: {TitanPalette.Background};")

        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        
        # HEADER
        self.cap = UI.Pill(side="none", color=self.accent_color); self.cap.setFixedHeight(65)
        cl = Chassis.Horizontal(self.cap); cl.setContentsMargins(50,0,50,0)
        cl.addWidget(UI.Label("SCIENCE STATION // ASTROMETRICS // QUANTUM CORE v31.0", size=26, color="black"))

        cl.addStretch(); layout.addWidget(self.cap)

        # Таймер циклічної зміни кольорів усіх кнопок (кожні 9 секунд)
        self.ColorTimer = Lore.Pulser(self)
        self.ColorTimer.timeout.connect(self._CycleAllColors)
        self.ColorTimer.start(9000)
        
        # MAIN
        self.ws = Matrix(); wl = Chassis.Horizontal(self.ws); wl.setSpacing(10)
        
        # PILLAR 1: ASTRO DATA
        self.p1 = Matrix(); self.p1.setFixedWidth(360)
        p1l = Chassis.Vertical(self.p1); p1l.setSpacing(4); p1l.setContentsMargins(10, 30, 0, 0)
        p1l.addWidget(UI.Label("◤ ASTROMETRIC LOG", size=11, color="#666666"))
        
        progs = ["SUBSPACE_SCAN", "STELLAR_CARTOGRAPHY", "QUANTUM_SIM", "BIO_SCAN", "PLANETARY_INDEX", "VOID_ANALYSIS", "NEBULA_FLUX"]
        for txt in progs:
            r = Chassis.Horizontal(); r.setSpacing(3)
            num = UI.Label(str(random.randint(1000, 9999)), size=14, color=TitanPalette.Buttons[0]); num.setFixedWidth(55)
            btn = UI.Button(txt, side="left", color=RandomButtonColor()); btn.setFixedHeight(34)
            btn.clicked.connect(lambda t=txt: self._handle_nav(t))
            self.AllCycleButtons.append(btn)
            r.addWidget(num); r.addWidget(btn); p1l.addLayout(r)
        
        p1l.addStretch()
        self.log_box = Matrix(); self.log_box.setFixedHeight(220); self.log_box.setStyleSheet(f"border-left: 6px solid {self.accent_color}; background: #051010; padding: 12px;")
        ll = Chassis.Vertical(self.log_box); self.log_txt = UI.Label(">>> SENSORS: ACTIVE.\n>>> SUBSPACE: NOMINAL.", size=10, color="#88FFAA")
        ll.addWidget(self.log_txt); p1l.addWidget(self.log_box); wl.addWidget(self.p1)
        
        # PILLAR 2: FLOW (ALGORITHMIC COLOR)
        self.flow = HQBackbone(color=self.accent_color); wl.addWidget(self.flow)
        
        # HUB: SCIENTIFIC VISUALIZER
        self.hub = Matrix(); hl = Chassis.Vertical(self.hub); hl.setSpacing(15); hl.setAlignment(Directive.Align.AlignCenter)
        hl.addWidget(UI.Label("SCIENCE DATA ACQUISITION & ANALYSIS", size=18, color=self.accent_color))
        
        self.stack = Chassis.Stack()
        self.stack.setFixedSize(850, 420); self.stack.setStyleSheet(f"border: 4px solid {TitanPalette.Buttons[0]}; border-radius: 80px; background: black; padding: 20px;")

        
        self.map = AstrometricMap(color=TitanPalette.Buttons[0]); self.stack.addWidget(self.map)
        self.quantum = QuantumVisualizer(color=TitanPalette.Buttons[0]); self.stack.addWidget(self.quantum)

        
        hl.addWidget(self.stack)
        hl.addWidget(UI.Label("TITANIUM ASTROMETRICS // SECTOR 001", size=32, color=TitanPalette.Buttons[0]))


        self.st_lbl = UI.Label("SCANNING STANDBY // RESOLUTION: 0.02pc", size=14, color="#AAAAAA")
        hl.addWidget(self.st_lbl); wl.addWidget(self.hub, 1)
        
        # PILLAR 4: COMMAND
        self.p4 = Matrix(); self.p4.setFixedWidth(320)
        p4l = Chassis.Vertical(self.p4); p4l.setSpacing(8); p4l.setContentsMargins(0, 100, 10, 0)
        p4l.addWidget(UI.Label("◢ SCIENCE COMMAND", size=11, color="#666666"))
        
        for name in ["EXECUTE_SIM", "INIT_CARTOGRAPHY", "SUBSPACE_BRIDGE", "SENSOR_RESET"]:
            btn = UI.Button(name, side="right", color=RandomButtonColor()); btn.setFixedHeight(50)
            btn.clicked.connect(lambda n=name: self._handle_cmd(n))
            self.AllCycleButtons.append(btn)
            p4l.addWidget(btn)

        # TR-590 TRICORDER LAUNCH BUTTON
        p4l.addSpacing(12)
        p4l.addWidget(UI.Label("\u25e2 SCIENTIFIC INSTRUMENTS", size=11, color="#666666"))
        btn_tric = UI.Button("TR-590 TRICORDER", side="right", color=TitanPalette.Buttons[3])
        btn_tric.setFixedHeight(56)
        btn_tric.clicked.connect(self._launch_tricorder)
        p4l.addWidget(btn_tric)
        
        p4l.addStretch()
        mb = Matrix(); mb.setFixedHeight(220); mb.setStyleSheet(f"border-right: 6px solid {TitanPalette.Buttons[0]}; background: #051010; padding: 15px;")
        mbl = Chassis.Vertical(mb); mbl.setSpacing(10); mbl.addWidget(UI.Label("◢ QUANTUM STATUS", size=10, color=self.accent_color))
        self.q_lbl = UI.Label("STATE: COHERENT\nPHASE: 0.024\nNODES: 1024", size=10, color=TitanPalette.Buttons[0])

        mbl.addWidget(self.q_lbl); p4l.addWidget(mb); wl.addWidget(self.p4); layout.addWidget(self.ws, 1)
        
        # FOOTER
        self.footer = UI.Pill(side="none", color="#111111"); self.footer.setFixedHeight(45)
        fl = Chassis.Horizontal(self.footer); fl.setContentsMargins(40,0,40,0)
        fl.addWidget(UI.Label("SCIENCE CORP // ASTROMETRIC DATA NOMINAL", size=11, color="#555555"))
        fl.addStretch(); btn_p = UI.Button("PWR", side="both", color=TitanPalette.Alert[1]); btn_p.setFixedSize(120, 36); btn_p.clicked.connect(sys.exit); fl.addWidget(btn_p)

        layout.addWidget(self.footer)

    def _log(self, msg):
        msgs = self.log_txt.text().split("\n")[-7:]; msgs.append(">>> " + str(msg).upper()); self.log_txt.setText("\n".join(msgs))

    def _CycleAllColors(self):
        # Змінити колір усіх кнопок і перемалювати
        for BtnNode in self.AllCycleButtons:
            BtnNode.ActiveColorNode = RandomButtonColor()
            BtnNode.ApplyTitaniumStyles()

    def _handle_nav(self, name):
        name = str(name).upper(); self._log(f"INITIATING: {name}")
        if "QUANTUM" in name: self.stack.setCurrentIndex(1); self.st_lbl.setText("QUANTUM CORE: ACTIVE")
        elif "CARTOGRAPHY" in name or "SCAN" in name: self.stack.setCurrentIndex(0); self.st_lbl.setText("ASTROMETRICS: ACTIVE")

    def _handle_cmd(self, name):
        name = str(name).upper(); self._log(f"CMD: {name}")
        if "SIM" in name:
            # Запустити квантову симуляцію — перейти на квантовий візуалізатор
            self.stack.setCurrentIndex(1)
            self.st_lbl.setText("QUANTUM SIM: RUNNING")
            self.q_lbl.setText("STATE: ENTANGLED\nPHASE: 0.999\nNODES: 32768")
            self._log("BELL STATE SIM ACTIVE")
        elif "CARTOGRAPHY" in name:
            # Запустити картографію — перейти на астрометричну карту
            self.stack.setCurrentIndex(0)
            self.st_lbl.setText("STELLAR CARTOGRAPHY: ACTIVE")
            self._log("CARTOGRAPHY INIT OK")
        elif "BRIDGE" in name:
            # Підпростір — показати астрокарту з повідомленням
            self.stack.setCurrentIndex(0)
            self.st_lbl.setText("SUBSPACE BRIDGE: ESTABLISHED")
            self._log("SUBSPACE FREQ: 4.0 GHz")
        elif "RESET" in name:
            # Скинути статус сенсорів до початкового стану
            self.stack.setCurrentIndex(0)
            self.st_lbl.setText("SCANNING STANDBY // RESOLUTION: 0.02pc")
            self.q_lbl.setText("STATE: COHERENT\nPHASE: 0.024\nNODES: 1024")
            self._log("SENSORS RESET OK")

    def _launch_tricorder(self):
        from programs.science.tricorder import TricorderWindow
        if not hasattr(self, '_TricorderRef') or self._TricorderRef is None:
            self._TricorderRef = TricorderWindow()
        self._TricorderRef.show()
        self._TricorderRef.raise_()

if __name__ == '__main__':
    from lcars.base.type import Application
    app = Application.instance() or Application(sys.argv)
    panel = SciencePanel(); panel.showFullScreen(); sys.exit(app.exec())
