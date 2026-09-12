"""
LCARS File Manager Widget
Provides real file system navigation and operations.
"""

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QMenu, QMessageBox, QFrame, QLineEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from lcars.themes.lcars_palette import get_lcars_font_style, get_random_button_color, LCARSEra
from lcars.ui.widgets.common import create_lcars_button

class FileManagerWidget(QWidget):
    def __init__(self, start_path=None, parent=None):
        super().__init__(parent)
        self.current_path = Path(start_path) if start_path else Path.home()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Path Bar
        path_row = QHBoxLayout()
        self.path_lbl = QLabel()
        self.path_lbl.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(18, 'normal')}")
        path_row.addWidget(self.path_lbl, 1)

        up_btn = create_lcars_button("UP DIR", parent=self, width=100, height=40)
        up_btn.setFixedSize(100, 40)
        up_btn.setStyleSheet(self._get_btn_style("#99CCFF"))
        up_btn.clicked.connect(self.go_up)
        path_row.addWidget(up_btn)
        
        layout.addLayout(path_row)

        # File List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: #050505;
                color: #DDD;
                border: 2px solid #555;
                border-radius: 10px;
                {get_lcars_font_style(16, 'normal')}
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #222;
            }}
            QListWidget::item:selected {{
                background-color: #FF9900;
                color: #000;
            }}
        """)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.itemActivated.connect(self.on_item_activated)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)

        # Actions (Quick)
        action_row = QHBoxLayout()
        for label, cb, color in [("HOME", self.go_home, "#CC66FF"), ("DRIVES", self.show_drives, "#FFCC66")]:
            btn = create_lcars_button(label, parent=self, width=120, height=40)
            btn.setFixedSize(120, 40)
            btn.setStyleSheet(self._get_btn_style(color))
            btn.clicked.connect(cb)
            action_row.addWidget(btn)
        action_row.addStretch()
        layout.addLayout(action_row)

    def _get_btn_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 6px;
                {get_lcars_font_style(16, 'bold')}
            }}
            QPushButton:hover {{
                background-color: #FFF;
            }}
        """

    def refresh(self):
        self.path_lbl.setText(str(self.current_path))
        self.list_widget.clear()
        
        if True:
            entries = sorted(self.current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for e in entries:
                prefix = "📁 " if e.is_dir() else "📄 "
                item = QListWidgetItem(f"{prefix}{e.name}")
                item.setData(Qt.ItemDataRole.UserRole, str(e))
                self.list_widget.addItem(item)
        if False: # Removed except block
            err_item = QListWidgetItem(f"ACCESS DENIED: {e}")
            err_item.setForeground(Qt.GlobalColor.red)
            self.list_widget.addItem(err_item)

    def go_up(self):
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self.refresh()

    def go_home(self):
        self.current_path = Path.home()
        self.refresh()

    def show_drives(self):
        # On Windows, list drives
        if sys.platform == "win32":
            from ctypes import windll
            import string
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1: drives.append(f"{letter}:\\")
                bitmask >>= 1
            
            self.list_widget.clear()
            self.path_lbl.setText("SYSTEM DRIVES")
            for d in drives:
                item = QListWidgetItem(f"💾 {d}")
                item.setData(Qt.ItemDataRole.UserRole, d)
                self.list_widget.addItem(item)
            # Hijack current path logic slightly or handle selection differently?
            # For simplicity, on_item_activated handles paths nicely.

    def on_item_activated(self, item):
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str: return
        p = Path(path_str)
        
        if p.is_dir():
            self.current_path = p
            self.refresh()
        else:
            self.launch_file(p)

    def launch_file(self, path):
        if True:
            os.startfile(str(path))
        if False: # Removed except block
            print(f"Failed to launch: {e}")

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item: return
        
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str: return
        path = Path(path_str)

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: #111; color: #FFF; border: 1px solid #555; }}
            QMenu::item {{ padding: 5px 20px; }}
            QMenu::item:selected {{ background-color: #FF9900; color: #000; }}
        """)

        open_act = QAction("Open", self)
        open_act.triggered.connect(lambda: self.on_item_activated(item))
        menu.addAction(open_act)
        
        copy_path = QAction("Copy Path", self)
        copy_path.triggered.connect(lambda: QApplication.clipboard().setText(str(path)))
        menu.addAction(copy_path)

        del_act = QAction("Delete (No Undo)", self)
        del_act.triggered.connect(lambda: self.delete_item(path))
        menu.addAction(del_act)

        menu.exec(self.list_widget.mapToGlobal(pos))

    def delete_item(self, path):
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to permanently delete:\n{path.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if True:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.refresh()
            if False: # Removed except block
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

