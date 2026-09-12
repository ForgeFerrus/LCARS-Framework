"""LCARS Start Menu PyQt view.

Невеликий діалог стартового меню реалізований як PyQt6 QDialog.
Цей файл створює візуальне меню в стилі LCARS і використовує існуючі
хелпери палітри та шрифтів з `lcars.themes.lcars_palette`.

Файл призначений як перша візуальна реалізація StartMenu. Він має
бути сумісним зі стандартною палітрою LCARS_25TH та використовувати
get_random_button_color` для кнопок. Не виконуємо QApplication тут.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout
from PyQt6.QtCore import Qt

from lcars.themes.lcars_palette import (
    LCARSEra, get_era_palette, get_random_button_color, get_lcars_font_style, setup_lcars_font
)


class StartMenuView(QDialog):
    """Простий Start Menu діалог.

    API:
      - `exec_and_get()` -> dict: показує діалог і повертає вибір користувача.
    """

    def __init__(self, parent=None, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__(parent)
        # УКР: налаштовуємо шрифти та палітру на рівні діалогу
        setup_lcars_font()
        self.era = era
        self.palette = get_era_palette(self.era)

        self.setWindowTitle("LCARS — Start Menu")
        self.setModal(True)
        self.setFixedSize(480, 420)
        self.setStyleSheet(f"background-color: {self.palette['background']}; color: {self.palette['text']};")

        layout = QVBoxLayout(self)

        title = QLabel("START MENU")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {self.palette['button_colors'][1]}; {get_lcars_font_style(20, 'normal')}")
        layout.addWidget(title)

        # Список проєктів (тимчасово наповнюється прикладами)
        self.projects = QListWidget()
        self.projects.addItem("ENX01 — Enterprise")
        self.projects.addItem("ENX02 — Research Lab")
        self.projects.addItem("NCC-project — Legacy")
        layout.addWidget(self.projects)

        btn_row = QHBoxLayout()
        self.open_btn = QPushButton("Open Project")
        self.open_btn.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; {get_lcars_font_style(12, 'normal')}")
        self.open_btn.clicked.connect(self._on_open)
        btn_row.addWidget(self.open_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(f"background-color: {self.palette['panel_color'] if 'panel_color' in self.palette else '#222'}; {get_lcars_font_style(12, 'normal')}")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        layout.addLayout(btn_row)

        self._selection = None

    def _on_open(self):
        item = self.projects.currentItem()
        if item:
            self._selection = {"project": item.text()}
            self.accept()

    def exec_and_get(self) -> dict | None:
        """Показати діалог і повернути вибір, або None якщо відмінено."""
        res = self.exec()
        if res == QDialog.DialogCode.Accepted:
            return self._selection
        return None
