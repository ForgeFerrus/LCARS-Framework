from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

class TacticalStation(QWidget):
    """
    Тактична підсистема LCARS. 
    Відповідає за моніторинг захисних полів, дефлекторів та безпеку.
    """
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or {}
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("TACTICAL STATION // SECURITY MATRIX")
        title.setStyleSheet(f"color: {self.theme.get('alert', '#FF3333')}; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(title)

        # Статус щитів
        shield_layout = QHBoxLayout()
        shield_label = QLabel("DEFLECTOR SHIELDS:")
        shield_label.setStyleSheet(f"color: {self.theme.get('text', '#FFFFFF')}; font-size: 20px;")
        self.shield_status = QLabel("ONLINE - 100%")
        self.shield_status.setStyleSheet("color: #33FF33; font-size: 20px; font-weight: bold;")
        shield_layout.addWidget(shield_label)
        shield_layout.addWidget(self.shield_status)
        shield_layout.addStretch()
        self.layout.addLayout(shield_layout)

        # Заглушка тактичної сітки
        matrix_label = QLabel("[ TACTICAL GRID ]")
        matrix_label.setStyleSheet("color: #FF9900; background-color: #222222; padding: 100px; text-align: center;")
        matrix_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(matrix_label, stretch=1)
