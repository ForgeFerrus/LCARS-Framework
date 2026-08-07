# Вузол зорельота LCARS з панелями стану та кнопками керування
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.interface import StatBar, DataBlock


# Компонент вузла зорельота з тактичним оглядом та статусами
class StarshipNode(QWidget):
    # Ініціалізація вузла зорельота з батьківським вікном
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        header = QHBoxLayout()
        self.elbow = LCARSElbow(Direction="top-left", Parent=self)
        header.addWidget(self.elbow.widget)

        title = QLabel("U.S.S. ENTERPRISE - NCC-1701-E")
        title.setStyleSheet("font-size: 24px; color: #FFCC00; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        self.layout.addLayout(header)

        content = QHBoxLayout()

        # Панель статусів (драйв, щити, імпульс)
        status_panel = QVBoxLayout()
        s1 = StatBar(Text="WARP CORE", Value=85, Parent=self)
        status_panel.addWidget(s1.widget)
        s2 = StatBar(Text="SHIELDS", Value=100, Parent=self)
        status_panel.addWidget(s2.widget)
        s3 = StatBar(Text="IMPULSE", Value=42, Parent=self)
        status_panel.addWidget(s3.widget)
        status_panel.addStretch()
        content.addLayout(status_panel)

        # Тактичний огляд
        self.data_block = DataBlock(LabelText="TACTICAL OVERVIEW", Parent=self)
        content.addWidget(self.data_block.widget, 2)

        # Кнопки керування (Бридж, Інженерія, Медичний, Картографія)
        controls = QVBoxLayout()
        for Label in ["BRIDGE", "ENGINEERING", "SICKBAY", "CARTOGRAPHY"]:
            Btn = LCARSButton(Text=Label, Parent=self)
            controls.addWidget(Btn.widget)
        controls.addStretch()
        content.addLayout(controls)

        self.layout.addLayout(content)
        self.layout.addStretch()
