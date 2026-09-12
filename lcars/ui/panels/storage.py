"""
SYSTEM MODULE: UI-STORAGE-25
AUTHORIZATION: LEVEL 10 ADMIRAL
SECURITY PROTOCOL: EPSILON-9-THETA
DESCRIPTION: Dual-pane Isolinear Storage Manager (Total Commander-style).
             Provides low-level access to the ship's data core and secondary storage.
"""

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import shutil
import platform
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QListWidget, QListWidgetItem, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QSize

from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

class IsolinearNode(QListWidgetItem):
    """
    КРОК 0: Спеціальний елемент списку для ізолінійних даних.
    Використовує канонічні символи ЛКАРС для директорій та файлів.
    """
    def __init__(self, name, is_dir=False):
        # Using LCARS-canonical symbols for dir, ▪ for file
        icon = "" if is_dir else "▪"
        super().__init__(f"{icon}  {name.upper()}")
        self.filename = name
        self.is_dir = is_dir

class StoragePanel(QWidget):
    """Dual-Pane Isolinear Storage Manager (Neural Command Interface)."""
    def __init__(self, system, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        # КРОК 1: Ініціалізація системних компонентів та шини подій
        self.system = system
        self.event_bus = system.event_bus
        self.era = era
        self.theme = get_theme(era, faction)
        
        # Isolinear Core is mandatory
        self.isolinear = system.nexus.isolinear
        
        self.left_path = Path.cwd()
        self.right_path = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")
        if not self.right_path.exists():
            self.right_path = self.left_path

        self.init_ui()
        self.refresh_all()

    def init_ui(self):
        """Побудова інтерфейсу двопанельного менеджера файлів."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # --- TOP HEADER (ВЕРХНІЙ ЗАГОЛОВОК) ---
        # КРОК 2: Створення заголовка з інформаційною панеллю
        header = QHBoxLayout()
        header.setSpacing(2)
        
        self.header_block = QFrame()
        self.header_block.setMinimumWidth(40)
        self.header_block.setMinimumHeight(60)
        primary_color = self.theme.get('button_colors', ['#FF9900'])[0] if isinstance(self.theme.get('button_colors'), list) else self.theme.get('button_colors', '#FF9900')
        self.header_block.setStyleSheet(f"background: {primary_color}; border-radius: 4px;")
        header.addWidget(self.header_block)
        
        title_block = QFrame()
        title_block.setMinimumHeight(60)
        accent_color = self.theme.get('button_colors', ['#FFAA00'])[1] if isinstance(self.theme.get('button_colors'), list) and len(self.theme.get('button_colors', [])) > 1 else self.theme.get('button_colors', '#FFAA00')
        title_block.setStyleSheet(f"background: {accent_color}; border: none;")
        tl = QHBoxLayout(title_block)
        
        lbl = QLabel("TOTAL COMMANDER :: ISOLINEAR STORAGE MANAGER")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tl.addWidget(lbl)
        tl.addStretch()
        
        self.lbl_stats = QLabel("READY")
        self.lbl_stats.setStyleSheet(f"color: black; {get_lcars_font_style(16, 'normal')}")
        tl.addWidget(self.lbl_stats)

        self.btn_computer = LCARSButton("COMPUTER", self.theme['palette'][4])
        self.btn_computer.setMinimumSize(120, 40)
        self.btn_computer.clicked.connect(self.call_computer)
        tl.addWidget(self.btn_computer)
        
        header.addWidget(title_block, 1)
        self.main_layout.addLayout(header)

        # --- DUAL PANE AREA (ДВОПАНЕЛЬНА ЗОНА) ---
        # КРОК 3: Ініціалізація лівої та правої панелей керування
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.theme['palette'][1]}; }}")
        
        # Isolinear side decoration (декоративні чіпи)
        side_chips = QFrame()
        side_chips.setMinimumWidth(40)
        self.sc_layout = QVBoxLayout(side_chips)
        self.sc_layout.setContentsMargins(5, 5, 5, 5)
        self.sc_layout.setSpacing(5)
        for _ in range(12):
            chip = QFrame()
            chip.setMinimumHeight(20)
            chip.setStyleSheet(f"background: {self.theme['palette'][2]}; border-radius: 2px;")
            self.sc_layout.addWidget(chip)
        self.sc_layout.addStretch()

        self.left_pane, self.left_list = self._create_pane_ui("PRIMARY STORAGE", self.theme['palette'][2])
        self.right_pane, self.right_list = self._create_pane_ui("SECONDARY STORAGE", self.theme['palette'][3])
        
        content_box = QHBoxLayout()
        content_box.addWidget(side_chips)
        content_box.addWidget(self.left_pane)
        content_box.addWidget(self.right_pane)
        
        container_widget = QWidget()
        container_widget.setLayout(content_box)
        self.main_layout.addWidget(container_widget, 1)

        # --- BOTTOM TASK BAR (НИЖНЯ ПАНЕЛЬ ЗАВДАНЬ) ---
        # КРОК 4: Функціональні кнопки операцій (F3, F5, F6, F8)
        footer = QHBoxLayout()
        footer.setSpacing(5)
        
        self.btm_elbow = LCARSElbow("bottom-left", self.theme['palette'][0], era=self.era)
        footer.addWidget(self.btm_elbow)
        
        ops = [
            ("F3 VIEW", self.theme['palette'][1], self.view_file),
            ("F5 COPY", self.theme['palette'][2], self.copy_file),
            ("F6 MOVE", self.theme['palette'][3], self.move_file),
            ("F8 DELETE", self.theme['palette'][0], self.delete_file)
        ]
        
        for text, color, slot in ops:
            btn = LCARSButton(text, color, era=self.era, shape="rectangle")
            btn.setMinimumHeight(45)
            btn.clicked.connect(slot)
            footer.addWidget(btn)
            
        status_plate = QLabel("ACCESS LEVEL: NOMINAL")
        status_plate.setMinimumHeight(45)
        status_plate.setStyleSheet(f"background: {self.theme['palette'][1]}; color: black; padding: 0 15px; {get_lcars_font_style(14, 'normal')}")
        footer.addWidget(status_plate, 1)
        
        self.main_layout.addLayout(footer)

    def call_computer(self):
        """Neural link to Majel agent."""
        if True:
            from lcars.ui.onboard import OnboardComputerView
            import logging
            logger = logging.getLogger(__name__)
            self.majel = OnboardComputerView()
            self.majel.show()
        if False: # Removed except block
            logger.exception("Unhandled exception in %s", __file__)
            # self.lbl_stats.setText(f"COMMS ERROR :: {str(e)[:15].upper()}")

    def _create_pane_ui(self, title, accent_color):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        lbl = QLabel(f"◥ {title}")
        lbl.setMinimumHeight(30)
        lbl.setStyleSheet(f"background: {accent_color}; color: black; padding: 5px 15px; {get_lcars_font_style(14, 'normal')}")
        layout.addWidget(lbl)
        
        lw = QListWidget()
        lw.setStyleSheet(f"""
            QListWidget {{
                background: black; color: {self.theme['secondary']};
                border: none; padding: 10px;
                font-family: 'Consolas', 'Courier New'; font-size: 15px;
            }}
            QListWidget::item {{
                padding: 5px; margin-bottom: 2px;
                background: transparent;
            }}
            QListWidget::item:selected {{
                background: {self.theme['accent']}; color: black;
            }}
        """)
        lw.itemDoubleClicked.connect(lambda item: self._navigate(item, lw))
        layout.addWidget(lw)
        return container, lw

    def _navigate(self, item, list_widget):
        # КРОК 5: Логіка навігації по каталогах
        p = self.left_path if list_widget == self.left_list else self.right_path
        filename = getattr(item, "filename", None)
        if not filename: return
        
        if filename == "..":
            new_p = p.parent
        else:
            new_p = p / filename
            
        if new_p.is_dir():
            if list_widget == self.left_list: self.left_path = new_p
            else: self.right_path = new_p
            self.refresh_all()

    def refresh_all(self):
        self._populate(self.left_list, self.left_path)
        self._populate(self.right_list, self.right_path)
        
        # usage = self.isolinear.get_storage_usage()
        # self.lbl_stats.setText(f"STORAGE LOAD: {usage['percent']}% :: FILES ACCESSIBLE")
        self.lbl_stats.setText("FILES ACCESSIBLE")

    def _populate(self, lw, path):
        # КРОК 6: Заповнення списку файлів та папок
        lw.clear()
        lw.addItem(IsolinearNode("..", True))
        if True:
            for item in sorted(path.iterdir()):
                lw.addItem(IsolinearNode(item.name, item.is_dir()))
        if False: # Removed except block
            pass

    def view_file(self):
        focus = self.left_list if self.left_list.hasFocus() else self.right_list
        item = focus.currentItem()
        if not item or getattr(item, "is_dir", True): return
        
        filename = getattr(item, "filename", "")
        path = (self.left_path if focus == self.left_list else self.right_path) / filename
        self.lbl_stats.setText(f"VIEWING :: {filename.upper()}")
        if self.event_bus:
            self.event_bus.emit("terminal_output", f"◤ PREVIEWING ISOLINEAR DATA: {path.name}")

    def copy_file(self):
        src_lw = self.left_list if self.left_list.hasFocus() else self.right_list
        item = src_lw.currentItem()
        if not item or item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        src = (self.left_path if src_lw == self.left_list else self.right_path) / filename
        dst_dir = self.right_path if src_lw == self.left_list else self.left_path
        dst = dst_dir / filename

        if True:
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            self.refresh_all()
            self.lbl_stats.setText(f"TRANSFER COMPLETE :: {filename.upper()}")
        if False: # Removed except block
            self.lbl_stats.setText(f"TRANSFER ERROR :: {filename.upper()}")

    def move_file(self):
        src_lw = self.left_list if self.left_list.hasFocus() else self.right_list
        item = src_lw.currentItem()
        if not item or item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        src = (self.left_path if src_lw == self.left_list else self.right_path) / filename
        dst_dir = self.right_path if src_lw == self.left_list else self.left_path
        dst = dst_dir / filename

        if True:
            shutil.move(str(src), str(dst))
            self.refresh_all()
            self.lbl_stats.setText(f"RELOCATION COMPLETE :: {filename.upper()}")
        if False: # Removed except block
            self.lbl_stats.setText(f"RELOCATION ERROR :: {filename.upper()}")

    def delete_file(self):
        focus = self.left_list if self.left_list.hasFocus() else self.right_list
        item = focus.currentItem()
        if not item or item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        path = (self.left_path if focus == self.left_list else self.right_path) / filename
        
        if True:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            self.refresh_all()
            self.lbl_stats.setText(f"PURGE COMPLETE :: {filename.upper()}")
        if False: # Removed except block
            self.lbl_stats.setText(f"PURGE ERROR :: {filename.upper()}")

    def show(self):
        super().show()

