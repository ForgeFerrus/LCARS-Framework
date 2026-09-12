import os
import shutil
import platform
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QListWidget, QListWidgetItem, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QSize

from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

class IsolinearNode(QListWidgetItem):
    def __init__(self, name, is_dir=False):
        # Using LCARS-canonical symbols ◢ for dir, ▪ for file
        icon = "◢" if is_dir else "▪"
        super().__init__(f"{icon}  {name.upper()}")
        self.filename = name
        self.is_dir = is_dir

class FileManagerView(QWidget):
    """Dual-Pane Isolinear Storage Manager (Neural Command Interface)."""
    def __init__(self, system, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # --- TOP HEADER ---
        header = QHBoxLayout()
        header.setSpacing(2)
        
        self.elbow = LCARSElbow("top-left", self.theme['accent'], era=self.era)
        header.addWidget(self.elbow)
        
        title_block = QFrame()
        title_block.setFixedHeight(60)
        title_block.setStyleSheet(f"background: {self.theme['accent']}; border: none;")
        tl = QHBoxLayout(title_block)
        
        lbl = QLabel("ISOLINEAR STORAGE MANAGER :: CORE DATA ACCESS")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tl.addWidget(lbl)
        tl.addStretch()
        
        self.lbl_stats = QLabel("READY")
        self.lbl_stats.setStyleSheet(f"color: black; {get_lcars_font_style(16, 'normal')}")
        tl.addWidget(self.lbl_stats)

        self.btn_computer = LCARSButton("COMPUTER", self.theme['palette'][4])
        self.btn_computer.setFixedSize(120, 40)
        self.btn_computer.clicked.connect(self.call_computer)
        tl.addWidget(self.btn_computer)
        
        header.addWidget(title_block, 1)
        self.main_layout.addLayout(header)

        # --- DUAL PANE AREA ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.theme['palette'][1]}; }}")
        
        # Isolinear side decoration
        side_chips = QFrame()
        side_chips.setFixedWidth(40)
        self.sc_layout = QVBoxLayout(side_chips)
        self.sc_layout.setContentsMargins(5, 5, 5, 5)
        self.sc_layout.setSpacing(5)
        for _ in range(12):
            chip = QFrame()
            chip.setFixedHeight(20)
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

        # --- BOTTOM TASK BAR ---
        footer = QHBoxLayout()
        footer.setSpacing(5)
        
        self.btm_elbow = LCARSElbow("bottom-left", self.theme['palette'][0], era=self.era)
        footer.addWidget(self.btm_elbow)
        
        ops = [
            ("F3 VIEW", self.theme['palette'][1], self.view_file),
            ("F5 COPY", self.theme['palette'][2], self.copy_file),
            ("F6 MOVE", self.theme['palette'][3], self.move_file),
            ("F8 DELETE", "#CC0000", self.delete_file)
        ]
        
        for text, color, slot in ops:
            btn = LCARSButton(text, color, era=self.era, shape="rectangle")
            btn.setFixedHeight(45)
            btn.clicked.connect(slot)
            footer.addWidget(btn)
            
        status_plate = QLabel("ACCESS LEVEL: NOMINAL")
        status_plate.setFixedHeight(45)
        status_plate.setStyleSheet(f"background: {self.theme['palette'][1]}; color: black; padding: 0 15px; {get_lcars_font_style(14, 'normal')}")
        footer.addWidget(status_plate, 1)
        
        self.main_layout.addLayout(footer)

    def call_computer(self):
            """Neural link to Majel agent."""
            from lcars.ui.onboard import OnboardComputerView
            self.majel = OnboardComputerView()
            self.majel.show()
            self.lbl_stats.setText(f"COMMS ERROR :: {str(e)[:15].upper()}")

    def _create_pane_ui(self, title, accent_color):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        lbl = QLabel(f"◥ {title}")
        lbl.setFixedHeight(30)
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
                background: #050505;
            }}
            QListWidget::item:selected {{
                background: {self.theme['accent']}; color: black;
            }}
        """)
        lw.itemDoubleClicked.connect(lambda item: self._navigate(item, lw))
        layout.addWidget(lw)
        return container, lw

    def _navigate(self, item, list_widget):
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
        
        usage = self.isolinear.get_storage_usage()
        self.lbl_stats.setText(f"STORAGE LOAD: {usage['percent']}% :: FILES ACCESSIBLE")

    def _populate(self, lw, path):
        lw.clear()
        lw.addItem(IsolinearNode("..", True))
        
        nodes = self.isolinear.list_directory(path)
        if not nodes and not path.exists():
            lw.addItem(IsolinearNode("PATH NOT FOUND", False))
        
        for node in nodes:
            lw.addItem(IsolinearNode(node["name"], node["is_dir"]))

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

        if self.isolinear.copy_node(src, dst):
            self.refresh_all()
            self.lbl_stats.setText(f"TRANSFER COMPLETE :: {filename.upper()}")
        else:
            self.lbl_stats.setText(f"TRANSFER ERROR :: {filename.upper()}")

    def move_file(self):
        src_lw = self.left_list if self.left_list.hasFocus() else self.right_list
        item = src_lw.currentItem()
        if not item or item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        src = (self.left_path if src_lw == self.left_list else self.right_path) / filename
        dst_dir = self.right_path if src_lw == self.left_list else self.left_path
        dst = dst_dir / filename

        if self.isolinear.move_node(src, dst):
            self.refresh_all()
            self.lbl_stats.setText(f"RELOCATION COMPLETE :: {filename.upper()}")
        else:
            self.lbl_stats.setText(f"RELOCATION ERROR :: {filename.upper()}")

    def delete_file(self):
        focus = self.left_list if self.left_list.hasFocus() else self.right_list
        item = focus.currentItem()
        if not item or item.text().endswith(".."): return
        
        filename = getattr(item, "filename", "")
        path = (self.left_path if focus == self.left_list else self.right_path) / filename
        
        if self.isolinear.delete_node(path):
            self.refresh_all()
            self.lbl_stats.setText(f"PURGE COMPLETE :: {filename.upper()}")
        else:
            self.lbl_stats.setText(f"PURGE ERROR :: {filename.upper()}")

    def show(self):
        super().show()

