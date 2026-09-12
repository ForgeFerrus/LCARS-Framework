import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QFrame
)

# Теми для епох (LCARS палітри)
LCARS_THEMES = {
    "TOS (23 ст.)": {"bg": "black", "primary": "orange", "accent": "blue"},
    "TNG (24 ст.)": {"bg": "black", "primary": "gold", "accent": "purple"},
    "DS9 (24 ст.)": {"bg": "darkgray", "primary": "maroon", "accent": "green"},
    "VOY (24 ст.)": {"bg": "black", "primary": "cyan", "accent": "yellow"},
    "ENT (22 ст.)": {"bg": "lightgray", "primary": "blue", "accent": "white"},
    "25th Century": {"bg": "black", "primary": "violet", "accent": "aqua"},
}

# Теми для фракцій
FACTION_THEMES = {
    "Federation": {"color": "blue", "accent": "orange"},
    "Klingon Empire": {"color": "red", "accent": "silver"},
    "Romulan Star Empire": {"color": "green", "accent": "yellow"},
    "Cardassian Union": {"color": "gold", "accent": "darkred"},
}

class FactionSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Faction Selection Console")
        self.setGeometry(200, 200, 700, 500)

        self.layout = QVBoxLayout()

        # Заголовок
        self.title = QLabel("FACTION SELECTION INTERFACE")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")
        self.layout.addWidget(self.title)

        # Вибір епохи
        self.era_combo = QComboBox()
        self.era_combo.addItems(list(LCARS_THEMES.keys()))
        self.layout.addWidget(self.era_combo)

        # Панель фракцій
        faction_layout = QHBoxLayout()
        for faction in FACTION_THEMES.keys():
            btn = QPushButton(faction)
            btn.setStyleSheet(self.lcars_button_style("gray"))
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            faction_layout.addWidget(btn)
        self.layout.addLayout(faction_layout)

        # Інформаційна панель
        self.info_label = QLabel("Вибір ще не зроблено.")
        self.info_label.setStyleSheet("color: gray; font-style: italic; font-size: 16px;")
        self.layout.addWidget(self.info_label)

        # LCARS панель (декоративна)
        self.lcars_panel = QFrame()
        self.lcars_panel.setStyleSheet("background-color: orange; border-radius: 25px; min-height: 50px;")
        self.layout.addWidget(self.lcars_panel)

        self.setLayout(self.layout)

    def lcars_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: black;
                font-weight: bold;
                border-radius: 20px;
                padding: 15px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: yellow;
            }}
        """

    def select_faction(self, faction):
        era = self.era_combo.currentText()
        faction_theme = FACTION_THEMES[faction]
        era_theme = LCARS_THEMES[era]

        # Застосування стилів
        self.setStyleSheet(f"background-color: {era_theme['bg']};")
        self.title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {era_theme['primary']};")
        self.info_label.setStyleSheet(f"color: {faction_theme['accent']}; font-weight: bold; font-size: 16px;")

        self.info_label.setText(f"Вибрано: {faction} ({era})")
        self.lcars_panel.setStyleSheet(f"background-color: {era_theme['accent']}; border-radius: 25px; min-height: 50px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FactionSelection()
    window.show()
    sys.exit(app.exec())
