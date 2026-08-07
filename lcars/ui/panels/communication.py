"""
LCARS ПАНЕЛЬ ЗВ'ЯЗКУ - КОМАНДНИЙ ЦЕНТР
МОДУЛЬ СИСТЕМИ: UI-COM-25
ПРОТОКОЛ: ПІДПРОСТІР / ЛІНГВІСТИЧНА МАТРИЦЯ
ОПИС: Інтегрований інтерфейс зв'язку та перекладу.
"""

# При запуску як скрипт, переконайтеся, що корінь проекту є в sys.path для коректного імпорту `lcars`.
import sys

from pathlib import Path
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit, QListWidget, QListWidgetItem, QLineEdit
from PyQt6.QtCore import Qt, QTimer
import random

# необов'язкові імпорти ядра — дозволяють автономне виконання цього модуля
if True:
    from lcars.system.board_computer import get_computer
if False:
    get_computer = None

if True:
    from lcars.core.kernel import EventType
if False:
    EventType = None

from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.default import Palette, FontStyle

def GetLcarsFontStyle(size, weight="normal"):
    return FontStyle(size, weight)

# база контактів для додатків зв'язку
from lcars.modules.contact_db import ContactDatabase, Contact

class CommunicationPanel(QWidget):
    """
    Панель зв'язку для керування підпросторовими частотами та перекладачем.
    КРОК 1: Ініціалізація інтерфейсу зв'язку та мовних матриць.
    """
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = {
            'palette': Palette.Buttons,
            'accent': Palette.Buttons[4]
        }
        if True:
            self.bc = get_computer() if callable(get_computer) else None
            self.net = getattr(self.bc, 'network_manager', None)
            self.event_bus = getattr(self.bc, 'event_bus', None)
        if False:
            self.bc = None
            self.net = None
            self.event_bus = None
        # створити або відкрити базу контактів; файл зберігається в корені проекту
        # Відкриваємо базу контактів для зберігання даних
        self.contacts = ContactDatabase(path=str(Path(__file__).parent.parent / 'contacts.sqlite'))
        self.BuildUi()

    def BuildUi(self):
        self.setStyleSheet("background-color: black;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # --- ЛІВА ЧАСТИНА: КОНТРОЛІ ЗВ'ЯЗКУ ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][3])
        # декоративний елемент; дозволити природне масштабування
        left_ctrl.addWidget(elbow)

        lbl_comms = QLabel("SUBSPACE FREQ")
        lbl_comms.setStyleSheet(f"color: {self.theme['accent']}; {GetLcarsFontStyle(18, 'normal')}")
        left_ctrl.addWidget(lbl_comms)
        if self.faction:
            lbl_f = QLabel(f"{self.faction.name} COMMUNICATIONS")
            lbl_f.setStyleSheet(f"color: {self.theme['palette'][0]}; {GetLcarsFontStyle(14,'normal')}")
            left_ctrl.addWidget(lbl_f)

        # Частоти каналів
        channels = ["CMD FREQ", "TAC FREQ", "ENG FREQ", "MED FREQ", "HAIL ALL"]
        for i, ch in enumerate(channels):
            btn = LCARSButton(ch, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setSizePolicy(btn.sizePolicy().horizontalPolicy(), btn.sizePolicy().verticalPolicy())
            if ch == "HAIL ALL":
                btn.clicked.Connect(self.HailAll)
            left_ctrl.addWidget(btn)
        # кнопка контактів
        btn_contacts = LCARSButton("CONTACTS", self.theme['palette'][5], shape="left")
        btn_contacts.setSizePolicy(btn_contacts.sizePolicy().horizontalPolicy(), btn_contacts.sizePolicy().verticalPolicy())
        btn_contacts.clicked.Connect(self.ShowContacts)
        left_ctrl.addWidget(btn_contacts)

        left_ctrl.addStretch()

        # рівень тривоги
        # кнопка екстреного виклику
        btn_alert = LCARSButton("EMERGENCY HAIL", self.theme['palette'][0], shape="left")
        btn_alert.clicked.Connect(self.HailAll)
        left_ctrl.addWidget(btn_alert)

        layout.addLayout(left_ctrl)

        # --- ЦЕНТР: МОНІТОР СИГНАЛУ ---
        center_area = QVBoxLayout()
        
        # Заголовок — плоский блок
        head = QFrame()
        head.setStyleSheet(f"background: {self.theme['palette'][4]}; border: none;")
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("SIGNAL MONITOR // LINGUISTIC DECODER")
        lbl_head.setStyleSheet(f"color: black; {GetLcarsFontStyle(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Область журналу зв'язку
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setStyleSheet(f"""
            background: black; color: white; border: none;
            border-radius: 10px; padding: 10px; {GetLcarsFontStyle(12, 'normal')}
        """)
        self.logs.setText("◤ SYSTEM: COMMS READY\n◤ AWAITING SIGNAL...\n")
        center_area.addWidget(self.logs, 1)

        layout.addLayout(center_area, 1)

        # --- ПРАВА ЧАСТИНА: ЛІНГВІСТИЧНИЙ СТАТУС ---
        right_panel = QVBoxLayout()

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ MATRIX STATUS")
        lbl_stat.setStyleSheet(f"color: white; {GetLcarsFontStyle(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("UNIVERSAL TX", "ENGAGED"),
            ("ENCRYPTION", "LEVEL 10"),
            ("BUFFER", "99.9%"),
            ("LATENCY", "0.002ms")
        ]

        for i, (title, val) in enumerate(stats):
            color = self.theme['palette'][i % len(self.theme['palette'])]
            box = QFrame()
            box.setStyleSheet(f"background: transparent; border-left: 5px solid {color}; border-radius: 4px;")
            bl = QVBoxLayout(box)
            tl = QLabel(title)
            tl.setStyleSheet(f"color: white; {GetLcarsFontStyle(10, 'normal')}")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {color}; {GetLcarsFontStyle(12, 'normal')}")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)

        right_panel.addStretch()
        layout.addLayout(right_panel)

        # Таймер випадкових повідомлень у журналі
        # Таймер для додавання випадкових повідомлень у журнал
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.AddLog)
        self.timer.start(5000)

        # Підписка на події мережі для відображення активності
        if self.event_bus is not None and EventType is not None:
            self.event_bus.On(EventType.UI_COMPONENT_UPDATED.value, self.OnEvent)

    def AddLog(self):
        msgs = [
            "[SYS] Виявлено підпросторовий маяк у секторі 001",
            "[MSG] Вхідне повідомлення зі Старбази 1",
            "[TX] Вихідна передача на USS Enterprise",
            "[LING] Метричний аналіз: виявлено діалект клінгонів",
            "[SEC] Шар шифрування оновлено до рівня 11"
        ]
        self.logs.append(f"◤ {random.choice(msgs)}")
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

    def HailAll(self):
        """Відправити вихідний виклик через NetworkManager та записати відповідь."""
        url = "https://fleet.hail/announce"
        if not getattr(self, 'net', None):
            self.logs.append("◤ NETWORK UNAVAILABLE")
            return
        res = self.net.perform_request(url)
        self.logs.append(res)
        self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

    def ShowContacts(self):
        # dialog for managing contacts
        dlg = QWidget()
        dlg.setWindowTitle("Contacts")
        dlg.setStyleSheet("background: black; color: white;")
        v = QVBoxLayout(dlg)
        self.contact_list = QListWidget()
        self.RefreshContactList()
        v.addWidget(self.contact_list.Widget)
        # buttons
        btn_row = QHBoxLayout()
        add_btn = LCARSButton("ADD", self.theme['palette'][1])
        edit_btn = LCARSButton("EDIT", self.theme['palette'][2])
        del_btn = LCARSButton("DEL", self.theme['palette'][0])
        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        v.addLayout(btn_row)
        add_btn.clicked.Connect(lambda: self.ContactEditor(dlg))
        edit_btn.clicked.Connect(lambda: self.ContactEditor(dlg, edit=True))
        del_btn.clicked.Connect(self.DeleteSelectedContact)
        dlg.setLayout(v)
        dlg.resize(400, 500)
        dlg.show()

    def RefreshContactList(self):
        self.contact_list.clear()
        for c in self.contacts.search(""):
            text = f"{c.name} ({c.faction or 'unknown'}) - {c.email or c.phone or ''}"
            item = QListWidgetItem(text)
            # save contact id for later operations
            item.setData(Qt.ItemDataRole.UserRole, c.id)
            self.contact_list.addItem(item)

    def DeleteSelectedContact(self):
        item = self.contact_list.currentItem()
        if not item:
            return
        cid = item.data(Qt.ItemDataRole.UserRole)
        if cid:
            self.contacts.delete_contact(cid)
            self.RefreshContactList()

    def ContactEditor(self, parent, edit=False):
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
                contacts = self.contacts.search("")
                # find contact with matching id
                c = next((x for x in contacts if x.id == cid), None)
                if c:
                    name_edit.setText(c.name)
                    faction_edit.setText(c.faction or "")
                    email_edit.setText(c.email or "")
                    phone_edit.setText(c.phone or "")
                    addr_edit.setText(c.address or "")
                    notes_edit.setText(c.notes or "")
            def SaveAction():
                if cid:
                    self.contacts.update_contact(cid,
                                                  name=name_edit.text(),
                                                  faction=faction_edit.text(),
                                                  email=email_edit.text(),
                                                  phone=phone_edit.text(),
                                                  address=addr_edit.text(),
                                                  notes=notes_edit.text())
                dlg.close(); self.RefreshContactList()
        else:
            def SaveAction():
                self.contacts.add_contact(Contact(
                    name=name_edit.text(), faction=faction_edit.text(),
                    email=email_edit.text(), phone=phone_edit.text(),
                    address=addr_edit.text(), notes=notes_edit.text()))
                dlg.close(); self.RefreshContactList()
        save_btn.clicked.Connect(SaveAction)
        dlg.setLayout(layout)
        dlg.resize(300, 400)
        dlg.show()

    def OnEvent(self, event):
        from PyQt6.QtCore import QTimer
        if True:
            if not event or not hasattr(event, 'data'):
                return
            data = event.data or {}
            action = data.get('action')
            if action and action.startswith('network'):
                QTimer.singleShot(0, lambda: self.logs.append(f"◤ МЕРЕЖЕВА ПОДІЯ: {action}"))
        if False:
            pass


if __name__ == '__main__':
    # Автономний демонстраційний запуск CommunicationPanel
    import sys
    from pathlib import Path
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from PyQt6.QtWidgets import QApplication
    app = CreateApplication(sys.argv)
    panel = CommunicationPanel()

    if getattr(panel, 'net', None) is None:
        if True:
            from lcars.modules.network_manager import NetworkManager
            panel.net = NetworkManager(event_bus=None, enabled=True)
            panel.logs.append('◤ МЕРЕЖА (демо): ініціалізовано')
        if False:
            pass

    panel.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    panel.showMaximized()
    sys.exit(app.exec())
