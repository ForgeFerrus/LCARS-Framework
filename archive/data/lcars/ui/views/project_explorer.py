"""Project Explorer PyQt view (placeholder).
щоб папка `views` не була порожньою. Реальна логіка має підключити `Project Manager` для наповнення списку.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QLabel, QFrame, QWidget, QStackedWidget
from PyQt6.QtCore import Qt

from lcars.themes.palette import get_era_palette, LCARSEra, get_lcars_font_style, setup_lcars_font, get_random_button_color
from lcars.ui.base.widgets import LCARSButton


class ProjectExplorerView(QDialog):
    # ... (код діалогу залишаємо для сумісності, якщо потрібно)
    pass

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QLabel, QFrame, QWidget, QStackedWidget, QApplication
from PyQt6.QtCore import Qt
from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style, setup_lcars_font
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

class ProjectExplorerWidget(QWidget):
    """Full-fidelity LCARS Project Explorer."""
    def __init__(self, project_manager, parent=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with Elbow
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        
        self.elbow = LCARSElbow("top-left", self.theme['accent'], era=self.era, faction=self.faction)
        header_row.addWidget(self.elbow)
        
        header = QLabel("◤ DISCOVERED ARCHIVES")
        header.setStyleSheet(f"color: white; {get_lcars_font_style(28, 'normal')}")
        header_row.addWidget(header)
        header_row.addStretch()
        
        layout.addLayout(header_row)

        # Content split
        content = QHBoxLayout()
        
        self.list = QListWidget()
        self.list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: 2px solid {self.theme['secondary']};
                border-radius: 10px;
                color: #B1957A;
                {get_lcars_font_style(16, 'normal')}
            }}
            QListWidget::item {{
                padding: 15px; border-bottom: 1px solid #222; margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {self.theme['accent']};
                color: black;
                border-radius: 5px;
            }}
        """)
        self.populate_projects()
        content.addWidget(self.list, 2)
        
        # Details Panel
        self.details = QFrame()
        self.details.setStyleSheet(f"background: #080808; border-radius: 10px; border-left: 5px solid {self.theme['accent']};")
        details_layout = QVBoxLayout(self.details)
        self.detail_label = QLabel("SELECT PROJECT\nFOR SPECIFICATIONS")
        self.detail_label.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(14, 'normal')}")
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details_layout.addWidget(self.detail_label)
        
        content.addWidget(self.details, 1)
        layout.addLayout(content)

        # Bottom Buttons
        row = QHBoxLayout()
        row.setSpacing(20)
        
        self.launch_btn = LCARSButton("LAUNCH SEQUENCE", "#FF9900", era=self.era)
        self.launch_btn.clicked.connect(self.launch_project)
        row.addWidget(self.launch_btn)

        back_btn = LCARSButton("RETURN TO MAIN", "#666666", era=self.era)
        back_btn.clicked.connect(self._go_back)
        row.addWidget(back_btn)

        layout.addLayout(row)
        
        self.list.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item):
        name = item.text().split(" - ")[0]
        self.detail_label.setText(f"PROJECT: {name}\nSTATUS: READY\nENCRYPTION: CLASS-IV\nREADY FOR SIMULATION.")

    def populate_projects(self):
        self.list.clear()
        if not self.project_manager:
              self.list.addItem("CORE SYSTEM NOT FOUND")
              return
        projects = self.project_manager.get_all_projects()
        if not projects:
            self.list.addItem("NO GEANT4 PROJECTS DETECTED")
            return
        for project in projects:
            self.list.addItem(f"{project.name.upper()} - {project.path}")

    def launch_project(self):
        item = self.list.currentItem()
        if not item: return
        name = item.text().split(" - ")[0]
        self.detail_label.setText(f"SEQUENCE INITIATED:\nEXECUTING {name}...")

    def _go_back(self):
        parent = self.parent()
        while parent and not isinstance(parent, QStackedWidget):
            parent = parent.parent()
        if parent:
            parent.setCurrentIndex(0)
