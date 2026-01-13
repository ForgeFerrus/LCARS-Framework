"""
LCARS Network Hub (Main Menu)
- Центральний вузол для вибору станції/модуля (корабель, штаб-квартира, база, академія, архів, музей, лабораторія, наукова станція)
- Вибір епохи/режиму (24th, 25th, Klingon, Federation HQ, Starbase, Academy, тощо)
- Підтримка темізації, інтеграції плагінів, сценаріїв запуску
- Кожен вузол відкривається як вкладка або окреме вікно
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
from lcars.ui.starship_node import StarshipNode
from lcars.ui.headquarters_node import HeadquartersNode

class StarbaseNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Starbase (Зоряна база): Логістика, ремонт"))

class AcademyNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Academy (Академія): Навчання, тренажери"))

class ArchiveNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Archive (Архів): База знань, історія"))

class MuseumNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Museum (Музей): Експозиції, демо"))

class LaboratoryNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Laboratory (Лабораторія): Експерименти, sandbox"))

class ScienceStationNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Science Station (Наукова станція): Аналіз, симуляції"))

class LCARSNetworkHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Network Hub - Main Menu")
        self.setMinimumSize(1200, 800)
        layout = QVBoxLayout(self)
        title = QLabel("LCARS GLOBAL NETWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; color: orange; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        # Додаємо вузли як вкладки
        self.tabs.addTab(StarshipNode(), "Корабель")
        self.tabs.addTab(HeadquartersNode(), "Штаб-квартира")
        self.tabs.addTab(StarbaseNode(), "Зоряна база")
        self.tabs.addTab(AcademyNode(), "Академія")
        self.tabs.addTab(ArchiveNode(), "Архів")
        self.tabs.addTab(MuseumNode(), "Музей")
        self.tabs.addTab(LaboratoryNode(), "Лабораторія")
        self.tabs.addTab(ScienceStationNode(), "Наукова станція")
        # TODO: додати вибір епохи, інтеграцію плагінів, сценарії запуску

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hub = LCARSNetworkHub()
    hub.show()
    sys.exit(app.exec())
