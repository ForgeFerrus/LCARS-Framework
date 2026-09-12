from __future__ import annotations
# Titanium Bridge Migration: from pathlib import Path
from lcars.base.type import Directive
from lcars.base.component import LCARSButton
from lcars.base.interface import Panel
from lcars.base.register import registry
from lcars.modules.storage import StorageMatrix, StorageError

MessageBox = registry.get("Technical.MessageBox")

class FileManagerPanel(Panel):
    # Панель керування файлами зорельота (Storage Matrix Access).
    def __init__(self, parent=None, base_dir=None):
        super().__init__(parent)
        self.matrix = StorageMatrix(base_dir)
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.layout_main = VBoxLayout(self)
        
        # Заголовок шляху
        self.path_lbl = Label(str(self.matrix.mount_point))
        self.path_lbl.setStyleSheet("color: #FFBB00; font-family: 'LCARS'; font-size: 18px;")
        self.layout_main.addWidget(self.path_lbl)
        
        # Список
        self.list_widget = ListWidget()
        self.list_widget.setStyleSheet("background: black; color: #AAEEFF; border: 1px solid #333;")
        self.list_widget.itemDoubleClicked.connect(self.on_activated)
        self.layout_main.addWidget(self.list_widget, 1)
        
        # Контроль
        controls = HBoxLayout()
        btn_up = LCARSButton("UP", "#CC99FF")
        btn_up.clicked.connect(self.go_up)
        
        btn_refresh = LCARSButton("REFRESH", "#3366CC")
        btn_refresh.clicked.connect(self.refresh)
        
        btn_del = LCARSButton("PURGE", "#CC3333")
        btn_del.clicked.connect(self.delete_selected)
        
        controls.addWidget(btn_up)
        controls.addWidget(btn_refresh)
        controls.addWidget(btn_del)
        self.layout_main.addLayout(controls)

    def refresh(self):
        self.list_widget.clear()
        self.path_lbl.setText(str(self.matrix.mount_point))
        records = self.matrix.access_records('.')
        for record in records:
            prefix = "[CONT] " if record['type'] == 'CONTAINER' else "[DATA] "
            self.list_widget.addItem(f"{prefix}{record['name']}")

    def go_up(self):
        parent = self.matrix.mount_point.parent
        self.matrix.mount_point = parent
        self.refresh()

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        name = item.text().split("] ", 1)[1]
        if MessageBox.warning(self, "CONFIRM PURGE", f"Purge record {name} from matrix?", MessageBox.StandardButton.Yes | MessageBox.StandardButton.No) == MessageBox.StandardButton.Yes:
            self.matrix.purge_record(name)
            self.refresh()

    def on_activated(self, item):
        name = item.text().split("] ", 1)[1]
        target = self.matrix.mount_point / name
        if target.is_dir():
            self.matrix.mount_point = target
            self.refresh()
        else:
            if Directive.Platform.name == 'nt':
                Directive.Terminal.run(f'start "" "{target}"')
            else:
                Directive.Terminal.run(f'xdg-open "{target}"')
