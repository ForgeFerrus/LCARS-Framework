# LCARS Onboard Computer Interface - Canonical Titanium Module (v25.0)
# ─────────────────────────────────────────────────────────────────────────────
# Titanium Bridge Migration: import sys, random
from lcars.base.types import (
    Visual, Lore, Chassis, Directive, Matrix, Application, LCARS
)
from lcars.base.defaults import get_lcars_font_style, get_theme, TitanPalette
from lcars.core.board_computer import BoardComputer

class SystemStatusPanel(Matrix):
    """Панель статусу систем (Тривога, Сканування, Метрики)."""
    def __init__(self, parent=None, era=None):
        super().__init__(parent)
        self.era = era
        self.computer = BoardComputer()
        self.alert_btns = {}
        self.bars = {}
        self.init_ui()

        # Підписка на події тривоги
        from lcars.system.alert import get_alert_system
        self.alert_system = get_alert_system(self.computer.event_bus)
        self.alert_system.alert_changed.connect(self.update_alert_visuals)

        self.timer = Directive.Timer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

        # Автоматичний запуск NovaInitializer (без try/except)
        from lcars.engineering.nova_act import NovaInitializer
        self._nova_initializer = NovaInitializer()
        self._nova_initializer.start()

    def init_ui(self):
        layout = Lore.ODN_Axial(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(8)

        # Рівні тривоги
        alert_layout = Lore.ODN_Lateral()
        alert_layout.setSpacing(4)
        
        from lcars.system.alert import AlertLevel
        alerts = [
            ("RED", TitanPalette.RED_ALERT, AlertLevel.RED),
            ("YEL", TitanPalette.YELLOW_STD, AlertLevel.YELLOW),
            ("NORM", TitanPalette.BLUE_MED, AlertLevel.GREEN),
        ]

        for text, color, level in alerts:
            btn = Visual.Button(text, color, era=self.era, shape="rect", checkable=True)
            btn.setMinimumSize(60, 30)
            btn.clicked.connect(lambda checked, l=level: self.set_alert(l))
            alert_layout.addWidget(btn)
            self.alert_btns[level] = btn
            
        layout.addLayout(alert_layout)
        
        # Сканування
        scan_row = Lore.ODN_Lateral()
        self.scan_btn = Visual.Button("INIT SCAN", TitanPalette.BLUE_LIGHT, era=self.era, shape="pill")
        self.scan_btn.setMinimumHeight(30)
        self.scan_btn.clicked.connect(self.run_scan)

        self.nova_act_btn = Visual.Button("NOVA ACT", TitanPalette.BLUE_MED, era=self.era, shape="rect")
        self.nova_act_btn.setMinimumHeight(30)
        self.nova_act_btn.clicked.connect(self._open_nova_act_panel)
        
        self.scanning_bar = Visual.Scanner("SYSTEM SCAN")
        self.scanning_bar.setMinimumHeight(30)
        
        scan_row.addWidget(self.scan_btn)
        scan_row.addWidget(self.nova_act_btn)
        layout.addLayout(scan_row)

        # Метрики
        metrics = [("CPU_LOAD", TitanPalette.BLUE_LIGHT), ("MEM", TitanPalette.YELLOW_STD), ("NEU", "#CC66FF")]
        for m, color in metrics:
            stat_bar = Visual.Progress(m, color, parent=self)
            stat_bar.setMinimumHeight(25)
            layout.addWidget(stat_bar)
            self.bars[m] = stat_bar

    def set_alert(self, level):
        self.alert_system.set_level(level)
        self.update_alert_visuals(level)

    def update_alert_visuals(self, active_level):
        for level, btn in self.alert_btns.items():
            btn.setChecked(level == active_level)

    def run_scan(self):
        self.scanning_bar.set_text("SCANNING...")
        Directive.Timer.singleShot(2000, self.scan_complete)
        
    def scan_complete(self):
        self.scanning_bar.set_text("SCAN COMPLETE")
        Directive.Timer.singleShot(1500, lambda: self.scanning_bar.set_text("SYSTEM SCAN"))

    def _open_nova_act_panel(self):
        # Запуск Nova Act як окремого застосунку через батник
        # Titanium Bridge Migration: import subprocess, os
        bat_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../start_nova_act.bat'))
        subprocess.Popen([bat_path], shell=True)
        print('◤ NOVA ACT LAUNCHED')

    def update_metrics(self):
        for bar in self.bars.values():
            val = max(5, min(100, bar.value() + random.randint(-5, 5)))
            bar.setValue(val)

class AIConfigPanel(Matrix):
    """Панель вибору провайдера AI."""
    def __init__(self, parent=None, era=None):
        super().__init__(parent)
        self.era = era
        self.computer = BoardComputer()
        self.init_ui()
        
    def init_ui(self):
        layout = Lore.ODN_Axial(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        prov_header = Visual.Label("◤ AI_PROVIDER")
        prov_header.setStyleSheet(f"color: {TitanPalette.ORANGE_STD}; {get_lcars_font_style(10)}")
        layout.addWidget(prov_header)

        self.scroll_area = Visual.Scroll()
        self.scroll_area.setMinimumHeight(100)
        
        self.mod_container = Matrix()
        self.mod_grid = Chassis.Grid(self.mod_container)
        self.scroll_area.setWidget(self.mod_container)
        layout.addWidget(self.scroll_area)

        self.apply_btn = Visual.Button("INIT AI CORE", TitanPalette.BLUE_MED, era=self.era, shape="pill")
        self.apply_btn.clicked.connect(self.apply_config)
        layout.addWidget(self.apply_btn)

    def apply_config(self):
        # Apply logic
        pass

class IntelligenceArray:
    def __init__(self, name, description, color):
        self.name = name
        self.description = description
        self.color = color or TitanPalette.BLUE_LIGHT

class AgentStub:
    def __init__(self, name): self.name = name
    def ask(self, q, cb): cb(f"Response to '{q}' (STUB)")

class OnboardComputerDrawer(Matrix):
    """Головна панель Бортового Комп'ютера."""
    def __init__(self, parent=None, era=None, width=420, mode="embedded"):
        super().__init__(parent)
        self.era = era
        self._drawer_width = width
        self.mode = mode
        
        self.arrays = {
            "MAJEL": IntelligenceArray("MAJEL CORE", "Central System Hub", TitanPalette.ORANGE_STD),
            "M-5": IntelligenceArray("M-5 MULTITRONIC", "Arch Logic", TitanPalette.BLUE_MED),
        }
        self.active_array = self.arrays["MAJEL"]
        self.computer = BoardComputer()
        self.agent = getattr(self.computer, 'agent', None) or AgentStub("CORE-STUB")

        self.setWindowFlags(Directive.Protocol.WindowType.Widget)
        self.setMaximumWidth(0)
        self._build_ui()

    def _build_ui(self):
        layout = Lore.ODN_Axial(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = Matrix()
        h_lay = Lore.ODN_Lateral(header)
        
        elbow = Visual.Elbow("top-left", color=self.active_array.color, era=self.era)
        h_lay.addWidget(elbow)
        
        title = Visual.Label(f"◤ {self.active_array.name}")
        title.setStyleSheet(f"color: {self.active_array.color}; {get_lcars_font_style(18)}")
        h_lay.addWidget(title, 1)
        
        close = Visual.Button("CLOSE", self.active_array.color, shape="rect")
        close.clicked.connect(self.hide_drawer)
        h_lay.addWidget(close)
        
        layout.addWidget(header)

        # Content
        content = Lore.ODN_Lateral()
        content.setContentsMargins(10, 10, 10, 10)
        
        internal_bar = Visual.Contour(color=self.active_array.color, direction="vertical")
        content.addWidget(internal_bar)
        
        body = Lore.ODN_Axial()
        body.addWidget(SystemStatusPanel(era=self.era))
        body.addWidget(AIConfigPanel(era=self.era))
        
        self.response_area = Visual.Input()
        self.response_area.setReadOnly(True)
        body.addWidget(self.response_area, 1)
        
        input_container = Matrix()
        input_container.setStyleSheet(f"border-top: 2px solid {self.active_array.color};")
        i_lay = Lore.ODN_Lateral(input_container)
        
        self.input_field = Visual.Input()
        self.input_field.returnPressed.connect(self.send_query)
        i_lay.addWidget(self.input_field, 1)
        
        send = Visual.Button("EXEC", self.active_array.color, shape="rect")
        send.clicked.connect(self.send_query)
        i_lay.addWidget(send)
        
        body.addWidget(input_container)
        content.addLayout(body, 1)
        layout.addLayout(content, 1)

    def send_query(self):
        text = self.input_field.text().strip()
        if text:
            self.response_area.append(f"[USER]: {text}")
            self.input_field.clear()
            self.agent.ask(text, lambda r: self.response_area.append(f"[{self.active_array.name}]: {r}"))

    def show_drawer(self): self._animate_width(0, self._drawer_width)
    def hide_drawer(self): self._animate_width(self.width(), 0)

    def _animate_width(self, start, end):
        self._anim = Directive.Animation(self, b"maximumWidth")
        self._anim.setDuration(300)
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.setEasingCurve(Directive.Protocol.Easing.Type.OutCubic)
        self._anim.start()

class OnboardStandalone(Chassis.Frame):
    def __init__(self, system=None):
        super().__init__()
        self.setWindowTitle("LCARS :: MAJEL CORE")
        self.setWindowFlags(Directive.Protocol.WindowType.Window)
        
        central = Matrix()
        self.setCentralWidget(central)
        layout = Lore.ODN_Axial(central)
        
        self.onboard = OnboardComputerDrawer(parent=self)
        self.onboard.show_drawer()
        layout.addWidget(self.onboard)

def main():
    app = Application(sys.argv)
    view = OnboardStandalone()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
