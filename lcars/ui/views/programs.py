"""
SYSTEM MODULE: UI-PROGRAMS-25
AUTHORIZATION: LEVEL 10 ADMIRAL
SECURITY PROTOCOL: EPSILON-9-THETA
DESCRIPTION: LCARS Programs View. Discovers and launches internal and external components.
"""

# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
)
from lcars.ui.base.widgets import (
    LCARSButton, LCARSInput, StatBar, ScanningBar, 
    LCARSElbow, LCARSContour, DataBlock, border_css
)
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.themes.palette import LCARSEra, get_random_button_color
from lcars.system.localization import LOCALIZATION as Language
from lcars.modules.sound_manager import get_sound_manager


class ProgramsView(QWidget):
    """
    КРОК 1: Ініціалізація перегляду програм.
    Цей клас відповідає за відображення доступних утиліт та проектів.
    """
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.init_ui()

    def init_ui(self):
        """Побудова сітки програм та завантаження локальних ресурсів."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        header = QLabel("SYSTEM PROGRAMS & UTILITIES")
        header.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(32, 'normal')}")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(20)

        # КРОК 2: Додавання внутрішніх інженерних програм
        self.add_program(
            "TOTAL COMMANDER", "file_manager", "#FF9900", internal=True
        )
        self.add_program(
            "ISOLINEAR ARCHITECT", "python lcars/engineering/architect.py", "#FFCC00"
        )
        self.add_program("LCARS DESIGNER", "python tools/ui_designer.py", "#FF9900")
        self.add_program(
            "NEURAL CONSOLE", "python lcars/ui/views/console.py", "#3366CC"
        )
        self.add_program(
            "COMPUTER CORE", "python lcars/ui/views/board_computer.py", "#99CCFF"
        )
        self.add_program(
            "MEDIA ARCHIVE", "python lcars/ui/views/media_player.py", "#FF66CC"
        )
        self.add_program(
            "NETWORK BROWSER", "python programs/network_browser.py", "#99CCFF"
        )
        self.add_program(
            "LCARS WEB BROWSER", "python programs/lcars_web_browser.py", "#3366CC"
        )

        # ДОДАНО: Інструмент дизайну детекторів — внутрішній перегляд UI
        self.add_program(
            "DETECTOR DESIGNER", "detector_designer", "#FF66CC", internal=True
        )

        # КРОК 3: Автоматичне виявлення локальних проектів у директорії programs/
        programs_path = Path("programs")
        if programs_path.exists():
            for item in programs_path.iterdir():
                if item.is_dir():
                    self.add_program(
                        f"PROJECT: {item.name}",
                        f"explorer {item.absolute()}",
                        "#00CC00",
                    )

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def add_program(self, name, command, color, internal=False):
        """
        КРОК 4: Метод для створення кнопок програм з відповідним стилем ЛКАРС.
        Підтримує як зовнішні команди, так і внутрішні переходи інтерфейсу.
        """
        btn = QPushButton(name)
        btn.setMinimumSize(200, 100)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border-radius: 5px;
                {get_lcars_font_style(18, 'normal')}
            }}
            QPushButton:hover {{ background-color: white; }}
        """)

        def run_prog():
            get_sound_manager().play("click")
            if internal:
                # КРОК 5: Перемикання на внутрішній віджет, якщо це передбачено
                if command == "file_manager":
                    # Перевага: використовуємо повноцінний Total Commander, якщо є;
                    # інакше — fallback на стару StoragePanel
                    if hasattr(self.parent(), 'show_total_commander'):
                        self.parent().show_total_commander()
                    elif hasattr(self.parent(), 'show_storage'):
                        self.parent().show_storage()
                elif command == "detector_designer" and hasattr(self.parent(), 'show_detector_designer'):
                    # Відкрити вкладку дизайну детекторів у головному вікні
                    self.parent().show_detector_designer()
            else:
                subprocess.Popen(command, shell=True)

        btn.clicked.connect(run_prog)

        count = self.grid.count()
        self.grid.addWidget(btn, count // 4, count % 4)
