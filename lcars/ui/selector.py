# Інтерфейс вибору фракції LCARS
# Початковий екран для вибору приналежності/теми.
# Перероблено для естетики 25-го Століття.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lcars.core.kernel import CreateApplication, ExistingApplication
from pathlib import Path

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame, QSizePolicy, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont

# Безпечний імпорт компонентів LCARS
if True:
    from lcars.ui.lcars_widgets import LcarsElbow, AnimatedButton
if False:
    # Резервний клас при автономному запуску без налаштування шляху
    class LcarsElbow(QFrame):
        def __init__(self, color, direction, size):
            super().__init__()
            self.setStyleSheet(f"background-color: {color}; border-{direction}-radius: {size[1]//2}px;")
            self.setFixedSize(*size)
            
    class AnimatedButton(QPushButton):
        def __init__(self, text, parent=None):
            super().__init__(text, parent)
            self.setStyleSheet("background-color: #FF9900; color: black; font-weight: bold; border-radius: 15px;")
            self.setFixedSize(200, 60)

# Сучасний екран вибору фракції з високоякісним стилем LCARS
class FactionSelector(QWidget):
    # Сигнал вибору фракції (передає ID фракції)
    factionSelected = pyqtSignal(str)
    
    # Ініціалізація вибору фракції з батьківським вікном
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self.SetupUi()
        
    # Побудова інтерфейсу: бічна панель + основний контент
    def SetupUi(self):
        # Головний макет: горизонтальний (ліва панель + основний контент)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(20, 20, 20, 20)
        master_layout.setSpacing(10)
        
        # --- ЛІВА БІЧНА ПАНЕЛЬ (Характерна LCARS крива) ---
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(5)
        
        # Верхній Elbow (Крива)
        # Колір 25-го Століття: #37A6D1 (Синій) або #FF9900 (Помаранчевий) для Командування
        self.elbow = LcarsElbow("#FF9900", "top-left", (150, 80))
        sidebar_layout.addWidget(self.elbow)
        
        # Вертикальна смуга, що з'єднує знизу
        self.v_bar = QFrame()
        self.v_bar.setFixedWidth(150)
        self.v_bar.setStyleSheet("background-color: #FF9900; border: none;")
        self.v_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sidebar_layout.addWidget(self.v_bar)
        
        # Нижній декоративний блок
        self.bottom_block = QFrame()
        self.bottom_block.setFixedSize(150, 60)
        self.bottom_block.setStyleSheet("background-color: #CC6600; border: none;")
        sidebar_layout.addWidget(self.bottom_block)
        
        master_layout.addLayout(sidebar_layout)
        
        # --- ОСНОВНА ОБЛАСТЬ КОНТЕНТУ ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 0, 0, 0)
        
        # Текст заголовка (вирівняний з elbow)
        header_text = QLabel("SYSTEM ACCESS AUTHORIZATION")
        header_text.setStyleSheet("""
            color: #FF9900;
            font-family: 'Arial', sans-serif;
            font-size: 42px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        """)
        header_text.setFixedHeight(80) # Відповідає висоті elbow
        header_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(header_text)
        
        # Верхня розділювальна лінія
        line = QFrame()
        line.setFixedHeight(5)
        line.setStyleSheet("background-color: #FF9900;")
        content_layout.addWidget(line)
        
        content_layout.addStretch(1)
        
        # Сітка фракцій
        grid = QGridLayout()
        grid.setSpacing(30)
        
        # Визначення фракцій: (Назва, ID, Колір)
        factions = [
            ("UNITED FEDERATION\nOF PLANETS", "federation", "#37A6D1"), # Синій
            ("KLINGON EMPIRE", "klingon", "#CE392B"), # Червоний
            ("ROMULAN STAR EMPIRE", "romulan", "#45D090"), # Зелений
            ("CARDASSIAN UNION", "cardassian", "#EACD53"), # Золотий
        ]
        
        row, col = 0, 0
        for name, fid, color in factions:
            btn = self.CreateFactionButton(name, fid, color)
            grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        content_layout.addLayout(grid)
        content_layout.addStretch(2)
        
        master_layout.addLayout(content_layout)
        
    # Створення великої стилізованої кнопки для вибору фракції
    def CreateFactionButton(self, name, fid, color):
        btn = QPushButton(name)
        btn.setFixedHeight(120)
        # Стиль: прямокутник із заокругленими кінцями (класичний LCARS lozenge)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: black;
                font-family: 'Arial';
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 60px; /* Повністю заокруглені кінці */
                padding: 20px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: white; 
            }}
            QPushButton:pressed {{
                background-color: #FF9900;
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.Connect(lambda: self.factionSelected.emit(fid))
        
        return btn

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = CreateApplication(sys.argv)
    window = FactionSelector()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
