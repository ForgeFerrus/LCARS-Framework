# SYSTEM MODULE: UI-STORAGE-25
# AUTHORIZATION: LEVEL 10 ADMIRAL
# SECURITY PROTOCOL: EPSILON-9-THETA
# DESCRIPTION: Dual-pane Isolinear Storage Manager (Total Commander-style).
#              Provides low-level access to the ship's data core and secondary storage.

import os
import shutil
import platform
from pathlib import Path

from lcars.base.interface import Segment
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSIndicator
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.core.signal import ODN

# КРОК 0: Спеціальний елемент списку для ізолінійних даних.
# Використовує канонічні символи ЛКАРС для директорій та файлів.
class IsolinearNode(LCARS.Interface.Select.ListItem):
    def __init__(self, name, is_dir=False):
        # Визначаємо іконку: порожній квадрат для директорії, заповнений для файлу
        icon = "" if is_dir else "▪"
        super().__init__(f"{icon}  {name.upper()}")
        self.filename = name
        self.is_dir = is_dir

# Дворучний менеджер ізолінійного сховища (нейронний інтерфейс командування)
class StoragePanel(Segment):
    def __init__(self, system=None, DesktopNodeRef=None, ParentNode=None):
        # Ініціалізація базового сегменту та збереження посилань
        super().__init__(Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        self.system = system
        
        self.widget.setStyleSheet("background-color: #000000;")
        
        # Встановлення початкових шляхів для лівої та правої панелей
        self.left_path = Path.cwd()
        self.right_path = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")
        # Перевірка існування вторинного шляху
        if not self.right_path.exists():
            self.right_path = self.left_path

        self.Build()
        self.RefreshAll()

    # Побудова основного інтерфейсу панелі
    def Build(self):
        root = self.Vertical(0, 0, 0, 0, 5)

        # --- ВЕРХНІЙ ЗАГОЛОВОК ---
        header = Segment(Parent=self.widget)
        head_layout = header.Horizontal(0, 0, 0, 0, 2)
        
        header_block = LCARSBar(Type="rect", Color=Palette.Buttons[1], Width=40, Height=60, Parent=header.widget)
        head_layout.addWidget(header_block.widget)
        
        title_block = Segment(Parent=header.widget)
        title_layout = title_block.Horizontal(0, 0, 0, 0, 0)
        title_block.widget.setStyleSheet(f"background: {Palette.Buttons[0]}; border: none;")
        title_block.widget.setMinimumHeight(60)
        
        lbl = LCARSLabel("TOTAL COMMANDER :: ISOLINEAR STORAGE MANAGER", Color="#000000", FontSize=20, Parent=title_block.widget)
        title_layout.addWidget(lbl.widget)
        title_layout.addStretch()
        
        self.lbl_stats = LCARSLabel("READY", Color="#000000", FontSize=16, Parent=title_block.widget)
        title_layout.addWidget(self.lbl_stats.widget)

        self.btn_computer = LCARSButton("COMPUTER", Type="rect", Color=Palette.Buttons[4], Width=120, Height=40, Parent=title_block.widget)
        self.btn_computer.clicked.connect(self.CallComputer)
        title_layout.addWidget(self.btn_computer.widget)
        
        head_layout.addWidget(title_block.widget, 1)
        root.addWidget(header.widget)

        # --- ОБЛАСТЬ ДВОХ ПАНЕЛЕЙ ---
        splitter_widget = LCARS.Interface.Splitter(LCARS.Protocol.OrientationFlag.Horizontal)
        splitter_widget.setHandleWidth(4)
        splitter_widget.setStyleSheet(f"QSplitter::handle {{ background: {Palette.Buttons[1]}; }}")
        
        # Бічні чіпи для індикації статусу
        side_chips = Segment(Parent=self.widget)
        sc_layout = side_chips.Vertical(5, 5, 5, 5, 5)
        side_chips.widget.setMinimumWidth(40)
        for _ in range(12):
            chip = LCARSBar(Type="rect", Color=Palette.Buttons[2], Height=20, Parent=side_chips.widget)
            sc_layout.addWidget(chip.widget)
        sc_layout.addStretch()

        # Створення лівої та правої панелі
        self.left_pane, self.left_list = self.CreatePaneUI("PRIMARY STORAGE", Palette.Buttons[2])
        self.right_pane, self.right_list = self.CreatePaneUI("SECONDARY STORAGE", Palette.Buttons[3])
        
        content_box = Segment(Parent=self.widget)
        cb_layout = content_box.Horizontal(0, 0, 0, 0, 0)
        cb_layout.addWidget(side_chips.widget)
        cb_layout.addWidget(self.left_pane.widget)
        cb_layout.addWidget(self.right_pane.widget)
        
        root.addWidget(content_box.widget, 1)

        # --- НИЖНІЙ РЯДОК ЗАВДАНЬ ---
        footer = Segment(Parent=self.widget)
        foot_layout = footer.Horizontal(0, 0, 0, 0, 5)
        
        self.btm_elbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[0], Parent=footer.widget)
        self.btm_elbow.widget.setMinimumHeight(45)
        foot_layout.addWidget(self.btm_elbow.widget)
        
        # Кнопки операцій з файлами
        ops = [
            ("F3 VIEW", Palette.Buttons[1], self.ViewFile),
            ("F5 COPY", Palette.Buttons[2], self.CopyFile),
            ("F6 MOVE", Palette.Buttons[3], self.MoveFile),
            ("F8 DELETE", Palette.Buttons[0], self.DeleteFile)
        ]
        
        for text, color, slot in ops:
            btn = LCARSButton(text, Type="rect", Color=color, Height=45, Parent=footer.widget)
            btn.clicked.connect(slot)
            foot_layout.addWidget(btn.widget)
            
        status_plate = LCARSLabel("ACCESS LEVEL: NOMINAL", Color="#000000", FontSize=14, Parent=footer.widget)
        status_plate.widget.setStyleSheet(f"background: {Palette.Buttons[1]}; color: black; padding: 0 15px;")
        status_plate.widget.setMinimumHeight(45)
        foot_layout.addWidget(status_plate.widget, 1)
        
        root.addWidget(footer.widget)

    # Виклик системи "Комп'ютер"
    def CallComputer(self):
        ODN.Emit("System.Phase.Computer")

    # Створення інтерфейсу однієї панелі (заголовок + список)
    def CreatePaneUI(self, title, accent_color):
        container = Segment(Parent=self.widget)
        layout = container.Vertical(0, 0, 0, 0, 2)
        
        lbl = LCARSIndicator(Text=f"◥ {title}", Type="rect", Color=accent_color, FontSize=14, Parent=container.widget)
        layout.addWidget(lbl.widget)
        
        lw = LCARS.Interface.Select.List()
        # Налаштування стилю списку файлів
        lw.setStyleSheet(f"""
            QListWidget {{
                background: black; color: {Palette.Neutral[0]};
                border: none; padding: 10px;
                font-family: 'Consolas', 'Courier New'; font-size: 15px;
            }}
            QListWidget::item {{
                padding: 5px; margin-bottom: 2px;
                background: transparent;
            }}
            QListWidget::item:selected {{
                background: {Palette.Buttons[0]}; color: black;
            }}
        """)
        # Підключення подвійного кліку для навігації
        lw.itemDoubleClicked.connect(lambda item: self.Navigate(item, lw))
        layout.addWidget(lw)
        return container, lw

    # Навігація по файловій системі при подвійному кліку
    def Navigate(self, item, list_widget):
        # Визначення поточного шляху залежно від активної панелі
        p = self.left_path if list_widget == self.left_list else self.right_path
        filename = getattr(item, "filename", None)
        if not filename: return
        
        # Формування нового шляху
        if filename == "..":
            new_p = p.parent
        else:
            new_p = p / filename
            
        # Перевірка чи є елемент директорією
        if new_p.is_dir():
            if list_widget == self.left_list: self.left_path = new_p
            else: self.right_path = new_p
            self.RefreshAll()

    # Оновлення обох панелей та статусу
    def RefreshAll(self):
        self.Populate(self.left_list, self.left_path)
        self.Populate(self.right_list, self.right_path)
        self.lbl_stats.SetText("FILES ACCESSIBLE")

    # Заповнення списку файлами з вказаної директорії
    def Populate(self, lw, path):
        lw.clear()
        lw.addItem(IsolinearNode("..", True))
        # Перевірка чи директорія доступна перед ітерацією
        if not path.exists():
            return
        if not path.is_dir():
            return
        for item in sorted(path.iterdir()):
            lw.addItem(IsolinearNode(item.name, item.is_dir()))

    # Перегляд файлу з виділенням у списку
    def ViewFile(self):
        # Визначення активного списку
        focus = self.left_list if self.left_list.hasFocus() else self.right_list
        item = focus.currentItem()
        # Перевірка наявності елементу та чи це не директорія
        if not item: return
        if hasattr(item, "is_dir") and item.is_dir: return
        
        filename = getattr(item, "filename", "")
        path = (self.left_path if focus == self.left_list else self.right_path) / filename
        self.lbl_stats.SetText(f"VIEWING :: {filename.upper()}")

    # Копіювання файлу між панелями
    def CopyFile(self):
        src_lw = self.left_list if self.left_list.hasFocus() else self.right_list
        item = src_lw.currentItem()
        # Перевірка наявності елементу та чи це не батьківська директорія
        if not item: return
        if item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        src = (self.left_path if src_lw == self.left_list else self.right_path) / filename
        # Визначення цільової директорії (протилежна панель)
        dst_dir = self.right_path if src_lw == self.left_list else self.left_path
        dst = dst_dir / filename

        # Перевірка чи джерело існує перед копіюванням
        if not src.exists():
            self.lbl_stats.SetText(f"TRANSFER ERROR :: {filename.upper()}")
            return
        
        # Копіювання директорії або файлу
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        self.RefreshAll()
        self.lbl_stats.SetText(f"TRANSFER COMPLETE :: {filename.upper()}")

    # Переміщення файлу між панелями
    def MoveFile(self):
        src_lw = self.left_list if self.left_list.hasFocus() else self.right_list
        item = src_lw.currentItem()
        if not item: return
        if item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        src = (self.left_path if src_lw == self.left_list else self.right_path) / filename
        dst_dir = self.right_path if src_lw == self.left_list else self.left_path
        dst = dst_dir / filename

        # Перевірка чи джерело існує перед переміщенням
        if not src.exists():
            self.lbl_stats.SetText(f"RELOCATION ERROR :: {filename.upper()}")
            return
        
        shutil.move(str(src), str(dst))
        self.RefreshAll()
        self.lbl_stats.SetText(f"RELOCATION COMPLETE :: {filename.upper()}")

    # Видалення файлу або директорії
    def DeleteFile(self):
        focus = self.left_list if self.left_list.hasFocus() else self.right_list
        item = focus.currentItem()
        if not item: return
        if item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        path = (self.left_path if focus == self.left_list else self.right_path) / filename
        
        # Перевірка чи шлях існує перед видаленням
        if not path.exists():
            self.lbl_stats.SetText(f"PURGE ERROR :: {filename.upper()}")
            return
        
        # Видалення директорії або файлу
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        self.RefreshAll()
        self.lbl_stats.SetText(f"PURGE COMPLETE :: {filename.upper()}")
