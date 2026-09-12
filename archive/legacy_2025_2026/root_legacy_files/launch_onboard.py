"""
АВТОНОМНИЙ ЗАПУСК БОРТОВОГО КОМП'ЮТЕРА LCARS (MAJEL CORE)
Архітектура TITAN v5.0
ПРОТОКОЛ: ІНТЕРФЕЙС ШТУЧНОГО ІНТЕЛЕКТУ
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PyQt6.QtCore import Qt

# Додавання кореневої папки проекту до шляхів імпорту
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.ui.onboard import OnboardComputerView as OnboardComputer
from lcars.ui.tools.terminal import LCARSTerminal
from lcars.themes.palette import LCARSEra, FactionEra
from lcars.themes.theme import get_lcars_font_style, get_theme, setup_lcars_font
from lcars.core.board_computer import BoardComputer
import plugins

class OnboardStandalone(QMainWindow):
    """Спеціалізоване вікно для взаємодії з ШІ та Системою."""
    
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.era = LCARSEra.LCARS_25TH
        self.theme = get_theme(self.era)
        
        self.setWindowTitle("LCARS :: ONBOARD COMPUTER :: MAJEL CORE")
        
        # Справжній інтерфейс LCARS має бути безрамковий
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black;")
        
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Спліттер для розділення ШІ-термінала та Консолі
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.theme['palette'][1]}; }}")
        
        # 1. Верхня частина: Бортовий комп'ютер (AI)
        # OnboardComputerView тепер імпортовано як OnboardComputerDrawer
        self.onboard = OnboardComputer(era=self.era, parent=self)
        self.onboard.show_drawer() # Активуємо віджет
        splitter.addWidget(self.onboard)
        
        # 2. Нижня частина: Консоль термінала
        # Previously used TerminalDrawer; we now embed canonical terminal directly.
        term_widget = QWidget()
        term_layout = QVBoxLayout(term_widget)
        term_layout.setContentsMargins(0,0,0,0)
        
        self.terminal = LCARSTerminal(parent=self, era=self.era)
        term_layout.addWidget(self.terminal)
        
        splitter.addWidget(term_widget)
        
        layout.addWidget(splitter)
        
        # Гаряча клавіша ESC для виходу
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(a0)

class SystemWrapper:
    """Wrapper to make the BoardComputer accessible as system.board_computer"""
    def __init__(self, computer):
        self.board_computer = computer

def main():
    # Налаштування UTF-8 для символів LCARS
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except: pass

    app = QApplication(sys.argv)
    
    # Ініціалізація системи
    computer = BoardComputer()
    computer.start()
    
    # Реєстрація в плагінах для доступу з віджетів
    system = SystemWrapper(computer)
    plugins.set_system(system)

    # Створення та відображення вікна
    view = OnboardStandalone(system)
    view.showFullScreen()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
