"""Project Explorer PyQt view (placeholder).

UKR: Простий переглядач проектів у вигляді списку — поки що заглушка,
UKR: щоб папка `views` не була порожньою. Реальна логіка має підключити
UKР: `ProjectManager` для наповнення списку.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

from lcars.themes.lcars_palette import get_era_palette, LCARSEra, get_lcars_font_style, setup_lcars_font


class ProjectExplorerView(QDialog):
    """Simple dialog that lists projects and returns selection."""

    def __init__(self, parent=None, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__(parent)
        # УКР: реєстрація шрифтів та палітри
        setup_lcars_font()
        pal = get_era_palette(era)

        self.setWindowTitle("Project Explorer")
        self.setFixedSize(420, 360)
        self.setStyleSheet(f"background-color: {pal['background']}; color: {pal['text']};")

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        # приклади проектів — замінити на ProjectManager.discover()
        self.list.addItem("ENX01 — Enterprise")
        self.list.addItem("ENX02 — Research Lab")
        layout.addWidget(self.list)

        row = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet(get_lcars_font_style(12, 'normal'))
        open_btn.clicked.connect(self.accept)
        row.addWidget(open_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        row.addWidget(cancel_btn)

        layout.addLayout(row)

    def selected(self) -> str | None:
        item = self.list.currentItem()
        return item.text() if item else None
