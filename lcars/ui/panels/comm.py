# ПАНЕЛЬ ЗВ'ЯЗКУ LCARS — КОМАНДНИЙ ЦЕНТР
# МОДУЛЬ СИСТЕМИ: UI-COM-25
# ПРОТОКОЛ: ПІДПРОСТІР / ЛІНГВІСТИЧНА МАТРИЦЯ
# ОПИС: Інтегрований інтерфейс зв'язку та перекладу.

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
import random

from lcars.base.type import LCARS
QWidget = LCARS.Widget
QVBoxLayout = LCARS.VBoxLayout
QHBoxLayout = LCARS.HBoxLayout
QLabel = LCARS.Label
QFrame = LCARS.Frame
QTextEdit = LCARS.TextEdit
QListWidget = LCARS.ListWidget
QLineEdit = LCARS.LineEdit

from lcars.base.types import Visual, Lore, Matrix, Directive, Chassis, Primitives, LCARSButton, LCARSElbow
from lcars.themes.palette import LCARSEra, FactionEra
from lcars.modules.comm import CommSystem, Contact

class CommPanel(QWidget):
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        # Отримання комп'ютера та менеджерів через реєстр або перевірку атрибутів
        self.bc = None
        get_comp = registry.get("Technical.Computer")
        if get_comp: self.bc = get_comp()
        
        self.net = None
        if self.bc: self.net = getattr(self.bc, 'network_manager', None)
        
        self.event_bus = None
        if self.bc: self.event_bus = getattr(self.bc, 'event_bus', None)
        
        # Використовуємо глобальну підсистему COMM (Titanium Standard)
        self.contacts = CommSystem
        self._build_ui()

    def _build_ui(self):
        # Побудова графічного інтерфейсу панелі.
        from lcars.base.types import Visual
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- ШАПКА ПАНЕЛІ ---
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)
        header_lay = QHBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 5, 20, 0)
        header_lay.setSpacing(20)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF', '#FFCC33'])
        
        self.header_elbow = Visual.Elbow("top-left", palette[1])
        self.header_elbow.setMinimumSize(320, 120)
        header_lay.addWidget(self.header_elbow)
        
        title_lay = QVBoxLayout()
        self.title_lbl = QLabel("SUBSPACE COMMUNICATIONS HUB // TITAN")
        self.title_lbl.setStyleSheet(f"color: {palette[0]}; font-size: 32pt; font-family: 'LCARS'; font-weight: bold; letter-spacing: 2px;")
        title_lay.addWidget(self.title_lbl)
        
        self.freq_lbl = QLabel("CARRIER: 45.2.Ghz // STATUS: MATRIX_ESTABLISHED")
        self.freq_lbl.setStyleSheet(f"color: {palette[2]}; font-size: 18pt; font-family: 'LCARS';")
        title_lay.addWidget(self.freq_lbl)
        header_lay.addLayout(title_lay, 1)
        
        header_lay.addWidget(LCARSSegment(palette[3], direction="horizontal", era=self.era), 1)
        layout.addWidget(header_frame)
        
        # --- ОСНОВНИЙ ВМІСТ ---
        body_hbox = QHBoxLayout()
        body_hbox.setContentsMargins(15, 10, 15, 15)
        body_hbox.setSpacing(25)
        
        # ЛІВА КОЛОНКА: КЕРУВАННЯ ЧАСТОТАМИ
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        
        channels = ["CMD FREQ", "TAC FREQ", "ENG FREQ", "MED FREQ", "EMERGENCY"]
        for i, ch in enumerate(channels):
            col = palette[i % len(palette)] if ch != "EMERGENCY" else "#CC0000"
            btn = Visual.Button(ch, col, shape="rect")
            btn.setFixedSize(200, 45)
            if ch == "EMERGENCY":
                btn.clicked.connect(self._hail_all)
            left_col.addWidget(btn)
            
        left_col.addWidget(LCARSSegment(palette[1], direction="vertical", era=self.era), 1)
        
        self.left_elbow_bot = Visual.Elbow("bottom-left", palette[0])
        self.left_elbow_bot.setMinimumHeight(120)
        left_col.addWidget(self.left_elbow_bot)
        
        body_hbox.addLayout(left_col)
        
        # ЦЕНТР: ЖУРНАЛ ПЕРЕДАЧ
        center_col = QVBoxLayout()
        center_col.setSpacing(15)
        
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setStyleSheet("background: #050505; color: #AAEEFF; border: 1px solid #111; padding: 15px; font-family: 'Consolas', monospace; border-radius: 4px;")
        self.logs.setText("◤ SYSTEM: COMMS READY\n◤ AWAITING SIGNAL...\n")
        center_col.addWidget(self.logs, 1)
        
        entry_lay = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("◤ ВВЕДІТЬ ПОВІДОМЛЕННЯ...")
        self.entry.setStyleSheet("background:#111; color:white; border: 1px solid #333; height: 35px; padding-left: 10px;")
        entry_lay.addWidget(self.entry, 1)
        
        btn_send = Visual.Button("TRANSMIT", palette[2], shape="rect")
        btn_send.setFixedSize(120, 35)
        btn_send.clicked.connect(self._transmit_msg)
        entry_lay.addWidget(btn_send)
        center_col.addLayout(entry_lay)
        
        body_hbox.addLayout(center_col, 2)
        
        # ПРАВА КОЛОНКА: СТАТУС МАТРИЦІ
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        lbl_stat = QLabel("◤ МАТРИЦЯ СТАТУС")
        lbl_stat.setStyleSheet(f"color: {palette[2]}; font-size: 16pt; font-family: 'LCARS'; font-weight: bold;")
        right_panel.addWidget(lbl_stat)
        
        stats = [
            ("UNIVERSAL TX", "ENGAGED"),
            ("ENCRYPTION", "LEVEL 12"),
            ("BUFFER", "99.9%"),
            ("LATENCY", "0.002ms")
        ]
        for title, val in stats:
            box = QFrame()
            box.setStyleSheet(f"border-left: 6px solid {palette[1]}; padding-left: 10px; background: rgba(255,153,0,0.05);")
            bl = QVBoxLayout(box)
            tl = QLabel(title)
            tl.setStyleSheet("color: white; font-size: 10pt;")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {palette[1]}; font-size: 14pt; font-weight: bold;")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)
            
        right_panel.addWidget(LCARSSegment(palette[3], era=self.era), 1)
        layout.addLayout(body_hbox, 1)

        # Таймер випадкових логів
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._add_log)
        self.timer.start(5000)

        # Підписка на події
        if self.event_bus:
            ev_type = registry.get("EventType.UI_COMPONENT_UPDATED")
            if ev_type: self.event_bus.subscribe(ev_type, self._on_event)

    def _transmit_msg(self):
        # Відправка введеного тексту в журнал та очищення поля.
        txt = self.entry.text()
        if not txt: return
        self.logs.append(f"◤ TX: {txt}")
        self.entry.clear()
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

    def _add_log(self):
        # Випадкові системні повідомлення.
        msgs = [
            "[SYS] Виявлено підпросторовий маяк у секторі 001",
            "[MSG] Вхідне повідомлення зі Старбази 1",
            "[TX] Вихідна передача на USS Enterprise",
            "[LING] Метричний аналіз: виявлено діалект клінгонів",
            "[SEC] Шар шифрування оновлено до рівня 11"
        ]
        self.logs.append(f"◤ {random.choice(msgs)}")
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

    def _hail_all(self):
        # Відправити загальний виклик.
        if not self.net:
            self.logs.append("◤ МЕРЕЖА НЕДОСТУПНА")
            return
        url = "https://fleet.hail/announce"
        res = self.net.perform_request(url)
        self.logs.append(res)
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

    def _on_event(self, event):
        # Обробка подій інтерфейсу.
        if not event: return
        data = getattr(event, 'data', {})
        if not data: return
        action = data.get('action', '')
        if action.startswith('network'):
            self.logs.append(f"◤ МЕРЕЖЕВА ПОДІЯ: {action}")

if __name__ == '__main__':
    # Автономний запуск для демонстрації.
    AppCls = registry.get("Technical.Application")
    app = AppCls(sys.argv)
    
    # Реєстрація стандартних компонентів для демо
    # Titanium Bridge Migration: from lcars.base.registry import register_standard
    register_standard()
    
    panel = CommunicationPanel()
    panel.show()
    sys.exit(app.exec())
