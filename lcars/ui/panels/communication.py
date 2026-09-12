# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from lcars.base.type import LCARS

QWidget = LCARS.Widget
QVBoxLayout = LCARS.VBoxLayout
QHBoxLayout = LCARS.HBoxLayout
QLabel = LCARS.Label
QFrame = LCARS.Frame
QTextEdit = LCARS.TextEdit
QListWidget = LCARS.ListWidget
QListWidgetItem = LCARS.Interface.Item.List
QLineEdit = LCARS.LineEdit
Qt = LCARS.Protocol.Align
QTimer = LCARS.Timer
import random

# необов'язкові імпорти ядра — дозволяють автономне виконання цього модуля
if True:
    from lcars.core.computer import get_computer
if False: # Removed except block
    get_computer = None

if True:
    from lcars.core.nexus import EventType
if False: # Removed except block
    EventType = None

from lcars.base.types import LCARSButton, LCARSElbow
from lcars.themes.palette import LCARSEra, FactionEra
from lcars.themes.theme import GetLcarsFontStyle, GetTheme

# підсистема зв'язку (COMM)
from lcars.modules.comm import CommSystem, Contact

class CommunicationPanel(QWidget):
    """
    Панель зв'язку для керування підпросторовими частотами та перекладачем.
    КРОК 1: Ініціалізація інтерфейсу зв'язку та мовних матриць.
    """
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        if True:
            self.bc = get_computer() if callable(get_computer) else None
            self.net = getattr(self.bc, 'network_manager', None)
            self.event_bus = getattr(self.bc, 'event_bus', None)
        if False: # Removed except block
            self.bc = None
            self.net = None
            self.event_bus = None
            self.event_bus = None
        # Використовуємо глобальну підсистему COMM (Titanium Standard)
        self.contacts = CommSystem
        self._build_ui()

    def _build_ui(self):
        from lcars.base.types import LCARSElbow, LCARSSegment, LCARSButton
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- TITAN COMMS HEADER ---
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)
        header_lay = QHBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 5, 20, 0)
        header_lay.setSpacing(20)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF', '#CC3333'])
        
        self.header_elbow = LCARSElbow("top-left", palette[1], era=self.era)
        self.header_elbow.widget.setMinimumSize(320, 120)
        header_lay.addWidget(self.header_elbow.widget)
        
        title_lay = QVBoxLayout()
        self.title_lbl = QLabel("SUBSPACE COMMUNICATIONS HUB // LCARS")
        self.title_lbl.setStyleSheet(f"color: {palette[0]}; {get_lcars_font_style(32, 'bold')}; letter-spacing: 2px;")
        title_lay.addWidget(self.title_lbl)
        
        self.freq_lbl = QLabel("CARRIER: 45.2.Ghz // STATUS: MATRIX_ESTABLISHED")
        self.freq_lbl.setStyleSheet(f"color: {palette[2]}; {get_lcars_font_style(18, 'normal')};")
        title_lay.addWidget(self.freq_lbl)
        header_lay.addLayout(title_lay, 1)
        
        header_lay.addWidget(LCARSSegment(palette[3], direction="horizontal", era=self.era).widget, 1)
        layout.addWidget(header_frame)
        
        # --- MAIN ARCHITECTURAL CONTENT ---
        body_hbox = QHBoxLayout()
        body_hbox.setContentsMargins(15, 10, 15, 15)
        body_hbox.setSpacing(25)
        
        # LEFT: FREQUENCY CONTROLS
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        
        channels = ["CMD FREQ", "TAC FREQ", "ENG FREQ", "MED FREQ", "EMERGENCY"]
        for i, ch in enumerate(channels):
            col = palette[i % len(palette)] if ch != "EMERGENCY" else "#CC3333"
            btn = LCARSButton(Text=ch, Color=col, Form=LCARSButton.Soft, CornerRadius=6)
            btn.widget.setFixedSize(200, 45)
            if ch == "EMERGENCY":
                btn.Clicked.Connect(self._hail_all)
            left_col.addWidget(btn.widget)
            
        left_col.addWidget(LCARSSegment(palette[1], direction="vertical", era=self.era).widget, 1)
        
        self.left_elbow_bot = LCARSElbow("bottom-left", palette[0], era=self.era)
        self.left_elbow_bot.widget.setMinimumHeight(120)
        left_col.addWidget(self.left_elbow_bot.widget)
        
        body_hbox.addLayout(left_col)
        
        # CENTER: TRANSMISSION LOGS
        center_col = QVBoxLayout()
        center_col.setSpacing(15)
        
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setStyleSheet("""
            background: #050505; color: #AAEEFF; border: 1px solid #111;
            padding: 15px; font-family: 'Consolas', monospace;
            border-radius: 4px;
        """)
        self.logs.setText("◤ SYSTEM: COMMS READY\n◤ AWAITING SIGNAL...\n")
        center_col.addWidget(self.logs, 1)
        
        entry_lay = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("◤ ENTER TRANSMISSION...")
        self.entry.setStyleSheet("background:#111; color:white; border: 1px solid #333; height: 35px; padding-left: 10px;")
        entry_lay.addWidget(self.entry, 1)
        
        btn_send = LCARSButton(Text="TRANSMIT", Color=palette[2], Form=LCARSButton.Soft, CornerRadius=6)
        btn_send.widget.setFixedSize(120, 35)
        btn_send.Clicked.Connect(lambda: (self.logs.append(f"◤ TX: {self.entry.text()}"), self.entry.clear()))
        entry_lay.addWidget(btn_send.widget)
        center_col.addLayout(entry_lay)
        
        body_hbox.addLayout(center_col, 2)
        
        # RIGHT: MATRIX STATUS
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        lbl_stat = QLabel("◤ MATRIX STATUS")
        lbl_stat.setStyleSheet(f"color: {palette[2]}; {get_lcars_font_style(16, 'bold')}")
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
            tl.setStyleSheet(f"color: white; {get_lcars_font_style(10, 'normal')}")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {palette[1]}; {get_lcars_font_style(14, 'bold')}")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)
            
        right_panel.addWidget(LCARSSegment(palette[3], era=self.era).widget, 1)
        body_hbox.addLayout(right_panel, 1)
        layout.addLayout(body_hbox, 1)

        # Таймер випадкових повідомлень у журналі
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._add_log)
        self.timer.start(5000)

        # Підписка на мережеві події для відображення активності мережі у журналі зв'язку
        if self.event_bus is not None and EventType is not None:
            self.event_bus.subscribe(EventType.UI_COMPONENT_UPDATED, self._on_event)

    def _add_log(self):
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
        """Відправити вихідний виклик через NetworkManager та записати відповідь."""
        url = "https://fleet.hail/announce"
        if not getattr(self, 'net', None):
            self.logs.append("◤ NETWORK UNAVAILABLE")
            return
        res = self.net.perform_request(url)
        self.logs.append(res)
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

    def _show_contacts(self):
        # dialog for managing contacts
        dlg = QWidget()
        dlg.setWindowTitle("Contacts")
        dlg.setStyleSheet("background: black; color: white;")
        v = QVBoxLayout(dlg)
        self.contact_list = QListWidget()
        self._refresh_contact_list()
        v.addWidget(self.contact_list)
        # buttons
        btn_row = QHBoxLayout()
        add_btn = LCARSButton("ADD", self.theme['palette'][1])
        edit_btn = LCARSButton("EDIT", self.theme['palette'][2])
        del_btn = LCARSButton("DEL", self.theme['palette'][0])
        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        v.addLayout(btn_row)
        add_btn.clicked.connect(lambda: self._contact_editor(dlg))
        edit_btn.clicked.connect(lambda: self._contact_editor(dlg, edit=True))
        del_btn.clicked.connect(self._delete_selected_contact)
        dlg.setLayout(v)
        dlg.resize(400, 500)
        dlg.show()

    def _refresh_contact_list(self):
        self.contact_list.clear()
        for c in self.contacts.Search(""):
            text = f"{c.name} ({c.faction or 'unknown'}) - {c.email or c.phone or ''}"
            item = QListWidgetItem(text)
            # save contact id for later operations
            item.setData(Qt.ItemDataRole.UserRole, c.id)
            self.contact_list.addItem(item)

    def _delete_selected_contact(self):
        item = self.contact_list.currentItem()
        if not item:
            return
        cid = item.data(Qt.ItemDataRole.UserRole)
        if cid:
            self.contacts.DeleteContact(cid)
            self._refresh_contact_list()

    def _contact_editor(self, parent, edit=False):
        dlg = QWidget(parent)
        dlg.setWindowTitle("Edit Contact" if edit else "Add Contact")
        layout = QVBoxLayout(dlg)
        name_edit = QLineEdit(); name_edit.setPlaceholderText("Name")
        faction_edit = QLineEdit(); faction_edit.setPlaceholderText("Faction")
        email_edit = QLineEdit(); email_edit.setPlaceholderText("Email")
        phone_edit = QLineEdit(); phone_edit.setPlaceholderText("Phone")
        addr_edit = QLineEdit(); addr_edit.setPlaceholderText("Address")
        notes_edit = QLineEdit(); notes_edit.setPlaceholderText("Notes")
        for w in (name_edit, faction_edit, email_edit, phone_edit, addr_edit, notes_edit):
            layout.addWidget(w)
        save_btn = LCARSButton("SAVE", self.theme['palette'][1])
        layout.addWidget(save_btn)
        if edit:
            item = self.contact_list.currentItem()
            cid = item.data(Qt.ItemDataRole.UserRole) if item else None
            if cid:
                # load existing contact data
                contacts = self.contacts.Search("")
                # find contact with matching id
                c = next((x for x in contacts if x.id == cid), None)
                if c:
                    name_edit.setText(c.name)
                    faction_edit.setText(c.faction or "")
                    email_edit.setText(c.email or "")
                    phone_edit.setText(c.phone or "")
                    addr_edit.setText(c.address or "")
                    notes_edit.setText(c.notes or "")
            def save_action():
                if cid:
                    self.contacts.UpdateContact(cid,
                                                  name=name_edit.text(),
                                                  faction=faction_edit.text(),
                                                  email=email_edit.text(),
                                                  phone=phone_edit.text(),
                                                  address=addr_edit.text(),
                                                  notes=notes_edit.text())
                dlg.close(); self._refresh_contact_list()
        else:
            def save_action():
                self.contacts.AddContact(Contact(
                    name=name_edit.text(), faction=faction_edit.text(),
                    email=email_edit.text(), phone=phone_edit.text(),
                    address=addr_edit.text(), notes=notes_edit.text()))
                dlg.close(); self._refresh_contact_list()
        save_btn.clicked.connect(save_action)
        dlg.setLayout(layout)
        dlg.resize(300, 400)
        dlg.show()

    def _on_event(self, event):
        if not event or not hasattr(event, 'data'):
            return
        data = event.data or {}
        action = data.get('action')
        if action and action.startswith('network'):
            QTimer.singleShot(0, lambda: self.logs.append(f"◤ МЕРЕЖЕВА ПОДІЯ: {action}"))


if __name__ == '__main__':
    # Автономний демонстраційний запуск CommunicationPanel
    app = LCARS.Application.instance() or LCARS.Application(LCARS.System.Arguments)
    panel = CommunicationPanel()

    if getattr(panel, 'net', None) is None:
        from lcars.modules.network_manager import NetworkManager
        panel.net = NetworkManager(event_bus=None, enabled=True)
        panel.logs.append('◤ МЕРЕЖА (демо): ініціалізовано')

    panel.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    panel.showMaximized()
    LCARS.System.Exit(app.exec())
