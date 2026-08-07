import sys, os, time, random
import importlib

# 1. СИСТЕМНА ІНІЦІАЛІЗАЦІЯ (TITANIUM COMM v31.1)
from lcars.base.register import registry
import lcars.base.interface as UI
from lcars.base.interface import LCARSProgramPanel

from lcars.base.type import Matrix, Chassis, Directive, Lore, Primitives, Visual
from lcars.base.default import TitanPalette, FontSetup as SetupFont, RandomButtonColor

# Перевірка наявності модуля комунікації через importlib та hasattr
_comm_mod = importlib.import_module('lcars.modules.communication')
if hasattr(_comm_mod, 'communication_system'):
    communication_system = _comm_mod.communication_system
else:
    communication_system = None

# Перевірка наявності модуля анімації сканера через importlib та hasattr
_anim_mod = importlib.import_module('lcars.base.animation')
if hasattr(_anim_mod, 'Scanner'):
    Scanner = _anim_mod.Scanner
else:
    Scanner = None



# ── 4. HQBACKBONE (ALGORITHMIC) ──────────────────────────────

# Клас каркасу зв'язку HQ для малювання фігури
class HQBackbone(Matrix):
    # Конструктор з кольором та батьківським віджетом
    def __init__(self, color, parent=None):
        super().__init__(parent); self.setFixedWidth(260); self.color = color
    # Малювання фігури з'єднання на панелі
    def paintEvent(self, event):
        p = Primitives.Painter()
        if not p.begin(self): return
        p.setRenderHint(Primitives.Painter.Antialiasing)
        # Обчислення розмірів та радіусів кутів
        w, h = self.width(), self.height(); th, r = 55, 100
        p.setBrush(Primitives.Brush(Primitives.Color(self.color))); p.setPen(Primitives.Pen(Primitives.Color(0,0,0,0)))
        # Побудова складного шляху з дугами та лініями
        path = Primitives.Path(); path.moveTo(0, 40); path.lineTo(w-r, 40); path.arcTo(Primitives.RectF(w-r*2, 40, r*2, r*2), 90, -90); path.lineTo(w, h-40-r); path.arcTo(Primitives.RectF(w-r*2, h-40-r*2, r*2, r*2), 0, -90); path.lineTo(0, h-40); path.lineTo(0, h-40-th); path.lineTo(w-r, h-40-th); path.arcTo(Primitives.RectF(w-r-th, h-40-th-(r-th)*2, (r-th)*2, (r-th)*2), 270, 90); path.lineTo(w-th, 40+r); path.arcTo(Primitives.RectF(w-r-th, 40+th, (r-th)*2, (r-th)*2), 0, 90); path.lineTo(0, 40+th); path.closeSubpath()
        p.drawPath(path); p.end()

# ── 5. COMMUNICATION PANEL (V31.1 ALGORITHMIC) ───────────────

# Панель комунікації LCARS для передачі даних підпростору
class CommPanel(LCARSProgramPanel):
    # Конструктор панелі комунікації
    def __init__(self, DesktopNodeRef=None, ParentNode=None, *args, **kwargs):
        self.comm = communication_system
        kwargs.setdefault('accent_color', TitanPalette.Buttons[1])
        super().__init__(title="LCARS SUBSPACE COMMUNICATION HUB", DesktopNodeRef=DesktopNodeRef, ParentNode=ParentNode, *args, **kwargs)


    # Побудова інтерфейсу панелі комунікації
    def BuildUi(self, layout):
        self.setStyleSheet(f"background: {TitanPalette.Background};")

        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        
        # Шапка з назвою системи
        self.cap = UI.Pill(side="none", color=self.accent_color); self.cap.setFixedHeight(65)
        cl = Chassis.Horizontal(self.cap); cl.setContentsMargins(50,0,50,0)
        cl.addWidget(UI.Label("SUBSPACE TRANSCEIVER // COMM HUB v31.1 // MASTER LINK", size=26, color="black"))

        cl.addStretch(); layout.addWidget(self.cap.Widget)
        
        # Основна область з трьома стовпцями
        self.ws = Matrix(); wl = Chassis.Horizontal(self.ws); wl.setSpacing(10)
        
        # Стовпець 1: Режими передачі
        self.p1 = Matrix(); self.p1.setFixedWidth(360)
        p1l = Chassis.Vertical(self.p1); p1l.setSpacing(4); p1l.setContentsMargins(10, 30, 0, 0)
        p1l.addWidget(UI.Label("◤ TRANSMISSION MODES", size=11, color="#666666"))
        
        # Створення кнопок режимів передачі
        modes = ["MESSAGES", "CONTACTS", "SIGNALS", "SCANNER", "ENCRYPTION", "FREQ_SWEEP", "RELAY_SYNC"]
        for txt in modes:
            r = Chassis.Horizontal(); r.setSpacing(3)
            num = Visual.Label(f"{random.randint(1, 99)} ch", size=14, color=TitanPalette.Scientific[0]); num.setFixedWidth(55)
            btn = Visual.Button(txt, side="left", color=RandomButtonColor()); btn.setFixedHeight(34)
            btn.clicked.Connect(lambda t=txt: self.SwitchPanel(t))
            r.addWidget(num); r.addWidget(btn); p1l.addLayout(r)

        
        p1l.addStretch()
        # Блок журналу подій трансивера
        self.log_box = Matrix(); self.log_box.setFixedHeight(220); self.log_box.setStyleSheet(f"border-left: 6px solid {self.accent_color}; background: #051015; padding: 12px;")
        ll = Chassis.Vertical(self.log_box); self.log_txt = UI.Label(">>> TRANSCEIVER: ONLINE.\n>>> SYNC: 99.9%.", size=10, color="#88AAFF")
        ll.addWidget(self.log_txt.Widget); p1l.addWidget(self.log_box.Widget); wl.addWidget(self.p1.Widget)
        
        # Стовпець 2: Каркас з'єднання
        self.flow = HQBackbone(color=self.accent_color); wl.addWidget(self.flow.Widget)
        
        # Центральний хаб: потік даних підпростору
        self.hub = Matrix(); hl = Chassis.Vertical(self.hub); hl.setSpacing(15); hl.setAlignment(Directive.Align.AlignCenter)
        hl.addWidget(UI.Label("SUBSPACE DATA STREAM // ENCRYPTED LINK", size=18, color=self.accent_color))
        
        # Вікно відображення потоку даних
        self.feed = registry.get("Technical.Widget.QTextEdit")()
        self.feed.setFixedSize(850, 360); self.feed.setReadOnly(True)
        self.feed.setStyleSheet(f"background: black; color: {TitanPalette.SKY}; border: 4px solid {TitanPalette.SKY}; border-radius: 40px; padding: 20px; font-family: 'LCARS'; font-size: 15pt;")
        self.feed.setText("◤ SYSTEM: MASTER HUB INITIALIZED\n◤ ISOLINER CORE: ACTIVE\n◤ ODN MATRIX: SYNCHRONIZED")
        hl.addWidget(self.feed.Widget)
        
        # Рядок введення повідомлення
        in_row = Chassis.Horizontal(); in_row.setContentsMargins(40, 0, 40, 0); in_row.setSpacing(10)
        self.entry = registry.get("Technical.Input")()
        self.entry.setPlaceholderText("ENTER SUBSPACE CODE...")
        self.entry.setStyleSheet(f"background: #111111; color: white; border: 2px solid {self.accent_color}; border-radius: 10px; padding: 8px; font-size: 14pt;")
        in_row.addWidget(self.entry, 1)
        # Кнопка передачі повідомлення
        self.tx_btn = UI.Button("TRANSMIT", side="right", color=get_random_button_color()); self.tx_btn.setFixedSize(160, 45); self.tx_btn.clicked.Connect(self.OnSend); in_row.addWidget(self.tx_btn.Widget)
        hl.addLayout(in_row)
        
        hl.addWidget(UI.Label("TITANIUM TRANSCEIVER // FREQ: 4.7GHz", size=24, color=TitanPalette.OCHRE))

        wl.addWidget(self.hub, 1)
        
        # Стовпець 4: Активні ретранслятори
        self.p4 = Matrix(); self.p4.setFixedWidth(320)
        p4l = Chassis.Vertical(self.p4); p4l.setSpacing(8); p4l.setContentsMargins(0, 100, 10, 0)
        p4l.addWidget(UI.Label("◢ ACTIVE RELAYS", size=11, color="#666666"))
        
        # Створення кнопок ретрансляторів
        for name in ["SOL-3", "ALPHA-9", "BETA-2", "EPSILON_LINK", "VULCAN_HUB"]:
            btn = Visual.Button(name, side="right", color=RandomButtonColor()); btn.setFixedHeight(50)
            p4l.addWidget(btn)

        
        p4l.addStretch()
        # Блок стану шифрування
        mb = Matrix(); mb.setFixedHeight(220); mb.setStyleSheet(f"border-right: 6px solid {TitanPalette.Scientific[0]}; background: #051015; padding: 15px;")

        mbl = Chassis.Vertical(mb); mbl.setSpacing(10); mbl.addWidget(UI.Label("◢ ENCRYPTION STATE", size=10, color=self.accent_color))
        self.enc_lbl = UI.Label("ALGORITHM: OMEGA-3\nSTRENGTH: 2048-BIT\nSTATUS: LOCKED", size=10, color=TitanPalette.SKY)
        mbl.addWidget(self.enc_lbl.Widget); p4l.addWidget(mb); wl.addWidget(self.p4.Widget); layout.addWidget(self.ws, 1)
        
        # Нижня панель зі статусом системи
        self.footer = UI.Pill(side="none", color="#111111"); self.footer.setFixedHeight(45)
        fl = Chassis.Horizontal(self.footer); fl.setContentsMargins(40,0,40,0)
        self.footer.addWidget(UI.Label("COMM SYS OPERATIONAL // LINK STABLE", size=11, color="#555555"))
        
        # Ініціалізація анімації сканера Titanium
        self.ScanNode = UI.Label("◢", size=24, color=self.accent_color)
        self.ScannerAnim = Scanner(self.ScanNode)
        self.ScannerAnim.start()
        hl.addWidget(self.ScanNode.Widget)

        fl.addStretch(); btn_p = Visual.Button("PWR", side="both", color=TitanPalette.Alert[1]); btn_p.setFixedSize(120, 36); btn_p.clicked.Connect(sys.exit); fl.addWidget(btn_p)


        layout.addWidget(self.footer.Widget)

    # Додавання повідомлення до журналу подій
    def Log(self, msg):
        msgs = self.log_txt.text().split("\n")[-7:]; msgs.append(">>> " + str(msg).upper()); self.log_txt.setText("\n".join(msgs))

    # Перемикання режиму панелі комунікації
    def SwitchPanel(self, mode):
        self.Log(f"MODE_SWITCH: {mode}")
        self.feed.setText(f"◤ MODE: {mode.upper()}\n{'-'*50}\n")
        if mode == "MESSAGES":
            # Завантаження останніх повідомлень для відображення
            msgs = self.comm.GetMessages("LOCAL")
            for m in msgs[-10:]: self.feed.append(f"[{time.strftime('%H:%M:%S')}] {m.Sender} ▷ {m.Content}")


    # Обробник натискання кнопки передачі
    def OnSend(self):
        txt = self.entry.text()
        if not txt: return
        self.comm.send_message("LOCAL", "EXTERNAL", txt); self.entry.clear(); self.Log("MESSAGE TRANSMITTED.")

if __name__ == '__main__':
    app = registry.get("Technical.Application")(sys.argv)
    panel = CommPanel(); panel.showFullScreen(); sys.exit(app.exec())
