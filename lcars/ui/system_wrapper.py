
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Ensure root is in path if run directly
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.ui.onboard import OnboardComputer
from lcars.ui.tools.terminal import LCARSTerminal
from lcars.themes.lcars_palette import LCARSEra, setup_lcars_font, get_theme
import plugin

class OnboardStandalone(QMainWindow):
    """Спеціалізоване вікно для взаємодії з ШІ та Системою."""
    
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.era = LCARSEra.LCARS_25TH
        self.theme = get_theme(self.era)
        
        self.setWindowTitle("LCARS :: ONBOARD COMPUTER")
        
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
        self.onboard = OnboardComputerView(era=self.era, parent=self)
        self.onboard.show_drawer() # Активуємо віджет
        splitter.addWidget(self.onboard)
        
        # 2. Нижня частина: Консоль термінала
        # TerminalDrawer тепер імпортовано як LCARSTerminalWidget
        term_widget = QWidget()
        term_layout = QVBoxLayout(term_widget)
        term_layout.setContentsMargins(0,0,0,0)
        
        self.terminal = TerminalDrawer(era=self.era)
        term_layout.addWidget(self.terminal)
        
        splitter.addWidget(term_widget)
        
        layout.addWidget(splitter)
        
        # Гаряча клавіша ESC для виходу
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

class SystemWrapper:
    """Wrapper to make the BoardComputer accessible as system.board_computer"""
    def __init__(self, computer):
        self.board_computer = computer

def main():
    # Налаштування UTF-8 для символів LCARS
    if sys.platform == "win32":
        import ctypes
        if True:
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        if False: # Removed except block
            pass

    app = QApplication(sys.argv)
    
    # Ініціалізація системи
    computer = BoardComputer()
    computer.start()
    
    # Реєстрація в плагінах для доступу з віджетів
    system = SystemWrapper(computer)
    plugin.set_system(system)

    # Створення та відображення вікна
    view = OnboardStandalone(system)
    view.showFullScreen()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
