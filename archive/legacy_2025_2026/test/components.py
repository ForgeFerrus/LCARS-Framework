import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib
from lcars.base.type import LCARS, Type
from lcars.base.interface import StatBar, DataBlock, ScanningBar, Padd
from lcars.base.component import (
    Graphic, Component, LCARSButton, LCARSElbow, LCARSIndicator,
)   
from lcars.base.animation import CreateStarfieldCluster, CreateSegmentBar
from lcars.base.default import DefaultBackground, Palette, RandomButtonColor, FontStyle, ContrastColor, DefaultRadius
from lcars.base.version import getVersion

# ==============================================================================
# ДОПОМІЖНІ ЗБІРКИ (ланцюжки: registry.Interface.*, LCARS.Widget())
# ==============================================================================
def PLayoutSound(name):
    if importlib.util.find_spec("lcars.modules.sound") is None:
        return
    from lcars.modules.sound import GetSoundManager
    sm = GetSoundManager()
    if sm is not None and hasattr(sm, "pLayout"):
        sm.pLayout(name)
Widget = LCARS.Segment

def VerticalLayout(parent=None):
    Cls = LCARS.VMatrix
    if parent is not None:
        parent_widget = parent.widget if hasattr(parent, 'widget') else parent
        return Cls(parent_widget)
    return Cls()

def HorizontalLayout(parent=None):
    Cls = LCARS.HMatrix
    if parent is not None:
        parent_widget = parent.widget if hasattr(parent, 'widget') else parent
        return Cls(parent_widget)
    return Cls()

def CreateTitle(parent, text, color):
    lbl = LCARSIndicator(Text=text, Parent=parent, Color=color)
    lbl.widget.setStyleSheet(
        "color: " + color + "; " + FontStyle(20, "normal") + " background: transparent;"
    )
    return lbl.widget

# ==============================================================================
# ПАНЕЛІ РОБОЧОГО СТОЛУ (лише base)
# ==============================================================================

class BridgePanel:
    def __init__(self, parent=None, system=None, era=None, faction=None):
        self.Widget = Widget(parent)
        self.Widget.setStyleSheet("background-color: " + DefaultBackground + ";")
        Layout = VerticalLayout(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        Layout.setSpacing(8)
        Protocol = LCARS.Protocol
        Layout.addWidget(
            CreateTitle(self.Widget, "◤ BRIDGE — MISSION CONTROL", Palette.Buttons[2]),
            0,
            Protocol.AlignmentFlag.AlignLeft if Protocol else None,
        )
        Layout.addWidget(ScanningBar(Palette.Buttons[2], parent=self.Widget).Widget)
        RowWidget = Widget(self.Widget)
        Row = HorizontalLayout(RowWidget)
        Row.addWidget(DataBlock("STARDATE", "ACTIVE", Palette.Buttons[2], parent=RowWidget).widget)
        Row.addWidget(DataBlock("HULL", "NOMINAL", Palette.Buttons[3], parent=RowWidget).widget)
        Layout.addWidget(RowWidget)
        star = CreateStarfieldCluster(Parent=self.Widget)
        Layout.addWidget(star.widget, 1)

class CommsPanel:
    def __init__(self, parent=None, system=None, era=None, faction=None):
        self.Widget = Widget(parent)
        Layout = VerticalLayout(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        D = LCARS.Protocol
        Layout.addWidget(
            CreateTitle(self.Widget, "◤ COMMS — SUBSPACE LINK", Palette.Buttons[1]),
            0,
            D.AlignmentFlag.AlignLeft if D else None,
        )
        logCls = LCARS.Terminal
        if logCls is not None:
            self.log = logCls(self.Widget)
            self.log.setReadOnly(True)
            self.log.setPlainText(
                "CHANNEL OPEN\nU.S.S. TITAN-A — EPSILON BAND\nSIGNAL: STABLE\nAWAITING TRANSMISSION..."
            )
            self.log.setStyleSheet(
                f"QTextEdit {{ background: #0a0a0a; color: {Palette.Panels[2]}; "
                f"border: 1px solid {Palette.Buttons[8]}; {FontStyle(12, 'normal')} }}"
            )
            Layout.addWidget(self.log, 1)
        else:
            fallback = Label1(Text="COMMS CHANNEL READY", Parent=self.Widget, Color=Palette.Panels[2])
            Layout.addWidget(fallback.widget, 1)


class EnginePanel:
    def __init__(self, parent=None, system=None, era=None, faction=None):
        self.Widget = Widget(parent)
        Layout = VerticalLayout(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        D = LCARS.Protocol
        Layout.addWidget(
            CreateTitle(self.Widget, "◤ ENGINE — WARP CORE", Palette.Buttons[4]),
            0,
            D.AlignmentFlag.AlignLeft if D else None,
        )
        Layout.addWidget(ScanningBar(Palette.Buttons[4], parent=self.Widget).widget)
        stats = [
            ("WARP FIELD", "STABLE"),
            ("EPS FLOW", "104%"),
            ("CORE TEMP", "3700 K"),
            ("PLASMA", "NOMINAL"),
        ]
        for title, val in stats:
            Layout.addWidget(DataBlock(title, val, Palette.Buttons[4], parent=self.Widget).widget)
        Layout.addStretch(1)
        
class ViewHost:
    def __init__(self, parent=None, system=None, *args, **kwargs):
        stack_cls = LCARS.Chamber
        self.stack = stack_cls(parent)
        self.Widget = self.stack
        
        self.bridge = BridgePanel(parent=self.stack)
        self.stack.addWidget(self.bridge.widget)
        
        from lcars.base.constructor import LCARSDesigner
        self.constructor = LCARSDesigner(Parent=self.stack)
        self.stack.addWidget(self.constructor)
            
        self.comms = CommsPanel(parent=self.stack)
        self.stack.addWidget(self.comms.widget)
        
        self.engine = EnginePanel(parent=self.stack)
        self.stack.addWidget(self.engine.widget)
        
        from lcars.ui.views.tri_panel_ide import TriPanelIDE
        self.ide = TriPanelIDE(parent=self.stack)
        self.stack.addWidget(self.ide)

    def ShowIndex(self, index):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

class LCARSConstructor:
    def __init__(self, parent=None, *args, **kwargs):
        from lcars.base.constructor import LCARSDesigner
        self.Widget = LCARSDesigner(Parent=parent)

class RunConstructor:
    def __init__(self, parent=None, *args, **kwargs):
        self.Widget = Widget(parent)

class LCARSIDE:
    def __init__(self, parent=None, *args, **kwargs):
        from lcars.ui.views.tri_panel_ide import TriPanelIDE
        self.Widget = TriPanelIDE(parent=parent)

class DesignerPanel:
    def __init__(self, parent=None, *args, **kwargs):
        from lcars.base.constructor import LCARSDesigner
        self.Widget = LCARSDesigner(Parent=parent)

class ConstructorPanel:
    def __init__(self, parent=None, *args, **kwargs):
        from lcars.base.constructor import LCARSDesigner
        self.Widget = LCARSDesigner(Parent=parent)
# ==============================================================================
# COMPONENT SHOWCASE — Демонстрація ВСІХ компонентів, анімацій та елементів
# ==============================================================================
class ComponentShowcase(Padd):

    PADD_W = 1260
    PADD_H = 820

    def __init__(self, parent=None):
        super().__init__(Title="◤ LCARS FRAMEWORK — COMPONENT SHOWCASE", Parent=parent)
        self.fullscreen = False
        self.setWindowTitle("◤ LCARS FRAMEWORK — COMPONENT SHOWCASE")
        self.resize(self.PADD_W, self.PADD_H)
        self.build()
        PLayoutSound("ready")

    # ── утиліти ──────────────────────────────────────────────────────────────
    def label(self, text, color=None, size=10, parent=None):
        Cls = LCARS.Indicator
        w = Cls(str(text).upper(), parent or self)
        w.setStyleSheet(
            f"color: {color or Palette.Panels[2]}; font-size: {size}pt;"
            " font-family: 'LCARS'; font-weight: bold;"
            " letter-spacing: 1.5px; background: transparent;"
        )
        return w

    def sec(self, text, color=None):
        lbl = self.label("◢  " + text, color or Palette.Panels[2], size=9)
        lbl.setStyleSheet(
            lbl.styleSheet() +
            f" border-bottom: 1px solid {color or Palette.Panels[2]}44;"
            " padding-bottom: 3px; margin-top: 4px;"
        )
        return lbl

    def tabPage(self):
        ScrollCls = LCARS.Buffer
        if ScrollCls:
            scroll = ScrollCls()
            scroll.setStyleSheet(
                "LCARSBuffer { background: transparent; border: none; }"
                "LCARSScrollBar:vertical { background: #0a0a0a; width: 8px; border: none; }"
                "LCARSScrollBar::handle:vertical { background: #223344; border-radius: 4px; }"
                "LCARSScrollBar::add-line:vertical, LCARSScrollBar::sub-line:vertical { height: 0; }"
            )
            scroll.setWidgetResizable(True)
            FrameCls = LCARS.Segment
            inner = FrameCls()
            inner.setStyleSheet("background: transparent;")
            col = VerticalLayout(inner)
            col.setContentsMargins(20, 16, 20, 16)
            col.setSpacing(14)
            scroll.setWidget(inner)
            return scroll, col
        col = VerticalLayout()
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(14)
        return None, col

    # ── збірка ───────────────────────────────────────────────────────────────
    def build(self):
        root = VerticalLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addLayout(self.header())
        root.addWidget(ScanningBar(Palette.Buttons[2], parent=self).Widget)

        # ── вкладки ──────────────────────────────────────────────────────────
        from lcars.base.animation import (
            ScanningBar as ABar, CreateSegmentBar as SegmentBar, StarfieldCluster,
            Pulse, DiagnosticGrid, Blink, Typewriter, TextDecode as ScrambledText,
        )
        TabCls = LCARS.Grid
        if TabCls:
            tabs = TabCls(self)
            tabs.setStyleSheet(
                "LCARSGrid::pane { border: none; background: transparent; }"
                f"LCARSTabBar::tab {{ background: #111; color: {Palette.Buttons[0]};"
                "  font-size: 10pt; font-family: 'LCARS'; font-weight: bold;"
                "  padding: 8px 22px; border: none;"
                f"  border-bottom: 2px solid {Palette.Buttons[0]}44; }}"
                f"LCARSTabBar::tab:selected {{ background: #050515;"
                f"  color: {Palette.Panels[2]}; border-bottom: 2px solid {Palette.Panels[2]}; }}"
                "LCARSTabBar::tab:hover { background: #1a1a2a; }"
            )
            tabs.addTab(self.tabButtons(), "◢  BUTTONS")
            tabs.addTab(self.tabGeometry(), "◢  GEOMETRY")
            tabs.addTab(self.tabAnimations(), "◢  ANIMATIONS")
            tabs.addTab(self.tabData(), "◢  DATA")
            tabs.addTab(self.tabStatus(), "◢  STATUS")
            root.addWidget(tabs, 1)
        else:
            # Якщо Tab недоступний — скролл-лист усього
            _, col = self.tabPage()
            root.addLayout(col, 1)

        from lcars.base.animation import SegmentBar as SBar
        root.addWidget(SBar(Parent=self))
        root.addLayout(self.footer())

    # ── ВКЛАДКА 1: КНОПКИ ────────────────────────────────────────────────────
    def tabButtons(self):
        scroll, col = self.tabPage()

        # Button1 — Button5
        col.addWidget(self.sec("Button1 — Button5  |  canonical color factory", Palette.Buttons[0]))
        r1 = HorizontalLayout()
        r1.setSpacing(6)
        for Factory, label in [
            (Button1, "ALPHA"), (Button2, "BETA"), (Button3, "GAMMA"),
            (Button4, "DELTA"), (Button5, "EPSILON"),
        ]:
            btn = Factory(Text=label, Parent=self)
            btn.setFixedSize(150, 48)
            btn.clicked.connect(lambda _=None: PLayoutSound("acknowledge"))
            r1.addWidget(btn.widget)
        r1.addStretch()
        col.addLayout(r1)

        # LCARSButton — форми
        col.addWidget(self.sec("LCARSButton  |  shape=rect / pill / left / right", Palette.Buttons[1]))
        r2 = HorizontalLayout()
        r2.setSpacing(6)
        for shape, label, color in [
            ("rect",  "RECT",  Palette.Buttons[0]),
            ("pill",  "PILL",  Palette.Buttons[1]),
            ("left",  "LEFT",  Palette.Buttons[2]),
            ("right", "RIGHT", Palette.Buttons[3]),
        ]:
            btn = LCARSButton(text=label, color=color, shape=shape, parent=self)
            btn.setFixedSize(150, 48)
            btn.clicked.connect(lambda _=None: PLayoutSound("acknowledge"))
            r2.addWidget(btn.widget)
        r2.addStretch()
        col.addLayout(r2)

        # Dedicated Shape Subclasses
        col.addWidget(self.sec("Dedicated Shape Subclasses  |  PillButton / RectButton / LeftRoundButton / RightRoundButton", Palette.Buttons[4]))
        r_shapes = HorizontalLayout()
        r_shapes.setSpacing(6)
        for Class, label, color in [
            (RectButton,  "RECT CLASS",  Palette.Buttons[0]),
            (PillButton,  "PILL CLASS",  Palette.Buttons[1]),
            (LeftRoundButton,  "LEFT CLASS",  Palette.Buttons[2]),
            (RightRoundButton, "RIGHT CLASS", Palette.Buttons[3]),
        ]:
            btn = Class(Text=label, Color=color, Parent=self)
            btn.setFixedSize(150, 48)
            btn.clicked.connect(lambda _=None: PLayoutSound("acknowledge"))
            r_shapes.addWidget(btn.widget)
        r_shapes.addStretch()
        col.addLayout(r_shapes)

        # Кольорові варіанти
        col.addWidget(self.sec("LCARSButton  |  all palette colors", Palette.Buttons[2]))
        r3 = HorizontalLayout()
        r3.setSpacing(6)
        for i, color in enumerate(Palette.Buttons):
            btn = LCARSButton(text=f"BTN {i}", color=color, shape="rect", parent=self)
            btn.setFixedSize(110, 48)
            btn.clicked.connect(lambda _=None: PLayoutSound("acknowledge"))
            r3.addWidget(btn.widget)
        r3.addStretch()
        col.addLayout(r3)

        # Alert кольори
        col.addWidget(self.sec("Alert / Warning colors", Palette.RedAlert[0]))
        r4 = HorizontalLayout()
        r4.setSpacing(6)
        for label, color in [
            ("RED ALERT",   Palette.RedAlert[0]),
            ("CRITICAL",    Palette.RedAlert[2]),
            ("YELLOW ALERT",Palette.YellowAlert[0]),
            ("CAUTION",     Palette.YellowAlert[2]),
        ]:
            btn = LCARSButton(text=label, color=color, shape="pill", parent=self)
            btn.setFixedSize(180, 48)
            btn.clicked.connect(lambda _=None: PLayoutSound("acknowledge"))
            r4.addWidget(btn.widget)
        r4.addStretch()
        col.addLayout(r4)

        col.addStretch()
        return scroll if scroll else self.wrapCol(col)

    # ── ВКЛАДКА 2: ГЕОМЕТРІЯ ─────────────────────────────────────────────────
    def tabGeometry(self):
        scroll, col = self.tabPage()

        # Elbows
        col.addWidget(self.sec("LCARSElbow  |  LCARS corner geometry", Palette.Buttons[0]))
        r1 = HorizontalLayout()
        r1.setSpacing(30)
        for direction, color, label in [
            ("top-left",     Palette.Buttons[0], "LCARSElbow\ntop-left"),
            ("top-right",    Palette.Buttons[1], "LCARSElbow\ntop-right"),
            ("bottom-left",  Palette.Buttons[3], "LCARSElbow\nbottom-left"),
            ("bottom-right", Palette.Buttons[4], "LCARSElbow\nbottom-right"),
        ]:
            wrap = VerticalLayout()
            wrap.setSpacing(4)
            el = LCARSElbow(Parent=self, Color=color, Direction=direction)
            el.setFixedSize(140, 85)
            wrap.addWidget(el.widget)
            wrap.addWidget(self.label(label, color, size=8))
            r1.addLayout(wrap)
        r1.addStretch()
        col.addLayout(r1)

        # LCARSElbow — розміри
        col.addWidget(self.sec("LCARSElbow  |  size variants", Palette.Buttons[2]))
        r2 = HorizontalLayout()
        r2.setSpacing(16)
        for w, h in [(80, 50), (120, 70), (160, 90), (200, 110)]:
            wrap = VerticalLayout()
            wrap.setSpacing(4)
            el = LCARSElbow(Parent=self, Color=Palette.Buttons[2], Direction="top-left")
            el.setFixedSize(w, h)
            wrap.addWidget(el.widget)
            wrap.addWidget(self.label(f"{w}×{h}", Palette.Buttons[2], size=8))
            r2.addLayout(wrap)
        r2.addStretch()
        col.addLayout(r2)

        col.addStretch()
        return scroll if scroll else self.wrapCol(col)

    # ── ВКЛАДКА 3: АНІМАЦІЇ ──────────────────────────────────────────────────
    def tabAnimations(self):
        from lcars.base.animation import (
            ScanningBar as AnimScan, CreateSegmentBar as SegmentBar, StarfieldCluster,
            Pulse, DiagnosticGrid, Blink, Typewriter, TextDecode as ScrambledText,
        )
        scroll, col = self.tabPage()

        # ScanningBar
        col.addWidget(self.sec("ScanningBar  |  animated scanning segments", Palette.Buttons[0]))
        for color in [Palette.Buttons[0], Palette.Buttons[2], Palette.Buttons[4]]:
            sb = AnimScan(Color=color, Parent=self)
            sb.setFixedHeight(14)
            col.addWidget(sb)

        # SegmentBar
        col.addWidget(self.sec("SegmentBar  |  pulsed multi-color segments", Palette.Buttons[1]))
        segbar = SegmentBar(Parent=self)
        segbar.setFixedHeight(18)
        col.addWidget(segbar)

        # Pulse
        col.addWidget(self.sec("Pulse  |  pulsing border frame", Palette.Buttons[3]))
        pulse = Pulse(Parent=self, Color=Palette.Buttons[3])
        pulse.setFixedHeight(50)
        col.addWidget(pulse)

        # DiagnosticGrid
        col.addWidget(self.sec("DiagnosticGrid  |  5×5 system diagnostic cells", Palette.Buttons[4]))
        grid = DiagnosticGrid(Parent=self)
        grid.setFixedHeight(100)
        col.addWidget(grid)

        # Typewriter + ScrambledText
        col.addWidget(self.sec("Typewriter  |  character-reveal text", Palette.Buttons[0]))
        tw_Row = HorizontalLayout()
        tw_Row.setSpacing(16)
        for cls, text, color in [
            (Typewriter,    "INITIALIZING LCARS CORE SYSTEMS",    Palette.Panels[2]),
            (ScrambledText, "STARFLEET DATABASE ACCESS GRANTED",  Palette.Buttons[0]),
        ]:
            anim = cls(Text=text, Parent=self, Color=color, FontSize=12, Speed=0.025)
            anim.setFixedHeight(36)
            tw_Row.addWidget(anim, 1)
        col.addLayout(tw_Row)

        # StarfieldCluster
        col.addWidget(self.sec("StarfieldCluster  |  space backgrounds", Palette.Buttons[2]))
        anim_Row = HorizontalLayout()
        anim_Row.setSpacing(16)
        sfc = StarfieldCluster(Parent=self)
        sfc.setFixedSize(280, 160)
        anim_Row.addWidget(sfc)
        anim_Row.addStretch()
        col.addLayout(anim_Row)

        # Blink
        col.addWidget(self.sec("Blink  |  alert flash", Palette.Buttons[3]))
        misc_Row = HorizontalLayout()
        misc_Row.setSpacing(20)
        bl = Blink(Parent=self, Color=Palette.RedAlert[0])
        bl.setFixedSize(80, 40)
        misc_Row.addWidget(bl)
        misc_Row.addStretch()
        col.addLayout(misc_Row)

        col.addStretch()
        return scroll if scroll else self.wrapCol(col)

    # ── ВКЛАДКА 4: ДАНІ ──────────────────────────────────────────────────────
    def tabData(self):
        scroll, col = self.tabPage()

        # DataBlock
        col.addWidget(self.sec("DataBlock  |  status value tiles", Palette.Buttons[0]))
        r1 = HorizontalLayout()
        r1.setSpacing(10)
        for title, val, color in [
            ("STARDATE", "3201.7",    Palette.Buttons[0]),
            ("HULL",     "NOMINAL",   Palette.Buttons[1]),
            ("SHIELDS",  "98%",       Palette.Buttons[2]),
            ("WARP",     "FACTOR 9",  Palette.Buttons[3]),
            ("EPS",      "OPTIMAL",   Palette.Buttons[4]),
            ("CREW",     "1014",      Palette.Buttons[5]),
        ]:
            db = DataBlock(title, val, color, parent=self)
            r1.addWidget(db.widget)
        r1.addStretch()
        col.addLayout(r1)

        # StatBar
        col.addWidget(self.sec("StatBar  |  labeled progress meters", Palette.Buttons[2]))
        sbcol = VerticalLayout()
        sbcol.setSpacing(6)
        for label, color, val in [
            ("WARP DRIVE",    Palette.Buttons[0], 92),
            ("EPS FLOW",      Palette.Buttons[2], 87),
            ("WARP PLASMA",   Palette.Buttons[4], 64),
            ("SHIELD GRID",   Palette.Buttons[1], 98),
            ("SENSOR ARRAY",  Palette.Buttons[3], 71),
            ("TRANSPORTERS",  Palette.Buttons[5], 55),
        ]:
            sb = StatBar(label, color, parent=self)
            sb.setValue(val)
            sbcol.addWidget(sb.widget)
        col.addLayout(sbcol)

        # Label1
        col.addWidget(self.sec("Label1  |  system text labels", Palette.Buttons[3]))
        lRow = HorizontalLayout()
        lRow.setSpacing(12)
        for text, color in [
            ("PRIMARY SYSTEMS ONLINE",  Palette.Panels[2]),
            ("YELLOW ALERT CONDITION",  Palette.YellowAlert[0]),
            ("RED ALERT — BATTLE READY",Palette.RedAlert[0]),
        ]:
            lbl = Label1(Text=text, Parent=self, Color=color)
            lRow.addWidget(lbl.widget)
        lRow.addStretch()
        col.addLayout(lRow)

        col.addStretch()
        return scroll if scroll else self.wrapCol(col)

    # ── ВКЛАДКА 5: СТАТУС / ПАНЕЛІ ───────────────────────────────────────────
    def tabStatus(self):
        scroll, col = self.tabPage()

        # ScanningBar кольори
        col.addWidget(self.sec("ScanningBar — all palette tones", Palette.Buttons[0]))
        for color in Palette.Buttons:
            sb = ScanningBar(color, parent=self)
            sb.widget.setFixedHeight(12)
            col.addWidget(sb.widget)

        # Кольорова палітра
        col.addWidget(self.sec("Palette.Buttons  |  9-color system palette", Palette.Buttons[2]))
        pal_Row = HorizontalLayout()
        pal_Row.setSpacing(4)
        FrameCls = LCARS.Frame
        for color in Palette.Buttons:
            swatch = FrameCls(self)
            swatch.setFixedSize(70, 50)
            swatch.setStyleSheet(f"background: {color}; border-radius: 4px;")
            wrap = VerticalLayout()
            wrap.setSpacing(2)
            wrap.addWidget(swatch)
            wrap.addWidget(self.label(color, color, size=7))
            pal_Row.addLayout(wrap)
        pal_Row.addStretch()
        col.addLayout(pal_Row)

        # Alert палітра
        col.addWidget(self.sec("Alert palettes", Palette.RedAlert[0]))
        alert_Row = HorizontalLayout()
        alert_Row.setSpacing(4)
        for color in Palette.RedAlert + Palette.YellowAlert:
            swatch = FrameCls(self)
            swatch.setFixedSize(70, 40)
            swatch.setStyleSheet(f"background: {color}; border-radius: 4px;")
            alert_Row.addWidget(swatch)
        alert_Row.addStretch()
        col.addLayout(alert_Row)

        # Реєстр — що доступно
        col.addWidget(self.sec("Registry — available Interface keys", Palette.Buttons[1]))
        keys = [
            "Interface.Widget", "Interface.Label", "Interface.Button",
            "Interface.Frame", "Interface.Application", "Interface.Scroll",
            "Interface.Tab", "Interface.Stacked", "Interface.Progress",
            "Interface.Layout.VBox", "Interface.Layout.HBox",
            "Interface.Input", "Interface.Input.Multiline",
            "Interface.Select.List", "Interface.Select.Combo",
            "Base.Timer", "Visual.Painter", "Visual.Color",
            "Visual.Brush", "Visual.Pen", "Visual.Font",
            "Protocol", "Protocol.Align.Center", "Protocol.Pen.NoPen",
        ]
        grid_Row = HorizontalLayout()
        grid_Row.setSpacing(6)
        TextCls = LCARS.Terminal
        if TextCls:
            log = TextCls(self)
            log.setReadOnly(True)
            lines = []
            for key in keys:
                val = LCARS.Get(key)
                status = "✓" if val is not None else "✗  NOT FOUND"
                lines.append(f"  {status}  {key}")
            log.setPlainText("\n".join(lines))
            log.setStyleSheet(
                "LCARSTerminal { background: #050510; color: #66CCFF;"
                " font-family: 'Courier New', monospace; font-size: 9pt;"
                " border: 1px solid #223344; border-radius: 4px; padding: 8px; }"
            )
            log.setFixedHeight(340)
            col.addWidget(log)

        col.addStretch()
        return scroll if scroll else self.wrapCol(col)

    # ── обгортка коли Tab недоступний ────────────────────────────────────────
    def wrapCol(self, col):
        WidgetCls = LCARS.Widget
        w = WidgetCls(self)
        w.setLayout(col)
        return w

    # ── заголовок ────────────────────────────────────────────────────────────
    def header(self):
        Row = HorizontalLayout()
        Row.setContentsMargins(0, 0, 0, 0)
        Row.setSpacing(0)

        self.el1 = LCARSElbow(Parent=self.widget, Color=Palette.Buttons[0], Direction="top-left")
        self.el1.setFixedSize(190, 72)
        Row.addWidget(self.el1.widget)

        self.title_label = LCARS.Label("◤ LCARS FRAMEWORK — COMPONENT SHOWCASE", self)
        self.title_label.setStyleSheet(
            f"color: {Palette.Panels[2]}; font-size: 16pt;"
            " font-family: 'LCARS'; font-weight: bold;"
            " background: transparent; padding: 0 20px;"
        )
        Row.addWidget(self.title_label, 1)

        self.btnMode = LCARSButton(
            text="FULLSCREEN", color=Palette.Buttons[2], shape="pill", parent=self.widget,
        )
        self.btnMode.setFixedSize(165, 44)
        self.btnMode.clicked.connect(self.toggleMode)
        Row.addWidget(self.btnMode.widget)

        self.el2 = LCARSElbow(Parent=self.widget, Color=Palette.Buttons[1], Direction="top-right")
        self.el2.setFixedSize(110, 72)
        Row.addWidget(self.el2.widget)
        return Row

    # ── підвал ───────────────────────────────────────────────────────────────
    def footer(self):
        Row = HorizontalLayout()
        Row.setContentsMargins(0, 0, 0, 0)
        Row.setSpacing(0)

        efl = LCARSElbow(Parent=self.widget, Color=Palette.Buttons[3], Direction="bottom-left")
        efl.setFixedSize(190, 58)
        Row.addWidget(efl.widget)

        status = LCARS.Label(
            "STATUS: READY  │  ALL SYSTEMS OPERATIONAL  │  LCARS v" + getVersion(), self.widget
        )
        status.setStyleSheet(
            f"color: {Palette.Panels[1]}; font-size: 9pt;"
            " font-family: 'LCARS'; background: transparent; padding: 0 20px;"
        )
        Row.addWidget(status, 1)

        btn_close = LCARSButton(text="TERMINATE", color=Palette.RedAlert[0], shape="rect", parent=self.widget)
        btn_close.setFixedSize(160, 40)
        btn_close.clicked.connect(self.close)
        Row.addWidget(btn_close.widget)

        efr = LCARSElbow(Parent=self.widget, Color=Palette.Buttons[4], Direction="bottom-right")
        efr.setFixedSize(110, 58)
        Row.addWidget(efr.widget)
        return Row

    # ── PADD ↔ Fullscreen ────────────────────────────────────────────────────
    def toggleMode(self):
        PLayoutSound("acknowledge")
        if self.fullscreen:
            self.showNormal()
            self.resize(self.PADD_W, self.PADD_H)
            self.btnMode.widget.setText("FULLSCREEN")
            self.fullscreen = False
        else:
            self.showFullScreen()
            self.btnMode.widget.setText("PADD MODE")
            self.fullscreen = True

    def keyPressEvent(self, event):
        Proto = LCARS.Protocol
        if Proto and event and event.key() == Proto.Key.Key_Escape:
            if self.fullscreen:
                self.toggleMode()
            else:
                self.close()
        super().keyPressEvent(event)

    # Використовує вбудований та преміальний eventFilter з батьківського класу LCARSPadd

if __name__ == '__main__':
    app = LCARS.Application(sys.argv)
    padd = ComponentShowcase()
    padd.show()
    sys.exit(app.exec())