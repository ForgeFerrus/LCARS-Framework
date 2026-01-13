"""
LCARS Headquarters Node (Штаб-квартира)
- Заглушка для стратегічного управління, адміністрування, глобальних налаштувань
- Далі: інтеграція реальних модулів HQ, API, профілю користувача
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class HeadquartersNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Штаб-квартира (Headquarters)")
        title.setStyleSheet("font-size: 24px; color: orange; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        layout.addWidget(QLabel("Стратегічне управління, адміністрування, глобальні налаштування."))
        # TODO: додати модулі HQ, профіль користувача, API
        self.setLayout(layout)
