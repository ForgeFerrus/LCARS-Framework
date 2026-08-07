# Центр керування системою LCARS
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from lcars.base.component import LCARSButton, LCARSElbow

# Центр керування системою з діагностикою, мережею, живленням та безпекою
class SystemControlCenter(QWidget):
    # Ініціалізація з батьківським вікном, ерою та фракцією
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок з elbow та назвою
        header = QHBoxLayout()
        header.addWidget(LCARSElbow(text="SYSTEM", color="#FFCC33", side="left", direction="down"))
        
        title_text = "SYSTEM CONTROL CENTER"
        if era:
            title_text += f" [{str(era).upper()}]"
            
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 24px; color: orange; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        self.layout.addLayout(header)
        
        # Блок інформації про фракцію
        info = QLabel(f"Faction: {str(faction) if faction else 'Federation Standard'}")
        info.setStyleSheet("color: #99CCFF; font-size: 16px; margin-bottom: 20px;")
        self.layout.addWidget(info)
        
        # Пункти меню: діагностика, мережа, живлення, безпека
        self.layout.addWidget(LCARSButton("DIAGNOSTICS", color="#3366FF"))
        self.layout.addWidget(LCARSButton("NETWORK CONFIG", color="#99CCFF"))
        self.layout.addWidget(LCARSButton("POWER MANAGEMENT", color="#FFCC33"))
        self.layout.addWidget(LCARSButton("SECURITY LOGS", color="#FF3333"))
        
        self.layout.addStretch()

# Псевдонім для сумісності
SystemMenu = SystemControlCenter
