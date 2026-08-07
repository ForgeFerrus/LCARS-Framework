import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QStackedWidget, QApplication
)
from PyQt6.QtCore import Qt
from lcars.core.kernel import CreateApplication
from lcars.ui.starship_node import StarshipNode
from lcars.ui.headquarters_node import HeadquartersNode
from lcars.base.component import LCARSElbow
from lcars.ui.screen.loading import LCARSLoading
from lcars.core.signal import ODN

class GenericNode(QWidget):
    def __init__(self, name, description):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl = QLabel(f"{name}: {description}")
        lbl.setStyleSheet("font-size: 20px; color: #99CCFF;")
        layout.addWidget(lbl)
        layout.addStretch()

class LCARSNetworkHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Network Hub")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: black; color: white;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # Етап 1: Екран завантаження (System Sequence)
        self.loader = LCARSLoading(Target="hub")
        self.stack.addWidget(self.loader.widget)
        
        # Етап 2: Головне меню (Network Hub)
        self.hub_menu = QWidget()
        self.SetupHubMenu(self.hub_menu)
        self.stack.addWidget(self.hub_menu)
        
        # Слухаємо ODN для перемикання після завершення ініціалізації
        ODN.Channel("System.Phase.Hub").Connect(self.ShowHubMenu)
        
        self.stack.setCurrentWidget(self.loader.widget)

    def SetupHubMenu(self, widget):
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок у стилі LCARS
        header = QHBoxLayout()
        header.addWidget(LCARSElbow(text="NETWORK", color="#CC99FF", side="left", direction="down"))
        
        title = QLabel("LCARS GLOBAL NETWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; color: orange; font-weight: bold; margin: 20px;")
        header.addWidget(title)
        
        header.addStretch()
        layout.addLayout(header)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #3366FF; background: black; }
            QTabBar::tab { background: #222222; color: #FFCC33; padding: 10px; border: 1px solid #3366FF; min-width: 120px; font-size: 14px; }
            QTabBar::tab:selected { background: #3366FF; color: black; font-weight: bold; }
        """)
        layout.addWidget(self.tabs)
        
        # Додавання вузлів
        self.tabs.addTab(StarshipNode(), "Starship")
        self.tabs.addTab(HeadquartersNode(), "Headquarters")
        self.tabs.addTab(GenericNode("Зоряна база", "Обслуговування, ремонт, логістика"), "Starbase")
        self.tabs.addTab(GenericNode("Академія", "Навчання, тренажери, документація"), "Academy")
        self.tabs.addTab(GenericNode("Архів", "База знань, історія, записи"), "Archive")
        self.tabs.addTab(GenericNode("Музей", "Експозиції, ретро-модулі"), "Museum")
        self.tabs.addTab(GenericNode("Лабораторія", "Експерименти, дослідження, sandbox"), "Laboratory")
        self.tabs.addTab(GenericNode("Наукова станція", "Аналіз даних, симуляції"), "Science Station")

    def ShowHubMenu(self, *args):
        self.stack.setCurrentWidget(self.hub_menu)

def main():
    app = CreateApplication(sys.argv)
    hub = LCARSNetworkHub()
    hub.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# Для зворотної сумісності
NetworkHub = LCARSNetworkHub
